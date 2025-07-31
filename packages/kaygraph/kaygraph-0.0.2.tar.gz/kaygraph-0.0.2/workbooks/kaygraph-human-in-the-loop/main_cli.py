#!/usr/bin/env python3
"""
CLI-based Human-in-the-Loop example.
Demonstrates document approval workflow with human review.
"""

import logging
import argparse
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, Node
from hitl_nodes import CLIHumanApprovalNode, ApprovalStatus
from utils.document_generator import generate_document

logger = logging.getLogger(__name__)


class DocumentGeneratorNode(Node):
    """Generate a document that needs approval."""
    
    def __init__(self):
        super().__init__(node_id="document_generator")
    
    def exec(self, prep_res):
        """Generate a document using AI."""
        topic = prep_res
        
        # Generate document (mocked here, use real LLM in production)
        document = generate_document(topic)
        
        return document
    
    def prep(self, shared):
        """Get document topic."""
        return shared.get("topic", "Quarterly Business Report")
    
    def post(self, shared, prep_res, exec_res):
        """Store generated document."""
        shared["generated_document"] = exec_res
        shared["approval_data"] = {
            "title": exec_res["title"],
            "summary": exec_res["summary"],
            "word_count": exec_res["word_count"],
            "sections": list(exec_res["sections"].keys()),
            "generated_at": datetime.utcnow().isoformat()
        }
        shared["approval_summary"] = f"Review '{exec_res['title']}' ({exec_res['word_count']} words)"
        
        logger.info(f"Generated document: {exec_res['title']}")
        return None  # Continue to approval


class DocumentReviewNode(CLIHumanApprovalNode):
    """Human review node for documents."""
    
    def __init__(self, **kwargs):
        super().__init__(
            approval_type="document_review",
            require_comments=True,
            **kwargs
        )
    
    def _prepare_request_data(self, shared):
        """Prepare document data for review."""
        doc = shared["generated_document"]
        return {
            "title": doc["title"],
            "summary": doc["summary"],
            "word_count": doc["word_count"],
            "sections": doc["sections"],
            "metadata": doc["metadata"]
        }
    
    def _get_approval_context(self, shared):
        """Get review context."""
        return {
            "topic": shared.get("topic"),
            "requester": shared.get("requester", "system"),
            "purpose": shared.get("purpose", "review"),
            "deadline": shared.get("deadline"),
            "previous_versions": shared.get("document_versions", [])
        }


class PublishDocumentNode(Node):
    """Publish approved document."""
    
    def __init__(self):
        super().__init__(node_id="publish_document")
    
    def exec(self, document):
        """Publish the document."""
        # In production, this would upload to CMS, send emails, etc.
        logger.info(f"Publishing document: {document['title']}")
        
        published_url = f"https://docs.company.com/{document['id']}"
        
        return {
            "published": True,
            "url": published_url,
            "published_at": datetime.utcnow().isoformat()
        }
    
    def prep(self, shared):
        """Get approved document."""
        return shared["generated_document"]
    
    def post(self, shared, prep_res, exec_res):
        """Store publication info."""
        shared["publication_result"] = exec_res
        logger.info(f"Document published at: {exec_res['url']}")
        return None


