from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from knowledge_processor import KnowledgeProcessor
from models import SlackMessage, KnowledgeBase, Fact, ProcessingRequest
from hardcoded_data import get_current_knowledge_base, get_knowledge_guidelines


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function to ingest Slack messages via Zapier."""

    def _send_json_response(self, data: dict, status_code: int = 200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def _send_error(self, message: str, status_code: int = 400):
        self._send_json_response({"success": False, "error": message}, status_code)

    def do_OPTIONS(self):
        self._send_json_response({}, 200)

    def do_POST(self):
        # Validate request size
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_error("Empty request body", 400)
            return

        try:
            raw_body = self.rfile.read(content_length).decode('utf-8')
            body = json.loads(raw_body)
            # Zapier sometimes wraps request payloads in an array – unwrap when needed
            if isinstance(body, list):
                if len(body) == 0:
                    self._send_error("Empty JSON array received", 400)
                    return
                body = body[0]
        except json.JSONDecodeError:
            self._send_error("Invalid JSON payload", 400)
            return

        # Extract Slack message fields from the Zapier payload
        # Zapier can customize field names, but we assume a simple setup where
        # the outgoing JSON contains: { "text": "...", "channel": "...", "user": "..." }
        message_text = body.get('text') or body.get('message') or body.get('content')
        if not message_text:
            self._send_error("Missing Slack message text in payload", 400)
            return

        channel = body.get('channel')
        user = body.get('user') or body.get('username')

        # Build SlackMessage model
        slack_msg = SlackMessage(content=message_text, channel=channel, user=user)

        # Prepare current knowledge base and guidelines (placeholder until we add storage)
        current_kb: KnowledgeBase = get_current_knowledge_base()
        guidelines: str = get_knowledge_guidelines()

        # Build processing request
        processing_request = ProcessingRequest(
            slack_message=slack_msg,
            current_knowledge_base=current_kb,
            guidelines=guidelines
        )

        # Process update
        processor = KnowledgeProcessor()
        result = processor.process_custom_input(processing_request)

        # Build response
        response_data = {
            "success": result.success,
            "processing_log": result.processing_log,
            "updated_knowledge_base": {
                "title": result.updated_knowledge_base.title,
                "facts": [fact.dict() for fact in result.updated_knowledge_base.facts]
            },
            "updated_knowledge_base_markdown": result.updated_knowledge_base.to_markdown()
        }

        if result.error_message:
            response_data["error_message"] = result.error_message

        status = 200 if result.success else 500
        self._send_json_response(response_data, status) 