"""API endpoint for knowledge management tasks."""

import os
import sys
import json
import logging
from http.server import BaseHTTPRequestHandler

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from task_manager import TaskManager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to fetch tasks."""
        try:
            # Check for protection secret
            secret = self.headers.get('x-protection-secret')
            expected_secret = os.getenv('VERCEL_PROTECTION_SECRET')
            
            if expected_secret and secret != expected_secret:
                self._send_error(401, "Unauthorized")
                return

            # Parse query parameters
            path = self.path
            query_params = {}
            if '?' in path:
                path, query_string = path.split('?', 1)
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value

            task_manager = TaskManager()

            # Handle different endpoints
            if path == '/api/tasks' or path == '/api/tasks/':
                # Get all tasks
                tasks = task_manager.get_all_tasks()
                response_data = {
                    "success": True,
                    "tasks": tasks,
                    "count": len(tasks)
                }
            elif path == '/api/tasks/pending':
                # Get pending tasks
                tasks = task_manager.get_pending_tasks()
                response_data = {
                    "success": True,
                    "tasks": tasks,
                    "count": len(tasks)
                }
            elif path == '/api/tasks/summary':
                # Get task summary (logs to server)
                task_manager.log_task_summary()
                all_tasks = task_manager.get_all_tasks()
                
                # Build summary data
                status_counts = {}
                
                for task in all_tasks:
                    status = task.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                response_data = {
                    "success": True,
                    "summary": {
                        "total_tasks": len(all_tasks),
                        "status_breakdown": status_counts
                    }
                }
            else:
                self._send_error(404, "Endpoint not found")
                return

            # Send successful response
            self._send_json_response(response_data)

        except Exception as e:
            logger.error(f"Error in GET handler: {str(e)}")
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        """Handle POST requests to update task status."""
        try:
            # Check for protection secret
            secret = self.headers.get('x-protection-secret')
            expected_secret = os.getenv('VERCEL_PROTECTION_SECRET')
            
            if expected_secret and secret != expected_secret:
                self._send_error(401, "Unauthorized")
                return

            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self._send_error(400, "Invalid JSON in request body")
                return

            task_manager = TaskManager()
            
            # Handle different update operations
            action = data.get('action')
            task_id = data.get('task_id')
            
            if not task_id:
                self._send_error(400, "task_id is required")
                return
            
            if action == 'mark_in_progress':
                success = task_manager.mark_task_in_progress(task_id)
            elif action == 'mark_completed':
                success = task_manager.mark_task_completed(task_id)
            elif action == 'cancel':
                success = task_manager.cancel_task(task_id)
            else:
                self._send_error(400, f"Invalid action: {action}")
                return
            
            response_data = {
                "success": success,
                "message": f"Task {task_id} {action} {'successful' if success else 'failed'}"
            }
            
            self._send_json_response(response_data)

        except Exception as e:
            logger.error(f"Error in POST handler: {str(e)}")
            self._send_error(500, f"Internal server error: {str(e)}")

    def _send_json_response(self, data):
        """Send a JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-protection-secret')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def _send_error(self, status_code, message):
        """Send an error response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_data = {"success": False, "error": message}
        self.wfile.write(json.dumps(error_data, indent=2).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-protection-secret')
        self.end_headers() 