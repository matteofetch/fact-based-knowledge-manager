"""
Vercel serverless function for knowledge base processing.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add the src directory to the Python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from knowledge_processor import KnowledgeProcessor
from models import ProcessingRequest, SlackMessage, KnowledgeBase, Fact


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""
    
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
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        action = query_params.get('action', [None])[0]
        
        try:
            if not action:
                # Base API endpoint
                self._send_json_response({
                    "service": "Fact-based Knowledge Manager",
                    "version": "1.0.0",
                    "status": "active",
                    "endpoints": {
                        "GET /api/process": "API information (this endpoint)",
                        "POST /api/process?action=hardcoded": "Run hardcoded knowledge processing flow",
                        "GET /api/process?action=health": "System health check",
                        "POST /api/process?action=custom": "Process custom knowledge update request"
                    },
                    "environment": os.getenv("ENVIRONMENT", "production")
                })
                
            elif action == 'health':
                # Health check endpoint
                processor = KnowledgeProcessor()
                health_status = processor.test_system_health()
                
                status_code = 200 if health_status["overall_status"] == "healthy" else 503
                self._send_json_response(health_status, status_code)
                
            else:
                self._send_error_response("Invalid action parameter", 400)
                
        except Exception as e:
            self._send_error_response(f"Server error: {str(e)}", 500)
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        action = query_params.get('action', [None])[0]
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = ""
            if content_length > 0:
                request_body = self.rfile.read(content_length).decode('utf-8')
            
            if action == 'hardcoded':
                # Run hardcoded processing flow
                processor = KnowledgeProcessor()
                result = processor.process_hardcoded_flow()
                
                # Convert result to dictionary
                response_data = {
                    "success": result.success,
                    "processing_log": result.processing_log,
                    "updated_knowledge_base": {
                        "title": result.updated_knowledge_base.title,
                        "facts": [
                            {
                                "number": fact.number,
                                "description": fact.description,
                                "last_validated": fact.last_validated
                            }
                            for fact in result.updated_knowledge_base.facts
                        ]
                    },
                    "updated_knowledge_base_markdown": result.updated_knowledge_base.to_markdown()
                }
                
                if result.error_message:
                    response_data["error_message"] = result.error_message
                
                status_code = 200 if result.success else 500
                self._send_json_response(response_data, status_code)
                
            elif action == 'custom':
                # Process custom request
                if not request_body:
                    self._send_error_response("Request body is required", 400)
                    return
                
                try:
                    request_data = json.loads(request_body)
                    
                    # Parse the request data into our models
                    slack_message = SlackMessage(
                        content=request_data["slack_message"]["content"],
                        channel=request_data["slack_message"].get("channel"),
                        user=request_data["slack_message"].get("user")
                    )
                    
                    # Parse facts
                    facts = []
                    for fact_data in request_data["current_knowledge_base"]["facts"]:
                        fact = Fact(
                            number=fact_data["number"],
                            description=fact_data["description"],
                            last_validated=fact_data["last_validated"]
                        )
                        facts.append(fact)
                    
                    knowledge_base = KnowledgeBase(
                        title=request_data["current_knowledge_base"]["title"],
                        facts=facts
                    )
                    
                    processing_request = ProcessingRequest(
                        slack_message=slack_message,
                        current_knowledge_base=knowledge_base,
                        guidelines=request_data["guidelines"]
                    )
                    
                    # Process the request
                    processor = KnowledgeProcessor()
                    result = processor.process_custom_input(processing_request)
                    
                    # Convert result to dictionary
                    response_data = {
                        "success": result.success,
                        "processing_log": result.processing_log,
                        "updated_knowledge_base": {
                            "title": result.updated_knowledge_base.title,
                            "facts": [
                                {
                                    "number": fact.number,
                                    "description": fact.description,
                                    "last_validated": fact.last_validated
                                }
                                for fact in result.updated_knowledge_base.facts
                            ]
                        },
                        "updated_knowledge_base_markdown": result.updated_knowledge_base.to_markdown()
                    }
                    
                    if result.error_message:
                        response_data["error_message"] = result.error_message
                    
                    status_code = 200 if result.success else 500
                    self._send_json_response(response_data, status_code)
                    
                except json.JSONDecodeError:
                    self._send_error_response("Invalid JSON in request body", 400)
                except KeyError as e:
                    self._send_error_response(f"Missing required field: {str(e)}", 400)
                except Exception as e:
                    self._send_error_response(f"Error processing request: {str(e)}", 500)
                
            else:
                self._send_error_response("Missing or invalid action parameter", 400)
                
        except Exception as e:
            self._send_error_response(f"Server error: {str(e)}", 500) 