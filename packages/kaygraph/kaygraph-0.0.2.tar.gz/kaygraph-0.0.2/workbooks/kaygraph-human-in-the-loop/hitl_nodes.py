"""
Human-in-the-Loop nodes for KayGraph.
Provides various nodes for human interaction, approval, and feedback.
"""

import logging
import time
import json
import uuid
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime, timedelta
from enum import Enum
from abc import abstractmethod

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, ValidatedNode

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of human approval."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    TIMEOUT = "timeout"
    ESCALATED = "escalated"


class HumanResponse:
    """Container for human response data."""
    def __init__(self, 
                 status: ApprovalStatus,
                 reviewer: str,
                 timestamp: datetime,
                 comments: Optional[str] = None,
                 modifications: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.status = status
        self.reviewer = reviewer
        self.timestamp = timestamp
        self.comments = comments
        self.modifications = modifications or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "status": self.status.value,
            "reviewer": self.reviewer,
            "timestamp": self.timestamp.isoformat(),
            "comments": self.comments,
            "modifications": self.modifications,
            "metadata": self.metadata
        }


class BaseHumanApprovalNode(ValidatedNode):
    """
    Base class for human approval nodes.
    Handles common approval logic and audit trails.
    """
    
    def __init__(self,
                 approval_type: str,
                 timeout_seconds: Optional[int] = None,
                 fallback_action: str = "reject",
                 escalation_threshold: Optional[int] = None,
                 require_comments: bool = False,
                 allowed_reviewers: Optional[List[str]] = None,
                 node_id: Optional[str] = None):
        """
        Initialize human approval node.
        
        Args:
            approval_type: Type of approval (e.g., "document", "budget", "content")
            timeout_seconds: Max seconds to wait for approval (None = wait forever)
            fallback_action: Action on timeout ("reject", "approve", "escalate")
            escalation_threshold: Number of rejections before escalation
            require_comments: Whether comments are required
            allowed_reviewers: List of allowed reviewer IDs (None = anyone)
            node_id: Node identifier
        """
        super().__init__(node_id=node_id or f"human_approval_{approval_type}")
        self.approval_type = approval_type
        self.timeout_seconds = timeout_seconds
        self.fallback_action = fallback_action
        self.escalation_threshold = escalation_threshold
        self.require_comments = require_comments
        self.allowed_reviewers = allowed_reviewers
        self.approval_id = None
    
    def validate_input(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Validate approval request data."""
        if "request_data" not in prep_res:
            raise ValueError("No request data provided for approval")
        
        if "requester" not in prep_res:
            raise ValueError("No requester identified")
        
        return prep_res
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare approval request."""
        # Generate unique approval ID
        self.approval_id = str(uuid.uuid4())
        
        # Get request data
        request_data = self._prepare_request_data(shared)
        
        # Create approval request
        approval_request = {
            "approval_id": self.approval_id,
            "approval_type": self.approval_type,
            "request_data": request_data,
            "requester": shared.get("requester", "system"),
            "created_at": datetime.utcnow(),
            "timeout_at": datetime.utcnow() + timedelta(seconds=self.timeout_seconds) if self.timeout_seconds else None,
            "require_comments": self.require_comments,
            "allowed_reviewers": self.allowed_reviewers,
            "context": self._get_approval_context(shared)
        }
        
        return approval_request
    
    @abstractmethod
    def _prepare_request_data(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the specific data for approval. Override in subclasses."""
        pass
    
    @abstractmethod
    def _get_approval_context(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get additional context for the approval. Override in subclasses."""
        pass
    
    def exec(self, approval_request: Dict[str, Any]) -> HumanResponse:
        """Request and wait for human approval."""
        logger.info(f"Requesting {self.approval_type} approval: {self.approval_id}")
        
        # Submit approval request
        self._submit_approval_request(approval_request)
        
        # Wait for response
        response = self._wait_for_approval(approval_request)
        
        # Audit the decision
        self._audit_decision(approval_request, response)
        
        return response
    
    @abstractmethod
    def _submit_approval_request(self, request: Dict[str, Any]):
        """Submit approval request to human channel. Override in subclasses."""
        pass
    
    @abstractmethod
    def _wait_for_approval(self, request: Dict[str, Any]) -> HumanResponse:
        """Wait for human response. Override in subclasses."""
        pass
    
    def _audit_decision(self, request: Dict[str, Any], response: HumanResponse):
        """Log the human decision for audit trail."""
        audit_entry = {
            "approval_id": self.approval_id,
            "approval_type": self.approval_type,
            "request": request,
            "response": response.to_dict(),
            "duration_seconds": (response.timestamp - request["created_at"]).total_seconds()
        }
        
        # In production, write to audit log database
        logger.info(f"Audit trail: {json.dumps(audit_entry, default=str)}")
    
    def validate_output(self, response: HumanResponse) -> HumanResponse:
        """Validate the human response."""
        if self.require_comments and not response.comments:
            raise ValueError("Comments are required for this approval")
        
        if self.allowed_reviewers and response.reviewer not in self.allowed_reviewers:
            raise ValueError(f"Reviewer {response.reviewer} not authorized")
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], response: HumanResponse) -> str:
        """Process approval response and determine next action."""
        # Store response in shared
        shared[f"{self.approval_type}_approval"] = response.to_dict()
        
        # Apply any modifications
        if response.modifications:
            shared[f"{self.approval_type}_modifications"] = response.modifications
        
        # Determine next action based on status
        if response.status == ApprovalStatus.APPROVED:
            logger.info(f"{self.approval_type} approved by {response.reviewer}")
            return "approved"
        elif response.status == ApprovalStatus.REJECTED:
            logger.info(f"{self.approval_type} rejected by {response.reviewer}")
            return "rejected"
        elif response.status == ApprovalStatus.MODIFIED:
            logger.info(f"{self.approval_type} modified by {response.reviewer}")
            return "modified"
        elif response.status == ApprovalStatus.TIMEOUT:
            logger.warning(f"{self.approval_type} approval timed out")
            return self._handle_timeout(shared)
        elif response.status == ApprovalStatus.ESCALATED:
            logger.info(f"{self.approval_type} escalated by {response.reviewer}")
            return "escalated"
        else:
            return "error"
    
    def _handle_timeout(self, shared: Dict[str, Any]) -> str:
        """Handle timeout based on fallback action."""
        if self.fallback_action == "approve":
            logger.info("Timeout: Auto-approving")
            return "approved"
        elif self.fallback_action == "reject":
            logger.info("Timeout: Auto-rejecting")
            return "rejected"
        elif self.fallback_action == "escalate":
            logger.info("Timeout: Escalating")
            return "escalated"
        else:
            return "timeout"


