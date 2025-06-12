"""
Vercel serverless function for task generation.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add the src directory to the Python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from task_generator import TaskGenerator
from logger import KnowledgeLogger


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for task generation."""
    
    def _send_json_response(self, data: dict, status_code: int = 200):
        """Send a JSON response with proper headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response_body = json.dumps(data, indent=2)
        self.wfile.write(response_body.encode('utf-8'))
    
    def _send_error_response(self, message: str, status_code: int = 500):
        """Send an error response."""
        error_data = {
            "success": False,
            "error": message,
            "timestamp": "2025-01-15T12:00:00Z"
        }
        self._send_json_response(error_data, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self._send_json_response({}, 200)
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            # API information endpoint
            self._send_json_response({
                "service": "Task Generation API",
                "version": "1.0.0",
                "status": "active",
                "endpoints": {
                    "GET /api/generate-tasks": "API information (this endpoint)",
                    "POST /api/generate-tasks": "Generate new knowledge management tasks using ChatGPT"
                },
                "description": "POST to this endpoint to trigger ChatGPT-based task generation",
                "environment": os.getenv("ENVIRONMENT", "production")
            })
            
        except Exception as e:
            self._send_error_response(f"Server error: {str(e)}", 500)
    
    def do_POST(self):
        """Handle POST requests to generate tasks."""
        try:
            # Initialize logger and task generator
            environment = os.getenv("ENVIRONMENT", "production")
            logger = KnowledgeLogger(environment)
            task_generator = TaskGenerator(logger)
            
            logger.info("Task generation API called")
            
            # Generate and store tasks
            result = task_generator.generate_and_store_tasks()
            
            # Prepare response
            response_data = {
                "service": "Task Generation API",
                "timestamp": "2025-01-15T12:00:00Z",
                **result
            }
            
            # Add processing log for debugging
            response_data["processing_log"] = logger.get_processing_summary()
            
            status_code = 200 if result["success"] else 500
            self._send_json_response(response_data, status_code)
            
        except Exception as e:
            self._send_error_response(f"Server error during task generation: {str(e)}", 500) 