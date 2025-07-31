import asyncio
import json
import logging
import queue
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class MonitoringEvent:
    """Standard monitoring event structure"""
    event_id: str
    timestamp: str
    node_id: str
    node_type: str
    event_type: str  # lifecycle, data, error, metric
    event_name: str
    data: Dict[str, Any]
    correlation_id: str
    workflow_id: str
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class MonitoringConfig:
    """Configuration for monitoring system"""
    backend: 'MonitoringBackend'
    enable_data_snapshots: bool = False
    max_snapshot_size: int = 1024
    sample_rate: float = 1.0  # 1.0 = 100% sampling
    batch_size: int = 100
    flush_interval: float = 1.0  # seconds
    circuit_breaker_threshold: int = 5
    async_workers: int = 4
    buffer_size: int = 10000


class MonitoringBackend(ABC):
    """Abstract base class for monitoring backends"""
    
    @abstractmethod
    async def send_event(self, event: MonitoringEvent):
        """Send a single event"""
        pass
    
    @abstractmethod
    async def send_batch(self, events: List[MonitoringEvent]):
        """Send a batch of events"""
        pass
    
    @abstractmethod
    async def connect(self):
        """Establish connection to backend"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close connection to backend"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if backend is connected"""
        pass


class MockBackend(MonitoringBackend):
    """In-memory mock backend for testing"""
    
    def __init__(self):
        self.events: List[MonitoringEvent] = []
        self._connected = False
        self.send_delay = 0.001  # Simulate network delay
    
    async def connect(self):
        self._connected = True
        logger.info("MockBackend connected")
    
    async def disconnect(self):
        self._connected = False
        logger.info("MockBackend disconnected")
    
    def is_connected(self) -> bool:
        return self._connected
    
    async def send_event(self, event: MonitoringEvent):
        if not self._connected:
            raise ConnectionError("MockBackend not connected")
        
        await asyncio.sleep(self.send_delay)
        self.events.append(event)
        logger.debug(f"MockBackend received event: {event.event_name}")
    
    async def send_batch(self, events: List[MonitoringEvent]):
        if not self._connected:
            raise ConnectionError("MockBackend not connected")
        
        await asyncio.sleep(self.send_delay * len(events))
        self.events.extend(events)
        logger.debug(f"MockBackend received batch of {len(events)} events")
    
    def get_events(self) -> List[MonitoringEvent]:
        """Get all stored events"""
        return self.events.copy()
    
    def clear_events(self):
        """Clear stored events"""
        self.events.clear()


