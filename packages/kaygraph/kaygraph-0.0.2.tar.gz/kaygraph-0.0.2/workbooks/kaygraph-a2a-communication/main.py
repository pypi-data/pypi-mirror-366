#!/usr/bin/env python3
"""
Multi-agent system demonstration using KayGraph A2A communication.
"""

import asyncio
import argparse
import logging
from typing import List, Dict, Any
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import AsyncGraph
from a2a_nodes import (
    MessageBus, AgentRegistry, CoordinatorAgent, SpecialistAgent,
    MonitorAgent, A2AAgent, MessageType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchAgent(SpecialistAgent):
    """Agent specialized in research tasks."""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, registry: AgentRegistry):
        super().__init__(
            agent_id, message_bus, registry,
            specialties=["research", "web_search", "fact_checking"]
        )
    
    async def _handle_task(self, message):
        """Handle research tasks."""
        task_id = message.payload.get("task_id")
        task = message.payload.get("task", {})
        task_type = task.get("type")
        
        if task_type == "research":
            query = task.get("query", "")
            logger.info(f"Researching: {query}")
            
            # Simulate research
            await asyncio.sleep(2)
            
            result = {
                "task_id": task_id,
                "status": "completed",
                "result": {
                    "query": query,
                    "findings": [
                        f"Fact 1 about {query}",
                        f"Fact 2 about {query}",
                        f"Fact 3 about {query}"
                    ],
                    "sources": ["source1.com", "source2.org"],
                    "confidence": 0.85
                },
                "processed_by": self.agent_id
            }
            
            await self.send_message(message.sender, MessageType.RESULT, result)
        else:
            await super()._handle_task(message)


class AnalysisAgent(SpecialistAgent):
    """Agent specialized in data analysis."""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, registry: AgentRegistry):
        super().__init__(
            agent_id, message_bus, registry,
            specialties=["data_analysis", "statistics", "visualization"]
        )
    
    async def _handle_task(self, message):
        """Handle analysis tasks."""
        task_id = message.payload.get("task_id")
        task = message.payload.get("task", {})
        task_type = task.get("type")
        
        if task_type == "data_analysis":
            data = task.get("data", [])
            logger.info(f"Analyzing data with {len(data)} points")
            
            # Simulate analysis
            await asyncio.sleep(1.5)
            
            # Mock analysis results
            if data:
                avg = sum(data) / len(data) if isinstance(data[0], (int, float)) else 0
                result = {
                    "task_id": task_id,
                    "status": "completed",
                    "result": {
                        "data_points": len(data),
                        "average": avg,
                        "min": min(data) if data else 0,
                        "max": max(data) if data else 0,
                        "insights": ["Trend detected", "Anomaly at position 3"]
                    },
                    "processed_by": self.agent_id
                }
            else:
                result = {
                    "task_id": task_id,
                    "status": "completed",
                    "result": {"message": "No data to analyze"},
                    "processed_by": self.agent_id
                }
            
            await self.send_message(message.sender, MessageType.RESULT, result)
        else:
            await super()._handle_task(message)


class WriterAgent(SpecialistAgent):
    """Agent specialized in content generation."""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, registry: AgentRegistry):
        super().__init__(
            agent_id, message_bus, registry,
            specialties=["writing", "summarization", "translation"]
        )
    
    async def _handle_task(self, message):
        """Handle writing tasks."""
        task_id = message.payload.get("task_id")
        task = message.payload.get("task", {})
        task_type = task.get("type")
        
        if task_type == "writing":
            topic = task.get("topic", "")
            style = task.get("style", "professional")
            logger.info(f"Writing about: {topic} in {style} style")
            
            # Simulate writing
            await asyncio.sleep(2.5)
            
            result = {
                "task_id": task_id,
                "status": "completed",
                "result": {
                    "title": f"Analysis of {topic}",
                    "content": f"This is a {style} article about {topic}. "
                              f"It covers key aspects and provides insights. "
                              f"The conclusion emphasizes the importance of {topic}.",
                    "word_count": 42,
                    "reading_time": "1 min"
                },
                "processed_by": self.agent_id
            }
            
            await self.send_message(message.sender, MessageType.RESULT, result)
        else:
            await super()._handle_task(message)


