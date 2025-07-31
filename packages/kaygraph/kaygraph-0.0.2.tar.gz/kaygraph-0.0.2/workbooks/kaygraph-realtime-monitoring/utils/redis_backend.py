import asyncio
import json
import logging
from typing import List, Optional, Set
import aioredis
from redis import Redis
from .monitoring import MonitoringBackend, MonitoringEvent

logger = logging.getLogger(__name__)


class RedisBackend(MonitoringBackend):
    """
    Redis Pub/Sub backend for real-time event streaming.
    Supports both sync and async Redis clients.
    """
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6379, 
        db: int = 0,
        password: Optional[str] = None,
        channel_prefix: str = "kaygraph:monitoring:",
        ttl: int = 3600  # 1 hour TTL for stored events
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.channel_prefix = channel_prefix
        self.ttl = ttl
        
        self._redis: Optional[aioredis.Redis] = None
        self._pubsub = None
        self._connected = False
        
        # Channels for different event types
        self.channels = {
            "all": f"{channel_prefix}all",
            "lifecycle": f"{channel_prefix}lifecycle",
            "data": f"{channel_prefix}data",
            "error": f"{channel_prefix}error",
            "metric": f"{channel_prefix}metric"
        }
    
    async def connect(self):
        """Establish connection to Redis"""
        try:
            self._redis = await aioredis.create_redis_pool(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                minsize=5,
                maxsize=10
            )
            self._connected = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            
            # Test connection
            await self._redis.ping()
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()
        self._connected = False
        logger.info("Disconnected from Redis")
    
    def is_connected(self) -> bool:
        return self._connected and self._redis is not None
    
    async def send_event(self, event: MonitoringEvent):
        """Send event to Redis pub/sub channels"""
        if not self.is_connected():
            raise ConnectionError("Redis backend not connected")
        
        try:
            event_json = event.to_json()
            
            # Publish to type-specific channel and all events channel
            await self._redis.publish(self.channels["all"], event_json)
            await self._redis.publish(self.channels[event.event_type], event_json)
            
            # Also store in Redis for persistence (with TTL)
            event_key = f"{self.channel_prefix}event:{event.event_id}"
            await self._redis.setex(event_key, self.ttl, event_json)
            
            # Add to workflow index
            workflow_key = f"{self.channel_prefix}workflow:{event.workflow_id}"
            await self._redis.zadd(
                workflow_key, 
                {event.event_id: float(event.timestamp.replace('T', '').replace(':', '').replace('-', '').split('.')[0])}
            )
            await self._redis.expire(workflow_key, self.ttl)
            
            # Add to node index
            node_key = f"{self.channel_prefix}node:{event.node_id}"
            await self._redis.zadd(
                node_key,
                {event.event_id: float(event.timestamp.replace('T', '').replace(':', '').replace('-', '').split('.')[0])}
            )
            await self._redis.expire(node_key, self.ttl)
            
            # Update metrics
            await self._update_metrics(event)
            
        except Exception as e:
            logger.error(f"Failed to send event to Redis: {e}")
            raise
    
    async def send_batch(self, events: List[MonitoringEvent]):
        """Send batch of events efficiently using pipeline"""
        if not self.is_connected():
            raise ConnectionError("Redis backend not connected")
        
        try:
            # Use pipeline for efficiency
            pipe = self._redis.pipeline()
            
            for event in events:
                event_json = event.to_json()
                
                # Publish commands
                pipe.publish(self.channels["all"], event_json)
                pipe.publish(self.channels[event.event_type], event_json)
                
                # Storage commands
                event_key = f"{self.channel_prefix}event:{event.event_id}"
                pipe.setex(event_key, self.ttl, event_json)
                
                # Index commands
                workflow_key = f"{self.channel_prefix}workflow:{event.workflow_id}"
                timestamp_score = float(event.timestamp.replace('T', '').replace(':', '').replace('-', '').split('.')[0])
                pipe.zadd(workflow_key, {event.event_id: timestamp_score})
                pipe.expire(workflow_key, self.ttl)
                
                node_key = f"{self.channel_prefix}node:{event.node_id}"
                pipe.zadd(node_key, {event.event_id: timestamp_score})
                pipe.expire(node_key, self.ttl)
            
            # Execute pipeline
            await pipe.execute()
            
            # Update metrics for batch
            for event in events:
                await self._update_metrics(event)
            
            logger.debug(f"Sent batch of {len(events)} events to Redis")
            
        except Exception as e:
            logger.error(f"Failed to send batch to Redis: {e}")
            raise
    
    async def _update_metrics(self, event: MonitoringEvent):
        """Update Redis metrics for monitoring"""
        try:
            # Increment counters
            counter_key = f"{self.channel_prefix}metrics:events:{event.event_type}"
            await self._redis.incr(counter_key)
            
            # Track active nodes
            if event.event_name == "node_started":
                active_key = f"{self.channel_prefix}active:nodes"
                await self._redis.sadd(active_key, event.node_id)
            elif event.event_name == "node_completed":
                active_key = f"{self.channel_prefix}active:nodes"
                await self._redis.srem(active_key, event.node_id)
            
            # Track active workflows
            if event.event_name == "node_started" and event.node_id.endswith("_start"):
                active_key = f"{self.channel_prefix}active:workflows"
                await self._redis.sadd(active_key, event.workflow_id)
            elif event.event_name == "node_completed" and event.node_id.endswith("_end"):
                active_key = f"{self.channel_prefix}active:workflows"
                await self._redis.srem(active_key, event.workflow_id)
            
        except Exception as e:
            logger.debug(f"Failed to update metrics: {e}")
    
    async def get_events_by_workflow(self, workflow_id: str, limit: int = 100) -> List[Dict]:
        """Retrieve events for a specific workflow"""
        if not self.is_connected():
            raise ConnectionError("Redis backend not connected")
        
        workflow_key = f"{self.channel_prefix}workflow:{workflow_id}"
        event_ids = await self._redis.zrevrange(workflow_key, 0, limit - 1)
        
        events = []
        for event_id in event_ids:
            event_key = f"{self.channel_prefix}event:{event_id.decode()}"
            event_json = await self._redis.get(event_key)
            if event_json:
                events.append(json.loads(event_json))
        
        return events
    
    async def get_events_by_node(self, node_id: str, limit: int = 100) -> List[Dict]:
        """Retrieve events for a specific node"""
        if not self.is_connected():
            raise ConnectionError("Redis backend not connected")
        
        node_key = f"{self.channel_prefix}node:{node_id}"
        event_ids = await self._redis.zrevrange(node_key, 0, limit - 1)
        
        events = []
        for event_id in event_ids:
            event_key = f"{self.channel_prefix}event:{event_id.decode()}"
            event_json = await self._redis.get(event_key)
            if event_json:
                events.append(json.loads(event_json))
        
        return events
    
    async def get_active_nodes(self) -> Set[str]:
        """Get currently active nodes"""
        if not self.is_connected():
            raise ConnectionError("Redis backend not connected")
        
        active_key = f"{self.channel_prefix}active:nodes"
        nodes = await self._redis.smembers(active_key)
        return {node.decode() for node in nodes}
    
    async def get_active_workflows(self) -> Set[str]:
        """Get currently active workflows"""
        if not self.is_connected():
            raise ConnectionError("Redis backend not connected")
        
        active_key = f"{self.channel_prefix}active:workflows"
        workflows = await self._redis.smembers(active_key)
        return {workflow.decode() for workflow in workflows}
    
    async def get_metrics(self) -> Dict[str, int]:
        """Get event metrics"""
        if not self.is_connected():
            raise ConnectionError("Redis backend not connected")
        
        metrics = {}
        for event_type in ["lifecycle", "data", "error", "metric"]:
            counter_key = f"{self.channel_prefix}metrics:events:{event_type}"
            count = await self._redis.get(counter_key)
            metrics[event_type] = int(count) if count else 0
        
        # Add active counts
        metrics["active_nodes"] = len(await self.get_active_nodes())
        metrics["active_workflows"] = len(await self.get_active_workflows())
        
        return metrics
    
    async def subscribe_to_events(self, event_types: Optional[List[str]] = None):
        """Subscribe to event channels for real-time updates"""
        if not self.is_connected():
            raise ConnectionError("Redis backend not connected")
        
        channels = []
        if event_types:
            for event_type in event_types:
                if event_type in self.channels:
                    channels.append(self.channels[event_type])
        else:
            channels.append(self.channels["all"])
        
        # Create pub/sub and subscribe
        self._pubsub = await self._redis.pubsub()
        await self._pubsub.subscribe(*channels)
        
        logger.info(f"Subscribed to channels: {channels}")
        return self._pubsub
    
    async def get_next_event(self):
        """Get next event from subscription"""
        if not self._pubsub:
            raise RuntimeError("Not subscribed to any channels")
        
        message = await self._pubsub.get_message(ignore_subscribe_messages=True)
        if message and message["type"] == "message":
            return json.loads(message["data"])
        return None


