"""
Database tool integration example using KayGraph.

Demonstrates integrating SQLite database operations with KayGraph
for task management workflows.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from kaygraph import Node, Graph, BatchNode
from utils.database import DatabaseManager, init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class InitDatabaseNode(Node):
    """Initialize database with schema."""
    
    def prep(self, shared):
        """Get database configuration."""
        return {
            "db_path": shared.get("db_path", "tasks.db"),
            "reset": shared.get("reset_db", False)
        }
    
    def exec(self, config):
        """Initialize database."""
        db_path = config["db_path"]
        
        if config["reset"]:
            # Remove existing database
            import os
            if os.path.exists(db_path):
                os.remove(db_path)
                self.logger.info(f"Removed existing database: {db_path}")
        
        # Initialize database
        db = init_database(db_path)
        db.disconnect()
        
        self.logger.info(f"Initialized database: {db_path}")
        
        return {
            "db_path": db_path,
            "initialized": True
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store database info."""
        shared["db_info"] = exec_res
        return "default"


class CreateTaskNode(Node):
    """Create a new task in the database."""
    
    def prep(self, shared):
        """Get task data."""
        return {
            "task": shared.get("new_task"),
            "db_path": shared.get("db_info", {}).get("db_path", "tasks.db")
        }
    
    def exec(self, data):
        """Create the task."""
        if not data["task"]:
            return {"success": False, "error": "No task data provided"}
        
        task_data = data["task"]
        
        with DatabaseManager(data["db_path"]) as db:
            try:
                task_id = db.create_task(task_data)
                
                # Retrieve created task
                created_task = db.get_task(task_id)
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "task": created_task
                }
            
            except Exception as e:
                self.logger.error(f"Failed to create task: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def post(self, shared, prep_res, exec_res):
        """Store result."""
        shared["create_result"] = exec_res
        
        if exec_res["success"]:
            print(f"\n✅ Created task #{exec_res['task_id']}: {exec_res['task']['title']}")
            return "list"
        else:
            print(f"\n❌ Failed to create task: {exec_res['error']}")
            return "error"


class ListTasksNode(Node):
    """List tasks from the database."""
    
    def prep(self, shared):
        """Get filter parameters."""
        return {
            "db_path": shared.get("db_info", {}).get("db_path", "tasks.db"),
            "filters": shared.get("list_filters", {}),
            "limit": shared.get("list_limit", 10)
        }
    
    def exec(self, params):
        """Query tasks."""
        with DatabaseManager(params["db_path"]) as db:
            tasks = db.list_tasks(
                status=params["filters"].get("status"),
                priority=params["filters"].get("priority"),
                limit=params["limit"]
            )
            
            # Get statistics
            stats = db.get_statistics()
            
            return {
                "tasks": tasks,
                "count": len(tasks),
                "statistics": stats
            }
    
    def post(self, shared, prep_res, exec_res):
        """Display results."""
        shared["task_list"] = exec_res["tasks"]
        shared["task_stats"] = exec_res["statistics"]
        
        # Display tasks
        print(f"\n📋 Tasks ({exec_res['count']} found):")
        print("-" * 60)
        
        if exec_res["tasks"]:
            for task in exec_res["tasks"]:
                status_emoji = {
                    "pending": "⏳",
                    "in_progress": "🔄",
                    "completed": "✅",
                    "cancelled": "❌"
                }.get(task["status"], "❓")
                
                print(f"{status_emoji} [{task['id']:3d}] {task['title']:<40} P{task['priority']}")
                if task["description"]:
                    print(f"        {task['description']}")
                if task["tags"]:
                    print(f"        Tags: {', '.join(task['tags'])}")
        else:
            print("No tasks found.")
        
        # Display statistics
        stats = exec_res["statistics"]
        print(f"\n📊 Statistics:")
        print(f"  Total tasks: {stats['total_tasks']}")
        print(f"  By status: {stats['by_status']}")
        print(f"  Overdue: {stats['overdue']}")
        
        return None


class UpdateTaskBatchNode(BatchNode):
    """Update multiple tasks in batch."""
    
    def prep(self, shared):
        """Get tasks to update."""
        updates = shared.get("task_updates", [])
        db_path = shared.get("db_info", {}).get("db_path", "tasks.db")
        
        # Add db_path to each update
        return [(update, db_path) for update in updates]
    
    def exec(self, item):
        """Update a single task."""
        update_data, db_path = item
        task_id = update_data.get("id")
        updates = {k: v for k, v in update_data.items() if k != "id"}
        
        with DatabaseManager(db_path) as db:
            success = db.update_task(task_id, updates)
            
            if success:
                updated_task = db.get_task(task_id)
                return {
                    "task_id": task_id,
                    "success": True,
                    "task": updated_task
                }
            else:
                return {
                    "task_id": task_id,
                    "success": False,
                    "error": "Task not found"
                }
    
    def post(self, shared, prep_res, exec_res):
        """Summarize updates."""
        successful = sum(1 for r in exec_res if r["success"])
        failed = len(exec_res) - successful
        
        print(f"\n📝 Batch Update Results:")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        
        for result in exec_res:
            if result["success"]:
                task = result["task"]
                print(f"  - Updated #{result['task_id']}: {task['title']} -> {task['status']}")
            else:
                print(f"  - Failed #{result['task_id']}: {result['error']}")
        
        shared["update_results"] = exec_res
        return None


class SearchTasksNode(Node):
    """Search tasks by keyword."""
    
    def prep(self, shared):
        """Get search query."""
        return {
            "query": shared.get("search_query", ""),
            "db_path": shared.get("db_info", {}).get("db_path", "tasks.db")
        }
    
    def exec(self, params):
        """Search tasks."""
        if not params["query"]:
            return {"tasks": [], "query": ""}
        
        with DatabaseManager(params["db_path"]) as db:
            tasks = db.search_tasks(params["query"])
            
            return {
                "tasks": tasks,
                "query": params["query"],
                "count": len(tasks)
            }
    
    def post(self, shared, prep_res, exec_res):
        """Display search results."""
        shared["search_results"] = exec_res["tasks"]
        
        print(f"\n🔍 Search Results for '{exec_res['query']}':")
        print(f"Found {exec_res['count']} matching tasks")
        print("-" * 60)
        
        for task in exec_res["tasks"]:
            print(f"[{task['id']:3d}] {task['title']}")
            if task["description"]:
                print(f"      {task['description'][:60]}...")
        
        return None


class GenerateReportNode(Node):
    """Generate a task report."""
    
    def prep(self, shared):
        """Gather data for report."""
        return {
            "db_path": shared.get("db_info", {}).get("db_path", "tasks.db"),
            "stats": shared.get("task_stats"),
            "recent_tasks": shared.get("task_list", [])[:5]
        }
    
    def exec(self, data):
        """Generate report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "database": data["db_path"],
            "summary": data["stats"],
            "recent_tasks": data["recent_tasks"],
            "insights": []
        }
        
        # Generate insights
        stats = data["stats"]
        
        # Completion rate
        total = stats["total_tasks"]
        if total > 0:
            completed = stats["by_status"].get("completed", 0)
            completion_rate = (completed / total) * 100
            report["insights"].append(
                f"Completion rate: {completion_rate:.1f}% ({completed}/{total} tasks)"
            )
        
        # Priority distribution
        high_priority = sum(
            count for priority, count in stats["by_priority"].items() 
            if priority >= 4
        )
        if high_priority > 0:
            report["insights"].append(
                f"High priority tasks (P4-P5): {high_priority}"
            )
        
        # Overdue tasks
        if stats["overdue"] > 0:
            report["insights"].append(
                f"⚠️ {stats['overdue']} tasks are overdue!"
            )
        
        return report
    
    def post(self, shared, prep_res, exec_res):
        """Save and display report."""
        import json
        
        # Save report
        report_path = "task_report.json"
        with open(report_path, 'w') as f:
            json.dump(exec_res, f, indent=2)
        
        # Display report
        print("\n" + "=" * 60)
        print("📊 TASK MANAGEMENT REPORT")
        print("=" * 60)
        print(f"Generated: {exec_res['generated_at']}")
        print(f"Database: {exec_res['database']}")
        
        print("\n📈 Summary:")
        summary = exec_res["summary"]
        print(f"  Total tasks: {summary['total_tasks']}")
        for status, count in summary["by_status"].items():
            print(f"  - {status.capitalize()}: {count}")
        
        print("\n💡 Insights:")
        for insight in exec_res["insights"]:
            print(f"  • {insight}")
        
        print(f"\n📄 Full report saved to: {report_path}")
        
        shared["report"] = exec_res
        return None


def create_task_management_graph():
    """Create the task management graph."""
    # Create nodes
    init_db = InitDatabaseNode(node_id="init_db")
    create_task = CreateTaskNode(node_id="create_task")
    list_tasks = ListTasksNode(node_id="list_tasks")
    update_batch = UpdateTaskBatchNode(node_id="update_batch")
    search_tasks = SearchTasksNode(node_id="search_tasks")
    generate_report = GenerateReportNode(node_id="generate_report")
    
    # Connect nodes
    init_db >> create_task
    create_task >> ("list", list_tasks)
    create_task >> ("error", list_tasks)  # List anyway
    list_tasks >> update_batch
    update_batch >> search_tasks
    search_tasks >> generate_report
    
    return Graph(start=init_db)


def create_sample_tasks():
    """Create sample task data."""
    return [
        {
            "title": "Implement database integration",
            "description": "Add SQLite support to KayGraph examples",
            "priority": 5,
            "tags": ["development", "kaygraph"],
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        },
        {
            "title": "Write documentation",
            "description": "Document the database tool integration example",
            "priority": 4,
            "tags": ["documentation", "kaygraph"]
        },
        {
            "title": "Code review",
            "description": "Review pull requests for the project",
            "priority": 3,
            "tags": ["review", "collaboration"]
        },
        {
            "title": "Update dependencies",
            "description": "Check and update project dependencies",
            "priority": 2,
            "tags": ["maintenance"],
            "due_date": (datetime.now() - timedelta(days=2)).isoformat()  # Overdue
        },
        {
            "title": "Plan next sprint",
            "description": "Planning meeting for next development sprint",
            "priority": 4,
            "tags": ["planning", "meeting"],
            "due_date": (datetime.now() + timedelta(days=1)).isoformat()
        }
    ]


def main():
    """Run the database tool integration example."""
    print("🗄️  KayGraph Database Tool Integration")
    print("=" * 60)
    print("This example demonstrates SQLite database integration")
    print("for task management workflows.\n")
    
    # Create graph
    graph = create_task_management_graph()
    
    # Create sample tasks
    sample_tasks = create_sample_tasks()
    
    print(f"Creating {len(sample_tasks)} sample tasks...")
    
    # Process each task
    for i, task in enumerate(sample_tasks):
        print(f"\n--- Processing Task {i+1}/{len(sample_tasks)} ---")
        
        shared = {
            "db_path": "task_management.db",
            "reset_db": (i == 0),  # Reset on first task
            "new_task": task,
            "list_filters": {},
            "search_query": "project",
            "task_updates": []
        }
        
        # Run for this task
        graph.run(shared)
        
        # After first few tasks, add some updates
        if i == 2:
            shared["task_updates"] = [
                {"id": 1, "status": "in_progress"},
                {"id": 2, "status": "in_progress", "priority": 5}
            ]
    
    print("\n✨ Database integration example complete!")
    print("Database file: task_management.db")


if __name__ == "__main__":
    main()