class CLIHumanApprovalNode(BaseHumanApprovalNode):
    """
    Human approval node that uses command-line interface.
    Good for development and simple workflows.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_approve = False  # For testing
    
    def _prepare_request_data(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data that needs approval from shared context."""
        # This is generic - override for specific use cases
        return {
            "data": shared.get("approval_data", {}),
            "summary": shared.get("approval_summary", "No summary provided")
        }
    
    def _get_approval_context(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get context to help reviewer make decision."""
        return {
            "workflow": shared.get("workflow_name", "Unknown"),
            "step": shared.get("current_step", "Unknown"),
            "history": shared.get("approval_history", [])
        }
    
    def _submit_approval_request(self, request: Dict[str, Any]):
        """Display approval request in CLI."""
        print("\n" + "="*60)
        print(f"🔔 APPROVAL REQUEST: {self.approval_type.upper()}")
        print("="*60)
        print(f"ID: {request['approval_id']}")
        print(f"Requester: {request['requester']}")
        print(f"Created: {request['created_at']}")
        if request['timeout_at']:
            print(f"Timeout: {request['timeout_at']}")
        print("\n📋 REQUEST DATA:")
        print(json.dumps(request['request_data'], indent=2))
        print("\n🔍 CONTEXT:")
        print(json.dumps(request['context'], indent=2))
        print("="*60)
    
    def _wait_for_approval(self, request: Dict[str, Any]) -> HumanResponse:
        """Wait for CLI input from user."""
        start_time = datetime.utcnow()
        
        # Auto-approve for testing
        if self.auto_approve:
            time.sleep(0.5)  # Simulate thinking
            return HumanResponse(
                status=ApprovalStatus.APPROVED,
                reviewer="auto_tester",
                timestamp=datetime.utcnow(),
                comments="Auto-approved for testing"
            )
        
        while True:
            # Check timeout
            if request['timeout_at'] and datetime.utcnow() > request['timeout_at']:
                return HumanResponse(
                    status=ApprovalStatus.TIMEOUT,
                    reviewer="system",
                    timestamp=datetime.utcnow(),
                    comments="Approval request timed out"
                )
            
            # Get user input
            print("\n🤔 DECISION OPTIONS:")
            print("  [A]pprove - Approve the request")
            print("  [R]eject  - Reject the request")
            print("  [M]odify  - Approve with modifications")
            print("  [E]scalate - Escalate to supervisor")
            print("  [T]imeout - Simulate timeout")
            
            choice = input("\nYour choice [A/R/M/E/T]: ").strip().upper()
            
            if choice not in ['A', 'R', 'M', 'E', 'T']:
                print("❌ Invalid choice. Please try again.")
                continue
            
            # Get reviewer name
            reviewer = input("Your name/ID: ").strip() or "anonymous"
            
            # Check if reviewer is allowed
            if self.allowed_reviewers and reviewer not in self.allowed_reviewers:
                print(f"❌ You ({reviewer}) are not authorized to approve this.")
                continue
            
            # Get comments
            comments = None
            if self.require_comments or choice in ['R', 'M', 'E']:
                comments = input("Comments (required): ").strip()
                if self.require_comments and not comments:
                    print("❌ Comments are required.")
                    continue
            
            # Get modifications if needed
            modifications = {}
            if choice == 'M':
                print("\n📝 Enter modifications (JSON format):")
                mod_input = input().strip()
                try:
                    modifications = json.loads(mod_input) if mod_input else {}
                except json.JSONDecodeError:
                    print("❌ Invalid JSON. Please try again.")
                    continue
            
            # Create response
            status_map = {
                'A': ApprovalStatus.APPROVED,
                'R': ApprovalStatus.REJECTED,
                'M': ApprovalStatus.MODIFIED,
                'E': ApprovalStatus.ESCALATED,
                'T': ApprovalStatus.TIMEOUT
            }
            
            return HumanResponse(
                status=status_map[choice],
                reviewer=reviewer if choice != 'T' else "system",
                timestamp=datetime.utcnow(),
                comments=comments,
                modifications=modifications,
                metadata={
                    "response_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                    "interface": "CLI"
                }
            )


class WebHumanApprovalNode(AsyncNode, BaseHumanApprovalNode):
    """
    Human approval node that uses web interface.
    Suitable for production use with FastAPI backend.
    """
    
    def __init__(self, 
                 api_endpoint: str,
                 *args, **kwargs):
        """
        Initialize web-based approval node.
        
        Args:
            api_endpoint: API endpoint for approval service
        """
        AsyncNode.__init__(self)
        BaseHumanApprovalNode.__init__(self, *args, **kwargs)
        self.api_endpoint = api_endpoint
    
    def _prepare_request_data(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for web display."""
        return {
            "title": shared.get("approval_title", f"{self.approval_type} Approval"),
            "description": shared.get("approval_description", ""),
            "data": shared.get("approval_data", {}),
            "display_fields": shared.get("display_fields", []),
            "actions": ["approve", "reject", "modify", "escalate"]
        }
    
    def _get_approval_context(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get context for web display."""
        return {
            "priority": shared.get("priority", "normal"),
            "category": shared.get("category", self.approval_type),
            "tags": shared.get("tags", []),
            "related_approvals": shared.get("related_approvals", [])
        }
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Async version of prep."""
        return self.prep(shared)
    
    async def exec_async(self, approval_request: Dict[str, Any]) -> HumanResponse:
        """Submit approval and poll for response."""
        logger.info(f"Submitting web approval: {self.approval_id}")
        
        # Submit to API
        await self._submit_approval_request_async(approval_request)
        
        # Poll for response
        response = await self._wait_for_approval_async(approval_request)
        
        # Audit
        self._audit_decision(approval_request, response)
        
        return response
    
    async def _submit_approval_request_async(self, request: Dict[str, Any]):
        """Submit approval request to web API."""
        # In production, use aiohttp or httpx
        # This is a mock implementation
        logger.info(f"POST {self.api_endpoint}/approvals")
        logger.info(f"Request: {json.dumps(request, default=str)}")
        
        # Simulate API call
        import asyncio
        await asyncio.sleep(0.1)
    
    async def _wait_for_approval_async(self, request: Dict[str, Any]) -> HumanResponse:
        """Poll API for approval response."""
        import asyncio
        
        poll_interval = 2  # seconds
        start_time = datetime.utcnow()
        
        while True:
            # Check timeout
            if request['timeout_at'] and datetime.utcnow() > request['timeout_at']:
                return HumanResponse(
                    status=ApprovalStatus.TIMEOUT,
                    reviewer="system",
                    timestamp=datetime.utcnow(),
                    comments="Approval request timed out"
                )
            
            # Poll API
            # In production: response = await http_client.get(f"{self.api_endpoint}/approvals/{self.approval_id}")
            
            # Simulate response (in production, parse API response)
            await asyncio.sleep(poll_interval)
            
            # Mock approved response after 5 seconds
            if (datetime.utcnow() - start_time).total_seconds() > 5:
                return HumanResponse(
                    status=ApprovalStatus.APPROVED,
                    reviewer="web_user_123",
                    timestamp=datetime.utcnow(),
                    comments="Approved via web interface",
                    metadata={
                        "ip_address": "192.168.1.100",
                        "user_agent": "Mozilla/5.0",
                        "interface": "Web"
                    }
                )
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], response: HumanResponse) -> str:
        """Async version of post."""
        return self.post(shared, prep_res, response)
    
    # Required stubs for BaseHumanApprovalNode
    def _submit_approval_request(self, request: Dict[str, Any]):
        """Sync version - not used in async node."""
        pass
    
    def _wait_for_approval(self, request: Dict[str, Any]) -> HumanResponse:
        """Sync version - not used in async node."""
        pass