class ReviseDocumentNode(Node):
    """Revise document based on feedback."""
    
    def __init__(self):
        super().__init__(node_id="revise_document", max_retries=3)
    
    def exec(self, revision_request):
        """Revise the document."""
        document = revision_request["document"]
        feedback = revision_request["feedback"]
        modifications = revision_request.get("modifications", {})
        
        # Apply modifications and feedback
        # In production, use LLM to revise based on feedback
        revised_doc = document.copy()
        revised_doc["title"] = modifications.get("title", document["title"])
        revised_doc["revision"] = {
            "number": document.get("revision", {}).get("number", 0) + 1,
            "feedback": feedback,
            "revised_at": datetime.utcnow().isoformat()
        }
        
        # Add revision note to summary
        revised_doc["summary"] = f"[REVISED] {revised_doc['summary']}"
        
        logger.info(f"Document revised (revision {revised_doc['revision']['number']})")
        
        return revised_doc
    
    def prep(self, shared):
        """Prepare revision request."""
        approval = shared["document_review_approval"]
        return {
            "document": shared["generated_document"],
            "feedback": approval.get("comments", ""),
            "modifications": approval.get("modifications", {})
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store revised document."""
        # Keep version history
        if "document_versions" not in shared:
            shared["document_versions"] = []
        shared["document_versions"].append(shared["generated_document"])
        
        # Update current document
        shared["generated_document"] = exec_res
        
        # Update approval data for re-review
        shared["approval_data"]["revision_number"] = exec_res["revision"]["number"]
        shared["approval_summary"] = f"Review REVISED '{exec_res['title']}' (Revision {exec_res['revision']['number']})"
        
        return None  # Go back to approval


class EscalateApprovalNode(Node):
    """Escalate approval to senior staff."""
    
    def __init__(self):
        super().__init__(node_id="escalate_approval")
    
    def exec(self, escalation_data):
        """Handle escalation."""
        logger.warning(f"Escalating approval: {escalation_data['reason']}")
        
        # In production:
        # - Notify senior staff
        # - Create high-priority task
        # - Set up meeting
        
        return {
            "escalated": True,
            "escalated_to": "senior_management",
            "priority": "high",
            "escalation_id": f"ESC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
    
    def prep(self, shared):
        """Prepare escalation data."""
        return {
            "document": shared["generated_document"],
            "approval_history": shared.get("document_review_approval"),
            "reason": shared.get("escalation_reason", "Timeout or reviewer request"),
            "requester": shared.get("requester", "system")
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store escalation result."""
        shared["escalation_result"] = exec_res
        logger.info(f"Escalation ID: {exec_res['escalation_id']}")
        return None


class NotifyRejectionNode(Node):
    """Notify about document rejection."""
    
    def __init__(self):
        super().__init__(node_id="notify_rejection")
    
    def exec(self, rejection_data):
        """Send rejection notification."""
        logger.info(f"Document rejected: {rejection_data['reason']}")
        
        # In production, send notifications
        return {
            "notified": True,
            "recipients": ["document_author", "project_manager"],
            "notification_sent_at": datetime.utcnow().isoformat()
        }
    
    def prep(self, shared):
        """Prepare rejection data."""
        approval = shared["document_review_approval"]
        return {
            "document_title": shared["generated_document"]["title"],
            "reviewer": approval["reviewer"],
            "reason": approval.get("comments", "No reason provided"),
            "rejected_at": approval["timestamp"]
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store notification result."""
        shared["rejection_notification"] = exec_res
        return None


def create_document_approval_workflow(auto_approve=False, timeout_seconds=None):
    """Create the document approval workflow graph."""
    # Create nodes
    generator = DocumentGeneratorNode()
    reviewer = DocumentReviewNode(
        timeout_seconds=timeout_seconds,
        fallback_action="escalate"
    )
    publisher = PublishDocumentNode()
    reviser = ReviseDocumentNode()
    escalator = EscalateApprovalNode()
    rejector = NotifyRejectionNode()
    
    # Set auto-approve for testing
    reviewer.auto_approve = auto_approve
    
    # Build graph
    graph = Graph(start=generator)
    
    # Connect nodes
    generator >> reviewer
    
    # Approval paths
    reviewer - "approved" >> publisher
    reviewer - "rejected" >> rejector
    reviewer - "modified" >> reviser
    reviewer - "escalated" >> escalator
    reviewer - "timeout" >> escalator
    
    # Revision loop
    reviser >> reviewer
    
    return graph


def main():
    """Run the CLI HITL example."""
    parser = argparse.ArgumentParser(description="Document Approval HITL Workflow")
    parser.add_argument("--topic", default="Q4 2024 Financial Report",
                       help="Document topic to generate")
    parser.add_argument("--auto-approve", action="store_true",
                       help="Auto-approve for testing")
    parser.add_argument("--timeout", type=int, default=300,
                       help="Approval timeout in seconds")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create workflow
    workflow = create_document_approval_workflow(
        auto_approve=args.auto_approve,
        timeout_seconds=args.timeout
    )
    
    # Prepare shared context
    shared = {
        "topic": args.topic,
        "requester": "quarterly_report_system",
        "purpose": "stakeholder_distribution",
        "deadline": "2024-12-31"
    }
    
    print("\n🚀 Starting Document Approval Workflow")
    print(f"📄 Topic: {args.topic}")
    print(f"⏱️  Timeout: {args.timeout} seconds")
    print(f"🤖 Auto-approve: {'Yes' if args.auto_approve else 'No'}")
    print("-" * 60)
    
    # Run workflow
    try:
        with workflow:
            final_action = workflow.run(shared)
        
        print("\n✅ Workflow completed successfully!")
        
        # Show results
        if "publication_result" in shared:
            print(f"📰 Document published: {shared['publication_result']['url']}")
        elif "escalation_result" in shared:
            print(f"⬆️  Escalated: {shared['escalation_result']['escalation_id']}")
        elif "rejection_notification" in shared:
            print(f"❌ Document rejected and stakeholders notified")
        
        # Show approval details
        if "document_review_approval" in shared:
            approval = shared["document_review_approval"]
            print(f"\n👤 Reviewer: {approval['reviewer']}")
            print(f"💬 Comments: {approval.get('comments', 'None')}")
            
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        print(f"\n❌ Workflow failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())