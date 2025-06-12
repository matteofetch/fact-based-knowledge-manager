"""Task Manager for knowledge management tasks."""

import logging
from typing import List, Dict, Any, Optional
from src.supabase_service import SupabaseService


logger = logging.getLogger(__name__)


class TaskManager:
    """Manages knowledge management tasks from Supabase."""

    def __init__(self):
        self.supabase_service = SupabaseService()

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all knowledge management tasks."""
        return self.supabase_service.fetch_knowledge_management_tasks()

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks, ordered by priority."""
        return self.supabase_service.get_pending_tasks()

    def get_high_priority_tasks(self) -> List[Dict[str, Any]]:
        """Get all high priority and urgent tasks."""
        return self.supabase_service.get_high_priority_tasks()

    def get_automated_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that don't require human input and are pending."""
        tasks = self.get_pending_tasks()
        return [task for task in tasks if not task.get("requires_human_input", False)]

    def get_human_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that require human input and are pending."""
        tasks = self.get_pending_tasks()
        return [task for task in tasks if task.get("requires_human_input", False)]

    def mark_task_in_progress(self, task_id: int) -> bool:
        """Mark a task as in progress."""
        return self.supabase_service.update_task_status(task_id, "in_progress")

    def mark_task_completed(self, task_id: int, completion_notes: Optional[str] = None) -> bool:
        """Mark a task as completed with optional notes."""
        return self.supabase_service.update_task_status(task_id, "completed", completion_notes)

    def cancel_task(self, task_id: int, reason: Optional[str] = None) -> bool:
        """Cancel a task with optional reason."""
        return self.supabase_service.update_task_status(task_id, "cancelled", reason)

    def log_task_summary(self) -> None:
        """Log a summary of current tasks."""
        try:
            all_tasks = self.get_all_tasks()
            if not all_tasks:
                logger.info("No knowledge management tasks found")
                return

            # Count by status
            status_counts = {}
            priority_counts = {}
            type_counts = {}

            for task in all_tasks:
                status = task.get("status", "unknown")
                priority = task.get("priority", "unknown")
                task_type = task.get("task_type", "unknown")

                status_counts[status] = status_counts.get(status, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                type_counts[task_type] = type_counts.get(task_type, 0) + 1

            logger.info(
                f"Task Summary - Total: {len(all_tasks)}, "
                f"Status: {status_counts}, "
                f"Priority: {priority_counts}, "
                f"Types: {type_counts}"
            )

            # Log pending high-priority tasks
            pending_high_priority = [
                task for task in all_tasks 
                if task.get("status") == "pending" and task.get("priority") in ["high", "urgent"]
            ]
            
            if pending_high_priority:
                logger.info(f"High-priority pending tasks:")
                for task in pending_high_priority:
                    logger.info(f"  - [{task['priority'].upper()}] {task['title']}")

        except Exception as e:
            logger.error(f"Error logging task summary: {e}")

    def format_task_for_display(self, task: Dict[str, Any]) -> str:
        """Format a task dictionary for human-readable display."""
        return (
            f"ID: {task['id']}\n"
            f"Title: {task['title']}\n"
            f"Description: {task['description']}\n"
            f"Status: {task['status']}\n"
            f"Priority: {task['priority']}\n"
            f"Type: {task['task_type']}\n"
            f"Requires Human: {task.get('requires_human_input', False)}\n"
            f"Assigned To: {task.get('assigned_to', 'Unassigned')}\n"
            f"Created: {task.get('created_at', 'Unknown')}\n"
            f"Due Date: {task.get('due_date', 'None')}\n"
        ) 