class HTTPBackend(MonitoringBackend):
    """HTTP webhook backend for monitoring events"""
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
        self._session = None
        self._connected = False
    
    async def connect(self):
        import aiohttp
        self._session = aiohttp.ClientSession(headers=self.headers)
        self._connected = True
        logger.info(f"HTTPBackend connected to {self.webhook_url}")
    
    async def disconnect(self):
        if self._session:
            await self._session.close()
        self._connected = False
        logger.info("HTTPBackend disconnected")
    
    def is_connected(self) -> bool:
        return self._connected and self._session is not None
    
    async def send_event(self, event: MonitoringEvent):
        if not self.is_connected():
            raise ConnectionError("HTTPBackend not connected")
        
        try:
            async with self._session.post(self.webhook_url, json=event.to_dict()) as response:
                if response.status >= 400:
                    raise Exception(f"HTTP error {response.status}")
        except Exception as e:
            logger.error(f"Failed to send event via HTTP: {e}")
            raise
    
    async def send_batch(self, events: List[MonitoringEvent]):
        if not self.is_connected():
            raise ConnectionError("HTTPBackend not connected")
        
        batch_data = {
            "events": [event.to_dict() for event in events],
            "batch_size": len(events),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with self._session.post(self.webhook_url, json=batch_data) as response:
                if response.status >= 400:
                    raise Exception(f"HTTP error {response.status}")
        except Exception as e:
            logger.error(f"Failed to send batch via HTTP: {e}")
            raise


class EventDispatcher:
    """
    Async event dispatcher with batching and circuit breaker.
    Runs in a separate thread to avoid blocking main execution.
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.backend = config.backend
        
        # Event queue
        self._event_queue = queue.Queue(maxsize=config.buffer_size)
        self._batch_buffer: List[MonitoringEvent] = []
        
        # Circuit breaker
        self._failure_count = 0
        self._circuit_open = False
        self._last_failure_time = None
        
        # Worker thread
        self._shutdown = False
        self._worker_thread = None
        self._executor = ThreadPoolExecutor(max_workers=config.async_workers)
        
        # Start dispatcher
        self._start()
    
    def _start(self):
        """Start the dispatcher thread"""
        self._worker_thread = threading.Thread(target=self._run_worker, daemon=True)
        self._worker_thread.start()
        logger.info("Event dispatcher started")
    
    def send_event_nowait(self, event: MonitoringEvent):
        """
        Send event without waiting (fire-and-forget).
        Returns immediately, never blocks.
        """
        if self._shutdown or self._circuit_open:
            return
        
        try:
            self._event_queue.put_nowait(event)
        except queue.Full:
            logger.warning("Event queue full, dropping event")
    
    def _run_worker(self):
        """Worker thread main loop"""
        # Create event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._worker_loop())
        except Exception as e:
            logger.error(f"Worker thread error: {e}")
        finally:
            loop.close()
    
    async def _worker_loop(self):
        """Async worker loop"""
        # Connect backend
        try:
            await self.backend.connect()
        except Exception as e:
            logger.error(f"Failed to connect backend: {e}")
            return
        
        last_flush = time.time()
        
        while not self._shutdown:
            try:
                # Check circuit breaker
                if self._circuit_open:
                    await self._check_circuit_breaker()
                    await asyncio.sleep(1)
                    continue
                
                # Get events from queue (non-blocking)
                timeout = min(0.1, self.config.flush_interval)
                try:
                    event = self._event_queue.get(timeout=timeout)
                    self._batch_buffer.append(event)
                except queue.Empty:
                    pass
                
                # Check if we should flush
                should_flush = (
                    len(self._batch_buffer) >= self.config.batch_size or
                    (time.time() - last_flush) >= self.config.flush_interval
                )
                
                if should_flush and self._batch_buffer:
                    await self._flush_batch()
                    last_flush = time.time()
                
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(1)
        
        # Final flush before shutdown
        if self._batch_buffer:
            await self._flush_batch()
        
        # Disconnect backend
        try:
            await self.backend.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting backend: {e}")
    
    async def _flush_batch(self):
        """Flush the current batch to backend"""
        if not self._batch_buffer:
            return
        
        batch = self._batch_buffer.copy()
        self._batch_buffer.clear()
        
        try:
            if len(batch) == 1:
                await self.backend.send_event(batch[0])
            else:
                await self.backend.send_batch(batch)
            
            # Reset failure count on success
            self._failure_count = 0
            
            logger.debug(f"Flushed {len(batch)} events to backend")
            
        except Exception as e:
            logger.error(f"Failed to flush batch: {e}")
            self._handle_failure()
            
            # Try to re-queue events if possible
            for event in batch:
                try:
                    self._event_queue.put_nowait(event)
                except queue.Full:
                    logger.warning("Cannot re-queue event, queue full")
    
    def _handle_failure(self):
        """Handle backend failure"""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self.config.circuit_breaker_threshold:
            self._circuit_open = True
            logger.warning("Circuit breaker opened due to repeated failures")
    
    async def _check_circuit_breaker(self):
        """Check if circuit breaker can be reset"""
        if not self._circuit_open:
            return
        
        # Try to reset after 30 seconds
        if time.time() - self._last_failure_time > 30:
            try:
                # Test connection
                if not self.backend.is_connected():
                    await self.backend.connect()
                
                self._circuit_open = False
                self._failure_count = 0
                logger.info("Circuit breaker reset")
            except Exception as e:
                logger.debug(f"Circuit breaker test failed: {e}")
    
    def shutdown(self):
        """Shutdown the dispatcher"""
        logger.info("Shutting down event dispatcher")
        self._shutdown = True
        
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        
        self._executor.shutdown(wait=True)
        logger.info("Event dispatcher shutdown complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics"""
        return {
            "queue_size": self._event_queue.qsize(),
            "batch_buffer_size": len(self._batch_buffer),
            "circuit_open": self._circuit_open,
            "failure_count": self._failure_count,
            "backend_connected": self.backend.is_connected()
        }