"""
Agent implementations using KayGraph AsyncNode.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from kaygraph import AsyncNode
from utils.messaging import Message, MessageQueue, SharedWorkspace
from utils.agent_prompts import (
    get_supervisor_prompt, get_researcher_prompt,
    get_writer_prompt, get_reviewer_prompt,
    parse_supervisor_plan, get_mock_response
)


class BaseAgent(AsyncNode):
    """Base class for all agents with common functionality."""
    
    def __init__(self, agent_id: str, capabilities: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.message_queue: Optional[MessageQueue] = None
        self.workspace: Optional[SharedWorkspace] = None
    
    def set_communication(self, message_queue: MessageQueue, workspace: SharedWorkspace):
        """Set communication channels."""
        self.message_queue = message_queue
        self.workspace = workspace
    
    async def send_message(self, to_agent: str, message_type: str, content: Any):
        """Send message to another agent."""
        if self.message_queue:
            message = Message(
                from_agent=self.agent_id,
                to_agent=to_agent,
                message_type=message_type,
                content=content
            )
            await self.message_queue.send_message(message)
    
    async def get_messages(self) -> List[Message]:
        """Get pending messages."""
        if self.message_queue:
            return await self.message_queue.get_messages_for_agent(self.agent_id)
        return []
    
    async def write_to_workspace(self, key: str, value: Any):
        """Write to shared workspace."""
        if self.workspace:
            await self.workspace.write(key, value, self.agent_id)
    
    async def read_from_workspace(self, key: str) -> Optional[Any]:
        """Read from shared workspace."""
        if self.workspace:
            return await self.workspace.read(key)
        return None


class SupervisorAgent(BaseAgent):
    """Supervisor agent that coordinates other agents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            agent_id="supervisor",
            capabilities="Task planning and delegation",
            *args, **kwargs
        )
        self.delegation_plan: Optional[Dict[str, Any]] = None
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare supervisor context."""
        return {
            "task": shared.get("task", ""),
            "agent_capabilities": shared.get("agent_capabilities", {}),
            "task_status": shared.get("task_status", {})
        }
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Create delegation plan."""
        # Get messages to check for completed tasks
        messages = await self.get_messages()
        
        # If this is initial planning
        if not self.delegation_plan:
            prompt = get_supervisor_prompt(
                prep_res["task"],
                prep_res["agent_capabilities"]
            )
            
            # In production, call real LLM
            response = get_mock_response("supervisor", prompt)
            self.delegation_plan = parse_supervisor_plan(response)
            
            self.logger.info(f"Created delegation plan: {self.delegation_plan}")
            return {
                "action": "delegate",
                "plan": self.delegation_plan
            }
        
        # Check for completed tasks
        completed_tasks = {}
        for msg in messages:
            if msg.message_type == "task_complete":
                agent = msg.content["agent"]
                result = msg.content["result"]
                completed_tasks[agent] = result
                self.logger.info(f"Received completion from {agent}")
        
        return {
            "action": "monitor",
            "completed_tasks": completed_tasks
        }
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> str:
        """Coordinate based on execution results."""
        action = exec_res["action"]
        
        if action == "delegate":
            # Send initial tasks to agents
            plan = exec_res["plan"]
            
            # Assign research task
            if "researcher" in plan["agents_needed"]:
                await self.send_message(
                    "researcher",
                    "assign_research",
                    {"topic": shared["task"]}
                )
                shared["task_status"]["researcher"] = "assigned"
            
            return "monitoring"
        
        elif action == "monitor":
            # Update task status
            for agent, result in exec_res["completed_tasks"].items():
                shared["task_status"][agent] = "completed"
                await self.write_to_workspace(f"{agent}_output", result)
            
            # Check what to do next
            status = shared["task_status"]
            
            # If research done but not writing, start writer
            if status.get("researcher") == "completed" and status.get("writer") != "assigned":
                research = await self.read_from_workspace("researcher_output")
                await self.send_message(
                    "writer",
                    "assign_writing",
                    {"topic": shared["task"], "research": research}
                )
                shared["task_status"]["writer"] = "assigned"
                return "monitoring"
            
            # If writing done but not review, start reviewer
            if status.get("writer") == "completed" and status.get("reviewer") != "assigned":
                content = await self.read_from_workspace("writer_output")
                await self.send_message(
                    "reviewer",
                    "assign_review",
                    {"content": content}
                )
                shared["task_status"]["reviewer"] = "assigned"
                return "monitoring"
            
            # Check if all done
            if all(status.get(agent) == "completed" 
                   for agent in ["researcher", "writer", "reviewer"]):
                self.logger.info("All tasks completed!")
                return "complete"
            
            return "monitoring"