class BatchHumanApprovalNode(BaseHumanApprovalNode):
    """
    Node for batch human approvals.
    Groups similar requests for efficient review.
    """
    
    def __init__(self,
                 batch_size: int = 10,
                 batch_timeout: int = 300,
                 *args, **kwargs):
        """
        Initialize batch approval node.
        
        Args:
            batch_size: Max items in a batch
            batch_timeout: Max seconds to wait for batch to fill
        """
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_batch = []
    
    def _prepare_request_data(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare batch of items for approval."""
        # Add current item to batch
        current_item = shared.get("approval_item", {})
        self.pending_batch.append(current_item)
        
        # Check if batch is ready
        batch_ready = (
            len(self.pending_batch) >= self.batch_size or
            shared.get("force_batch_approval", False)
        )
        
        if batch_ready:
            batch_data = {
                "items": self.pending_batch.copy(),
                "batch_size": len(self.pending_batch),
                "batch_type": self.approval_type
            }
            self.pending_batch.clear()
            return batch_data
        else:
            # Return empty - no approval needed yet
            return {}
    
    def _get_approval_context(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get batch context."""
        return {
            "total_pending": shared.get("total_pending_items", 0),
            "batch_number": shared.get("batch_number", 1),
            "previous_batches": shared.get("previous_batch_results", [])
        }


if __name__ == "__main__":
    # Test the approval nodes
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test CLI approval
    print("Testing CLI Human Approval Node...")
    
    shared = {
        "approval_data": {
            "document": "Quarterly Report Q4 2024",
            "author": "AI Assistant",
            "word_count": 5000,
            "key_findings": [
                "Revenue increased 15%",
                "Customer satisfaction at all-time high",
                "Need to invest in R&D"
            ]
        },
        "approval_summary": "Please review the Q4 2024 quarterly report",
        "requester": "report_generator_ai",
        "workflow_name": "quarterly_reporting"
    }
    
    # Create approval node
    approval_node = CLIHumanApprovalNode(
        approval_type="document",
        timeout_seconds=60,
        fallback_action="escalate",
        require_comments=True
    )
    
    # For testing, enable auto-approve
    approval_node.auto_approve = True
    
    # Run approval
    action = approval_node.run(shared)
    print(f"\nApproval result: {action}")
    print(f"Approval details: {json.dumps(shared.get('document_approval', {}), indent=2)}")