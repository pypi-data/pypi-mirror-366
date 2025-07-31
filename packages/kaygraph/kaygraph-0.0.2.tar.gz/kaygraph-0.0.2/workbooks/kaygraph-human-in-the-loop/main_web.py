#!/usr/bin/env python3
"""
Web-based Human-in-the-Loop example with FastAPI.
Production-ready approval system with web interface.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import AsyncGraph, Node
from hitl_nodes import WebHumanApprovalNode, ApprovalStatus, HumanResponse

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="KayGraph HITL Approval System")

# In-memory storage for demo (use database in production)
approval_store: Dict[str, dict] = {}
workflow_store: Dict[str, dict] = {}


# Pydantic models for API
class ApprovalRequest(BaseModel):
    title: str
    description: str
    data: dict
    requester: str
    priority: str = "normal"
    timeout_seconds: Optional[int] = 300


class ApprovalDecision(BaseModel):
    approval_id: str
    status: str  # approved, rejected, modified, escalated
    reviewer: str
    comments: Optional[str] = None
    modifications: Optional[dict] = None


class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    current_step: str
    created_at: datetime
    completed_at: Optional[datetime] = None


# API endpoints
@app.get("/")
async def home():
    """Serve the web UI."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>KayGraph HITL Approval System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .approval-card { background: white; padding: 20px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .pending { border-left: 5px solid #f39c12; }
            .approved { border-left: 5px solid #27ae60; }
            .rejected { border-left: 5px solid #e74c3c; }
            .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 3px; cursor: pointer; }
            .btn-approve { background: #27ae60; color: white; }
            .btn-reject { background: #e74c3c; color: white; }
            .btn-modify { background: #3498db; color: white; }
            .btn-escalate { background: #9b59b6; color: white; }
            .data-display { background: #ecf0f1; padding: 10px; border-radius: 3px; margin: 10px 0; }
            .comments { width: 100%; padding: 10px; margin: 10px 0; }
            .priority-high { color: #e74c3c; font-weight: bold; }
            .priority-normal { color: #2c3e50; }
            .priority-low { color: #95a5a6; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 KayGraph HITL Approval System</h1>
                <p>Review and approve AI-generated content and decisions</p>
            </div>
            
            <div id="approvals-container">
                <h2>📋 Pending Approvals</h2>
                <div id="pending-approvals"></div>
                
                <h2>✅ Recent Decisions</h2>
                <div id="recent-decisions"></div>
            </div>
        </div>
        
        <script>
            // Fetch and display approvals
            async function loadApprovals() {
                const response = await fetch('/api/approvals/pending');
                const approvals = await response.json();
                
                const container = document.getElementById('pending-approvals');
                container.innerHTML = '';
                
                if (approvals.length === 0) {
                    container.innerHTML = '<p>No pending approvals</p>';
                    return;
                }
                
                approvals.forEach(approval => {
                    const card = createApprovalCard(approval);
                    container.appendChild(card);
                });
            }
            
            function createApprovalCard(approval) {
                const card = document.createElement('div');
                card.className = 'approval-card pending';
                
                const priorityClass = `priority-${approval.context.priority}`;
                
                card.innerHTML = `
                    <h3>${approval.request_data.title}</h3>
                    <p class="${priorityClass}">Priority: ${approval.context.priority}</p>
                    <p><strong>Requester:</strong> ${approval.requester}</p>
                    <p><strong>Type:</strong> ${approval.approval_type}</p>
                    <p>${approval.request_data.description}</p>
                    
                    <div class="data-display">
                        <strong>Data:</strong>
                        <pre>${JSON.stringify(approval.request_data.data, null, 2)}</pre>
                    </div>
                    
                    <textarea class="comments" id="comments-${approval.approval_id}" 
                              placeholder="Comments (required for reject/modify)"></textarea>
                    
                    <div class="actions">
                        <button class="btn btn-approve" onclick="makeDecision('${approval.approval_id}', 'approved')">
                            ✅ Approve
                        </button>
                        <button class="btn btn-reject" onclick="makeDecision('${approval.approval_id}', 'rejected')">
                            ❌ Reject
                        </button>
                        <button class="btn btn-modify" onclick="makeDecision('${approval.approval_id}', 'modified')">
                            ✏️ Modify
                        </button>
                        <button class="btn btn-escalate" onclick="makeDecision('${approval.approval_id}', 'escalated')">
                            ⬆️ Escalate
                        </button>
                    </div>
                `;
                
                return card;
            }
            
            async function makeDecision(approvalId, status) {
                const comments = document.getElementById(`comments-${approvalId}`).value;
                
                if ((status === 'rejected' || status === 'modified') && !comments) {
                    alert('Comments are required for reject/modify decisions');
                    return;
                }
                
                const decision = {
                    approval_id: approvalId,
                    status: status,
                    reviewer: prompt('Your name/ID:') || 'anonymous',
                    comments: comments
                };
                
                if (status === 'modified') {
                    const modifications = prompt('Enter modifications (JSON format):');
                    try {
                        decision.modifications = JSON.parse(modifications || '{}');
                    } catch (e) {
                        alert('Invalid JSON for modifications');
                        return;
                    }
                }
                
                const response = await fetch('/api/approvals/decide', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(decision)
                });
                
                if (response.ok) {
                    alert('Decision recorded successfully');
                    loadApprovals();
                    loadRecentDecisions();
                } else {
                    alert('Error recording decision');
                }
            }
            
            async function loadRecentDecisions() {
                const response = await fetch('/api/approvals/recent');
                const decisions = await response.json();
                
                const container = document.getElementById('recent-decisions');
                container.innerHTML = '';
                
                decisions.slice(0, 5).forEach(decision => {
                    const card = document.createElement('div');
                    card.className = `approval-card ${decision.status}`;
                    card.innerHTML = `
                        <h4>${decision.title}</h4>
                        <p><strong>Status:</strong> ${decision.status}</p>
                        <p><strong>Reviewer:</strong> ${decision.reviewer}</p>
                        <p><strong>Time:</strong> ${new Date(decision.timestamp).toLocaleString()}</p>
                        ${decision.comments ? `<p><strong>Comments:</strong> ${decision.comments}</p>` : ''}
                    `;
                    container.appendChild(card);
                });
            }
            
            // Load approvals on page load
            loadApprovals();
            loadRecentDecisions();
            
            // Refresh every 5 seconds
            setInterval(() => {
                loadApprovals();
                loadRecentDecisions();
            }, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/approvals/submit")
async def submit_approval(request: ApprovalRequest):
    """Submit a new approval request."""
    approval_id = str(uuid.uuid4())
    
    approval_data = {
        "approval_id": approval_id,
        "approval_type": "web_approval",
        "request_data": {
            "title": request.title,
            "description": request.description,
            "data": request.data
        },
        "requester": request.requester,
        "created_at": datetime.utcnow(),
        "status": ApprovalStatus.PENDING.value,
        "context": {
            "priority": request.priority,
            "interface": "web"
        }
    }
    
    approval_store[approval_id] = approval_data
    logger.info(f"Approval request submitted: {approval_id}")
    
    return {"approval_id": approval_id, "status": "submitted"}


@app.get("/api/approvals/pending")
async def get_pending_approvals():
    """Get all pending approval requests."""
    pending = [
        approval for approval in approval_store.values()
        if approval["status"] == ApprovalStatus.PENDING.value
    ]
    return pending


@app.get("/api/approvals/{approval_id}")
async def get_approval(approval_id: str):
    """Get specific approval request."""
    if approval_id not in approval_store:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval_store[approval_id]


@app.post("/api/approvals/decide")
async def make_decision(decision: ApprovalDecision):
    """Record a decision for an approval request."""
    if decision.approval_id not in approval_store:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    approval = approval_store[decision.approval_id]
    
    # Update approval with decision
    approval["status"] = decision.status
    approval["decision"] = {
        "status": decision.status,
        "reviewer": decision.reviewer,
        "timestamp": datetime.utcnow().isoformat(),
        "comments": decision.comments,
        "modifications": decision.modifications
    }
    
    logger.info(f"Decision recorded for {decision.approval_id}: {decision.status}")
    
    return {"status": "decision_recorded"}


@app.get("/api/approvals/recent")
async def get_recent_decisions():
    """Get recent approval decisions."""
    decided = [
        {
            **approval["decision"],
            "title": approval["request_data"]["title"],
            "approval_id": approval["approval_id"]
        }
        for approval in approval_store.values()
        if "decision" in approval
    ]
    
    # Sort by timestamp
    decided.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return decided


@app.post("/api/workflows/start")
async def start_workflow(background_tasks: BackgroundTasks):
    """Start a new approval workflow."""
    workflow_id = str(uuid.uuid4())
    
    # Create workflow instance
    workflow_data = {
        "workflow_id": workflow_id,
        "status": "running",
        "current_step": "generating_content",
        "created_at": datetime.utcnow()
    }
    
    workflow_store[workflow_id] = workflow_data
    
    # Run workflow in background
    background_tasks.add_task(run_approval_workflow, workflow_id)
    
    return {"workflow_id": workflow_id, "status": "started"}


@app.get("/api/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get workflow status."""
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow_store[workflow_id]


# Workflow implementation
class ContentGeneratorNode(Node):
    """Generate content that needs approval."""
    
    def exec(self, prep_res):
        """Generate content."""
        return {
            "title": "Monthly Marketing Report",
            "content": "This month's marketing metrics show...",
            "metrics": {
                "leads": 1250,
                "conversions": 89,
                "revenue": 125000
            }
        }
    
    def post(self, shared, prep_res, exec_res):
        """Prepare for approval."""
        shared["generated_content"] = exec_res
        shared["approval_title"] = exec_res["title"]
        shared["approval_description"] = "Please review the monthly marketing report"
        shared["approval_data"] = exec_res
        return None


async def run_approval_workflow(workflow_id: str):
    """Run the approval workflow."""
    try:
        # Update workflow status
        workflow_store[workflow_id]["current_step"] = "awaiting_approval"
        
        # Create workflow graph
        generator = ContentGeneratorNode()
        approver = WebHumanApprovalNode(
            api_endpoint="http://localhost:8000/api",
            approval_type="content_review",
            timeout_seconds=300
        )
        
        # Build graph
        graph = AsyncGraph(start=generator)
        generator >> approver
        
        # Run workflow
        shared = {
            "workflow_id": workflow_id,
            "requester": "marketing_system"
        }
        
        await graph.run_async(shared)
        
        # Update workflow completion
        workflow_store[workflow_id]["status"] = "completed"
        workflow_store[workflow_id]["completed_at"] = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {e}")
        workflow_store[workflow_id]["status"] = "failed"
        workflow_store[workflow_id]["error"] = str(e)


def main():
    """Run the FastAPI server."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting KayGraph HITL Web Server")
    print("📍 Access the UI at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()