class ResearchAgent(BaseAgent):
    """Research agent that gathers information."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            agent_id="researcher",
            capabilities="Information gathering and analysis",
            *args, **kwargs
        )
    
    async def prep_async(self, shared: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for research assignments."""
        messages = await self.get_messages()
        
        for msg in messages:
            if msg.message_type == "assign_research":
                return msg.content
        
        return None
    
    async def exec_async(self, prep_res: Optional[Dict]) -> Optional[str]:
        """Perform research."""
        if not prep_res:
            return None
        
        topic = prep_res.get("topic", "")
        prompt = get_researcher_prompt(topic)
        
        # Simulate research time
        await asyncio.sleep(1)
        
        # In production, call real LLM
        research_findings = get_mock_response("researcher", prompt)
        
        self.logger.info(f"Completed research on: {topic}")
        return research_findings
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Optional[Dict], 
                         exec_res: Optional[str]) -> str:
        """Share research results."""
        if exec_res:
            # Notify supervisor
            await self.send_message(
                "supervisor",
                "task_complete",
                {"agent": self.agent_id, "result": exec_res}
            )
            
            # Share with other agents
            await self.write_to_workspace("research_findings", exec_res)
        
        return "wait"


class WriterAgent(BaseAgent):
    """Writer agent that creates content."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            agent_id="writer",
            capabilities="Content creation and structuring",
            *args, **kwargs
        )
    
    async def prep_async(self, shared: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for writing assignments."""
        messages = await self.get_messages()
        
        for msg in messages:
            if msg.message_type == "assign_writing":
                return msg.content
        
        return None
    
    async def exec_async(self, prep_res: Optional[Dict]) -> Optional[str]:
        """Create content."""
        if not prep_res:
            return None
        
        topic = prep_res.get("topic", "")
        research = prep_res.get("research", "")
        
        prompt = get_writer_prompt(topic, research)
        
        # Simulate writing time
        await asyncio.sleep(1.5)
        
        # In production, call real LLM
        content = get_mock_response("writer", prompt)
        
        self.logger.info(f"Completed writing on: {topic}")
        return content
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Optional[Dict], 
                         exec_res: Optional[str]) -> str:
        """Share written content."""
        if exec_res:
            # Notify supervisor
            await self.send_message(
                "supervisor",
                "task_complete",
                {"agent": self.agent_id, "result": exec_res}
            )
            
            # Share with other agents
            await self.write_to_workspace("draft_content", exec_res)
        
        return "wait"


class ReviewerAgent(BaseAgent):
    """Reviewer agent that reviews and improves content."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(
            agent_id="reviewer",
            capabilities="Content review and quality assurance",
            *args, **kwargs
        )
    
    async def prep_async(self, shared: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for review assignments."""
        messages = await self.get_messages()
        
        for msg in messages:
            if msg.message_type == "assign_review":
                return msg.content
        
        return None
    
    async def exec_async(self, prep_res: Optional[Dict]) -> Optional[str]:
        """Review content."""
        if not prep_res:
            return None
        
        content = prep_res.get("content", "")
        prompt = get_reviewer_prompt(content)
        
        # Simulate review time
        await asyncio.sleep(1)
        
        # In production, call real LLM
        review = get_mock_response("reviewer", prompt)
        
        self.logger.info("Completed content review")
        return review
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Optional[Dict], 
                         exec_res: Optional[str]) -> str:
        """Share review results."""
        if exec_res:
            # Notify supervisor
            await self.send_message(
                "supervisor",
                "task_complete",
                {"agent": self.agent_id, "result": exec_res}
            )
            
            # Share review
            await self.write_to_workspace("review_feedback", exec_res)
            
            # If approved, mark final content
            if "approve" in exec_res.lower():
                draft = await self.read_from_workspace("draft_content")
                if draft:
                    await self.write_to_workspace("final_content", draft)
        
        return "wait"