class OrchestratorAgent(CoordinatorAgent):
    """Enhanced coordinator that can handle complex workflows."""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, registry: AgentRegistry):
        super().__init__(agent_id, message_bus, registry)
        self.workflows = {}  # workflow_id -> workflow_state
    
    async def handle_message(self, message: Message):
        """Handle orchestration messages."""
        if message.payload.get("type") == "complex_workflow":
            await self._handle_complex_workflow(message)
        else:
            await super().handle_message(message)
    
    async def _handle_complex_workflow(self, message: Message):
        """Handle multi-step workflow."""
        workflow_id = str(uuid.uuid4())
        workflow_type = message.payload.get("workflow_type")
        
        logger.info(f"Starting complex workflow {workflow_id}: {workflow_type}")
        
        if workflow_type == "research_and_report":
            # Step 1: Research
            research_response = await self.request({
                "type": "research",
                "query": message.payload.get("topic", "AI trends")
            }, timeout=10)
            
            if not research_response:
                await self.reply(message, {
                    "status": "error",
                    "error": "Research failed"
                })
                return
            
            # Step 2: Analyze findings
            findings = research_response.payload.get("result", {}).get("findings", [])
            analysis_response = await self.request({
                "type": "data_analysis",
                "data": [len(f) for f in findings]  # Analyze finding lengths
            }, timeout=10)
            
            # Step 3: Write report
            writer_response = await self.request({
                "type": "writing",
                "topic": message.payload.get("topic", "AI trends"),
                "style": "analytical"
            }, timeout=10)
            
            # Combine results
            final_result = {
                "workflow_id": workflow_id,
                "status": "completed",
                "research": research_response.payload.get("result"),
                "analysis": analysis_response.payload.get("result") if analysis_response else None,
                "report": writer_response.payload.get("result") if writer_response else None
            }
            
            await self.reply(message, final_result)


async def create_multi_agent_system(num_workers: int = 3) -> Dict[str, Any]:
    """Create and configure a multi-agent system."""
    # Create infrastructure
    message_bus = MessageBus()
    registry = AgentRegistry()
    
    # Create coordinator
    orchestrator = OrchestratorAgent("orchestrator", message_bus, registry)
    
    # Create specialist agents
    agents = [orchestrator]
    
    # Research agents
    for i in range(num_workers):
        agent = ResearchAgent(f"researcher_{i}", message_bus, registry)
        agents.append(agent)
    
    # Analysis agents
    for i in range(num_workers):
        agent = AnalysisAgent(f"analyst_{i}", message_bus, registry)
        agents.append(agent)
    
    # Writer agents
    for i in range(num_workers):
        agent = WriterAgent(f"writer_{i}", message_bus, registry)
        agents.append(agent)
    
    # Monitor agent
    monitor = MonitorAgent("monitor", message_bus, registry)
    agents.append(monitor)
    
    return {
        "agents": agents,
        "message_bus": message_bus,
        "registry": registry,
        "orchestrator": orchestrator,
        "monitor": monitor
    }


