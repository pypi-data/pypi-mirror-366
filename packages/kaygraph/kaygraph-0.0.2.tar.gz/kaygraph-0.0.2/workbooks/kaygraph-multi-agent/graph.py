"""
Multi-agent system graph using KayGraph AsyncGraph.
"""

import asyncio
from typing import Dict, Any, List
from kaygraph import AsyncGraph, AsyncNode
from agents import SupervisorAgent, ResearchAgent, WriterAgent, ReviewerAgent
from utils.messaging import MessageQueue, SharedWorkspace


class MultiAgentCoordinator(AsyncNode):
    """Coordinator node that manages the multi-agent system."""
    
    def __init__(self, agents: List[BaseAgent], *args, **kwargs):
        super().__init__(node_id="coordinator", *args, **kwargs)
        self.agents = agents
        self.message_queue = MessageQueue()
        self.workspace = SharedWorkspace()
        
        # Set up communication for all agents
        for agent in self.agents:
            agent.set_communication(self.message_queue, self.workspace)
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare coordination context."""
        return {
            "task": shared.get("task", ""),
            "max_iterations": shared.get("max_iterations", 10),
            "current_iteration": shared.get("current_iteration", 0)
        }
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Run one iteration of agent coordination."""
        iteration = prep_res["current_iteration"]
        self.logger.info(f"Coordination iteration {iteration}")
        
        # Run all agents concurrently
        agent_tasks = []
        for agent in self.agents:
            # Create a task for each agent
            task = asyncio.create_task(self._run_agent(agent, shared={}))
            agent_tasks.append((agent.agent_id, task))
        
        # Wait for all agents to complete their iteration
        results = {}
        for agent_id, task in agent_tasks:
            try:
                result = await task
                results[agent_id] = result
                self.logger.debug(f"{agent_id} completed iteration")
            except Exception as e:
                self.logger.error(f"{agent_id} failed: {e}")
                results[agent_id] = f"error: {str(e)}"
        
        # Check system state
        workspace_keys = await self.workspace.list_keys()
        queue_size = self.message_queue.get_queue_size()
        
        return {
            "iteration": iteration,
            "agent_results": results,
            "workspace_keys": workspace_keys,
            "queue_size": queue_size,
            "final_content_ready": "final_content" in workspace_keys
        }
    
    async def _run_agent(self, agent: BaseAgent, shared: Dict[str, Any]) -> str:
        """Run a single agent iteration."""
        return await agent._run_async(shared)
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> str:
        """Determine next action based on system state."""
        shared["current_iteration"] = exec_res["iteration"] + 1
        
        # Log progress
        self.logger.info(f"Iteration {exec_res['iteration']} complete. "
                        f"Queue size: {exec_res['queue_size']}, "
                        f"Workspace items: {len(exec_res['workspace_keys'])}")
        
        # Check if task is complete
        if exec_res["final_content_ready"]:
            # Retrieve final outputs
            final_content = await self.workspace.read("final_content")
            review = await self.workspace.read("review_feedback")
            research = await self.workspace.read("research_findings")
            
            shared["final_output"] = {
                "content": final_content,
                "review": review,
                "research": research
            }
            
            self.logger.info("Multi-agent task completed!")
            return "complete"
        
        # Check iteration limit
        if shared["current_iteration"] >= prep_res["max_iterations"]:
            self.logger.warning("Reached maximum iterations")
            return "timeout"
        
        # Continue if there are pending messages or work
        if exec_res["queue_size"] > 0 or shared["current_iteration"] < 3:
            await asyncio.sleep(0.1)  # Small delay between iterations
            return "continue"
        
        return "complete"


class InitNode(AsyncNode):
    """Initialize the multi-agent system."""
    
    async def prep_async(self, shared: Dict[str, Any]) -> str:
        """Get task from shared state."""
        return shared.get("task", "")
    
    async def exec_async(self, prep_res: str) -> Dict[str, Any]:
        """Set up initial state."""
        return {
            "task": prep_res,
            "agent_capabilities": {
                "researcher": "Information gathering and analysis",
                "writer": "Content creation and structuring",
                "reviewer": "Content review and quality assurance"
            },
            "task_status": {}
        }
    
    async def post_async(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> str:
        """Initialize shared state."""
        shared.update(exec_res)
        shared["current_iteration"] = 0
        self.logger.info(f"Initialized multi-agent system for task: {prep_res}")
        return "default"


class OutputNode(AsyncNode):
    """Format and display final output."""
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare output data."""
        return {
            "task": shared.get("task", ""),
            "final_output": shared.get("final_output", {}),
            "task_status": shared.get("task_status", {})
        }
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> str:
        """Format final output."""
        from utils.agent_prompts import format_final_output
        
        output = format_final_output(
            prep_res["task"],
            prep_res["final_output"]
        )
        
        return output
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> str:
        """Display final output."""
        print(exec_res)
        return "default"


def create_multi_agent_graph() -> AsyncGraph:
    """
    Create the multi-agent system graph.
    
    Returns:
        Configured AsyncGraph with multi-agent system
    """
    # Create agents
    supervisor = SupervisorAgent(node_id="supervisor_agent")
    researcher = ResearchAgent(node_id="researcher_agent")
    writer = WriterAgent(node_id="writer_agent")
    reviewer = ReviewerAgent(node_id="reviewer_agent")
    
    agents = [supervisor, researcher, writer, reviewer]
    
    # Create nodes
    init_node = InitNode(node_id="init")
    coordinator = MultiAgentCoordinator(agents=agents)
    output_node = OutputNode(node_id="output")
    
    # Connect nodes
    init_node >> coordinator
    coordinator >> ("continue", coordinator)  # Self-loop for iterations
    coordinator >> ("complete", output_node)
    coordinator >> ("timeout", output_node)
    
    # Create graph
    graph = AsyncGraph(start=init_node)
    graph.logger.info("Multi-agent graph created")
    
    return graph


if __name__ == "__main__":
    # Test graph creation
    import asyncio
    
    async def test():
        graph = create_multi_agent_graph()
        print(f"Multi-agent graph created with start node: {graph.start_node.node_id}")
    
    asyncio.run(test())