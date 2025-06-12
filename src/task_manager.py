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



    def mark_task_in_progress(self, task_id: int) -> bool:
        """Mark a task as in progress."""
        return self.supabase_service.update_task_status(task_id, "in_progress")

    def mark_task_completed(self, task_id: int) -> bool:
        """Mark a task as completed."""
        return self.supabase_service.update_task_status(task_id, "completed")

    def cancel_task(self, task_id: int) -> bool:
        """Cancel a task."""
        return self.supabase_service.update_task_status(task_id, "cancelled")

    def log_task_summary(self) -> None:
        """Log a summary of current tasks."""
        try:
            all_tasks = self.get_all_tasks()
            if not all_tasks:
                logger.info("No knowledge management tasks found")
                return

            # Count by status
            status_counts = {}

            for task in all_tasks:
                status = task.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1

            logger.info(
                f"Task Summary - Total: {len(all_tasks)}, "
                f"Status: {status_counts}"
            )

            # Log pending tasks
            pending_tasks = [
                task for task in all_tasks 
                if task.get("status") == "pending"
            ]
            
            if pending_tasks:
                logger.info(f"Pending tasks:")
                for task in pending_tasks:
                    logger.info(f"  - {task['title']}")

        except Exception as e:
            logger.error(f"Error logging task summary: {e}")

    def format_task_for_display(self, task: Dict[str, Any]) -> str:
        """Format a task dictionary for human-readable display."""
        return (
            f"ID: {task['id']}\n"
            f"Title: {task['title']}\n"
            f"Status: {task['status']}\n"
            f"Created: {task.get('created_at', 'Unknown')}\n"
        ) 