class SyncRedisBackend:
    """
    Synchronous Redis client for non-async contexts.
    Useful for testing and simple scripts.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = Redis(host=host, port=port, db=db, decode_responses=True)
        self.channel_prefix = "kaygraph:monitoring:"
    
    def get_events_by_workflow(self, workflow_id: str, limit: int = 100) -> List[Dict]:
        """Get events for a workflow"""
        workflow_key = f"{self.channel_prefix}workflow:{workflow_id}"
        event_ids = self.redis.zrevrange(workflow_key, 0, limit - 1)
        
        events = []
        for event_id in event_ids:
            event_key = f"{self.channel_prefix}event:{event_id}"
            event_json = self.redis.get(event_key)
            if event_json:
                events.append(json.loads(event_json))
        
        return events
    
    def get_active_nodes(self) -> Set[str]:
        """Get active nodes synchronously"""
        active_key = f"{self.channel_prefix}active:nodes"
        return self.redis.smembers(active_key)
    
    def get_metrics(self) -> Dict[str, int]:
        """Get metrics synchronously"""
        metrics = {}
        for event_type in ["lifecycle", "data", "error", "metric"]:
            counter_key = f"{self.channel_prefix}metrics:events:{event_type}"
            count = self.redis.get(counter_key)
            metrics[event_type] = int(count) if count else 0
        
        metrics["active_nodes"] = len(self.get_active_nodes())
        return metrics