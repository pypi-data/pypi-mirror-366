import asyncio
import json
import time
import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime
from kaygraph import Node, MetricsNode
import logging
from utils.monitoring import MonitoringConfig, EventDispatcher, MonitoringEvent

logging.basicConfig(level=logging.INFO)


class MonitoringNode(Node):
    """
    Base node class with real-time monitoring capabilities.
    Sends events asynchronously without blocking execution.
    """
    
    # Class-level monitoring configuration
    _monitoring_config: Optional[MonitoringConfig] = None
    _event_dispatcher: Optional[EventDispatcher] = None
    _monitoring_enabled: bool = True
    
    @classmethod
    def configure_monitoring(cls, config: MonitoringConfig):
        """Configure monitoring for all MonitoringNode instances"""
        cls._monitoring_config = config
        cls._event_dispatcher = EventDispatcher(config)
        cls._monitoring_enabled = True
        logging.info("Monitoring configured with backend: %s", config.backend.__class__.__name__)
    
    @classmethod
    def disable_monitoring(cls):
        """Disable monitoring globally"""
        cls._monitoring_enabled = False
        if cls._event_dispatcher:
            cls._event_dispatcher.shutdown()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._workflow_id = str(uuid.uuid4())
        self._execution_id = None
        self._start_time = None
        
    def _should_monitor(self) -> bool:
        """Check if monitoring should be performed for this execution"""
        if not self._monitoring_enabled or not self._event_dispatcher:
            return False
        
        # Apply sampling rate
        if self._monitoring_config and self._monitoring_config.sample_rate < 1.0:
            import random
            return random.random() < self._monitoring_config.sample_rate
        
        return True
    
    def _create_event(
        self, 
        event_type: str, 
        event_name: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> MonitoringEvent:
        """Create a monitoring event"""
        return MonitoringEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            node_id=self.node_id,
            node_type=self.__class__.__name__,
            event_type=event_type,
            event_name=event_name,
            data=data or {},
            correlation_id=self._execution_id or "unknown",
            workflow_id=self._workflow_id
        )
    
    def _send_event_async(self, event: MonitoringEvent):
        """Send event asynchronously without blocking"""
        if self._should_monitor() and self._event_dispatcher:
            # Fire and forget - don't await
            self._event_dispatcher.send_event_nowait(event)
    
    def _capture_data_snapshot(self, data: Any, max_size: int = 1024) -> Optional[Dict[str, Any]]:
        """Capture a snapshot of data for monitoring"""
        if not self._monitoring_config or not self._monitoring_config.enable_data_snapshots:
            return None
        
        try:
            # Convert to JSON-serializable format
            if isinstance(data, (dict, list, str, int, float, bool, type(None))):
                serialized = json.dumps(data)
            else:
                serialized = json.dumps(str(data))
            
            # Truncate if too large
            if len(serialized) > max_size:
                return {
                    "truncated": True,
                    "original_size": len(serialized),
                    "preview": serialized[:max_size],
                    "type": type(data).__name__
                }
            
            return {
                "truncated": False,
                "data": data,
                "type": type(data).__name__
            }
        except Exception as e:
            return {
                "error": f"Failed to serialize: {e}",
                "type": type(data).__name__
            }
    
    def before_prep(self, shared: Dict[str, Any]):
        """Hook: Send monitoring event before prep"""
        super().before_prep(shared)
        
        self._execution_id = str(uuid.uuid4())
        self._start_time = time.time()
        
        event = self._create_event(
            event_type="lifecycle",
            event_name="node_started",
            data={
                "state": "preparing",
                "params": self.params,
                "shared_keys": list(shared.keys()) if shared else []
            }
        )
        self._send_event_async(event)
    
    def prep(self, shared: Dict[str, Any]) -> Any:
        """Wrapped prep with monitoring"""
        event = self._create_event(
            event_type="lifecycle",
            event_name="node_preparing",
            data={"state": "prep_started"}
        )
        self._send_event_async(event)
        
        try:
            result = super().prep(shared)
            
            # Capture prep output
            snapshot = self._capture_data_snapshot(result)
            event = self._create_event(
                event_type="data",
                event_name="prep_output",
                data={
                    "state": "prep_completed",
                    "output_snapshot": snapshot
                }
            )
            self._send_event_async(event)
            
            return result
        except Exception as e:
            event = self._create_event(
                event_type="error",
                event_name="prep_failed",
                data={
                    "state": "prep_error",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            self._send_event_async(event)
            raise
    
    def exec(self, prep_res: Any) -> Any:
        """Override in subclass - monitored automatically"""
        raise NotImplementedError("Must implement exec method")
    
    def _exec(self, prep_res: Any) -> Any:
        """Wrapped exec with monitoring"""
        # Capture exec input
        input_snapshot = self._capture_data_snapshot(prep_res)
        event = self._create_event(
            event_type="lifecycle",
            event_name="node_executing", 
            data={
                "state": "exec_started",
                "input_snapshot": input_snapshot
            }
        )
        self._send_event_async(event)
        
        exec_start = time.time()
        
        try:
            result = super()._exec(prep_res)
            
            exec_time = time.time() - exec_start
            
            # Capture exec output
            output_snapshot = self._capture_data_snapshot(result)
            event = self._create_event(
                event_type="data",
                event_name="exec_output",
                data={
                    "state": "exec_completed",
                    "output_snapshot": output_snapshot,
                    "execution_time": exec_time
                }
            )
            self._send_event_async(event)
            
            # Send performance metric
            metric_event = self._create_event(
                event_type="metric",
                event_name="execution_time",
                data={
                    "value": exec_time,
                    "unit": "seconds"
                }
            )
            self._send_event_async(metric_event)
            
            return result
        except Exception as e:
            exec_time = time.time() - exec_start
            
            event = self._create_event(
                event_type="error",
                event_name="exec_failed",
                data={
                    "state": "exec_error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time": exec_time,
                    "retry_count": getattr(self, 'cur_retry', 0)
                }
            )
            self._send_event_async(event)
            raise
    
    def after_exec(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any):
        """Hook: Send monitoring event after exec"""
        super().after_exec(shared, prep_res, exec_res)
        
        event = self._create_event(
            event_type="lifecycle",
            event_name="after_exec",
            data={
                "state": "post_processing",
                "has_result": exec_res is not None
            }
        )
        self._send_event_async(event)
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> Optional[str]:
        """Wrapped post with monitoring"""
        try:
            action = super().post(shared, prep_res, exec_res)
            
            total_time = time.time() - self._start_time if self._start_time else 0
            
            event = self._create_event(
                event_type="lifecycle",
                event_name="node_completed",
                data={
                    "state": "completed",
                    "next_action": action,
                    "total_execution_time": total_time,
                    "shared_keys_modified": list(shared.keys()) if shared else []
                }
            )
            self._send_event_async(event)
            
            return action
        except Exception as e:
            event = self._create_event(
                event_type="error",
                event_name="post_failed",
                data={
                    "state": "post_error",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            self._send_event_async(event)
            raise
    
    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Hook: Enhanced error monitoring"""
        event = self._create_event(
            event_type="error",
            event_name="error_handler_invoked",
            data={
                "error": str(error),
                "error_type": type(error).__name__,
                "will_suppress": False  # Will be updated based on return value
            }
        )
        self._send_event_async(event)
        
        # Call parent error handler
        suppress = super().on_error(shared, error)
        
        if suppress:
            event = self._create_event(
                event_type="lifecycle",
                event_name="error_suppressed",
                data={
                    "error": str(error),
                    "error_type": type(error).__name__
                }
            )
            self._send_event_async(event)
        
        return suppress


class MonitoringMetricsNode(MetricsNode):
    """
    Combines MetricsNode functionality with real-time monitoring.
    Provides both aggregate metrics and real-time event streaming.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inherit monitoring setup from MonitoringNode
        MonitoringNode.__init__(self, *args, **kwargs)
    
    def _run(self, shared: Dict[str, Any]) -> Any:
        """Enhanced run with both metrics and monitoring"""
        # Send start event
        if hasattr(MonitoringNode, '_should_monitor') and MonitoringNode._should_monitor(self):
            MonitoringNode.before_prep(self, shared)
        
        # Run with metrics collection
        result = super()._run(shared)
        
        # Send metrics as monitoring events
        if hasattr(MonitoringNode, '_should_monitor') and MonitoringNode._should_monitor(self):
            stats = self.get_stats()
            event = MonitoringNode._create_event(
                self,
                event_type="metric",
                event_name="node_metrics",
                data={
                    "metrics": stats,
                    "execution_count": len(self.metrics["execution_times"])
                }
            )
            MonitoringNode._send_event_async(self, event)
        
        return result