async def demonstrate_a2a_communication(system: Dict[str, Any]):
    """Demonstrate various A2A communication patterns."""
    orchestrator = system["orchestrator"]
    monitor = system["monitor"]
    
    print("\n=== Agent-to-Agent Communication Demo ===\n")
    
    # 1. Simple task delegation
    print("1. Simple Research Task")
    response = await orchestrator.request({
        "type": "research",
        "query": "quantum computing applications"
    }, timeout=10)
    
    if response:
        print(f"   Result: {response.payload.get('result', {}).get('findings', [])[:2]}")
    
    # 2. Data analysis
    print("\n2. Data Analysis Task")
    response = await orchestrator.request({
        "type": "data_analysis",
        "data": [10, 20, 15, 30, 25, 35, 40]
    }, timeout=10)
    
    if response:
        result = response.payload.get("result", {})
        print(f"   Average: {result.get('average')}")
        print(f"   Insights: {result.get('insights')}")
    
    # 3. Complex workflow
    print("\n3. Complex Workflow: Research and Report")
    response = await orchestrator.request({
        "type": "complex_workflow",
        "workflow_type": "research_and_report",
        "topic": "future of renewable energy"
    }, timeout=30)
    
    if response:
        print(f"   Workflow completed: {response.payload.get('status')}")
        print(f"   Research findings: {len(response.payload.get('research', {}).get('findings', []))} items")
        print(f"   Report generated: {response.payload.get('report', {}).get('title')}")
    
    # 4. System monitoring
    print("\n4. System Status")
    response = await monitor.request({
        "type": "system_status"
    }, timeout=5)
    
    if response:
        status = response.payload
        print(f"   Total agents: {status.get('total_agents')}")
        print(f"   Healthy agents: {status.get('healthy_agents')}")
    
    # 5. Broadcast message
    print("\n5. Broadcasting Alert")
    await orchestrator.broadcast({
        "alert": "System demonstration complete",
        "timestamp": datetime.now().isoformat()
    })
    print("   Alert broadcast to all agents")
    
    # 6. Topic-based communication
    print("\n6. Topic-based Communication")
    
    # Subscribe some agents to topics
    for agent in system["agents"][:3]:
        await agent.subscribe("updates")
    
    # Publish to topic
    await orchestrator.publish("updates", {
        "message": "New task available",
        "priority": "high"
    })
    print("   Published update to 'updates' topic")
    
    await asyncio.sleep(2)  # Let messages propagate


async def stress_test(system: Dict[str, Any], num_tasks: int = 100):
    """Stress test the multi-agent system."""
    orchestrator = system["orchestrator"]
    
    print(f"\n=== Stress Test: {num_tasks} tasks ===\n")
    
    start_time = asyncio.get_event_loop().time()
    
    # Send many tasks concurrently
    tasks = []
    for i in range(num_tasks):
        task_type = ["research", "data_analysis", "writing"][i % 3]
        
        if task_type == "research":
            task_data = {"type": "research", "query": f"topic_{i}"}
        elif task_type == "data_analysis":
            task_data = {"type": "data_analysis", "data": list(range(i, i+10))}
        else:
            task_data = {"type": "writing", "topic": f"subject_{i}"}
        
        tasks.append(orchestrator.request(task_data, timeout=30))
    
    # Wait for all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Count successes
    successful = sum(1 for r in results if r and not isinstance(r, Exception))
    failed = len(results) - successful
    
    duration = asyncio.get_event_loop().time() - start_time
    
    print(f"Completed {successful}/{num_tasks} tasks in {duration:.2f} seconds")
    print(f"Success rate: {successful/num_tasks*100:.1f}%")
    print(f"Throughput: {successful/duration:.1f} tasks/second")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KayGraph Agent-to-Agent Communication Demo"
    )
    
    parser.add_argument(
        "--agents",
        type=int,
        default=2,
        help="Number of agents of each type"
    )
    
    parser.add_argument(
        "--stress-test",
        action="store_true",
        help="Run stress test"
    )
    
    parser.add_argument(
        "--tasks",
        type=int,
        default=100,
        help="Number of tasks for stress test"
    )
    
    args = parser.parse_args()
    
    async def run():
        # Create system
        system = await create_multi_agent_system(num_workers=args.agents)
        
        # Start all agents
        for agent in system["agents"]:
            await agent.start()
        
        print(f"Started {len(system['agents'])} agents")
        
        try:
            # Run demonstrations
            await demonstrate_a2a_communication(system)
            
            # Run stress test if requested
            if args.stress_test:
                await stress_test(system, args.tasks)
            
        finally:
            # Stop all agents
            print("\n=== Shutting down agents ===")
            for agent in system["agents"]:
                await agent.stop()
    
    # Run the system
    asyncio.run(run())


if __name__ == "__main__":
    import uuid
    from datetime import datetime
    main()