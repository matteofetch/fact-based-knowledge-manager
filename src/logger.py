"""
Comprehensive logging system for knowledge management processing.
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class KnowledgeLogger:
    """Logger specifically designed for knowledge management operations."""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.logs = []
        
    def _create_log_entry(self, level: LogLevel, message: str, extra_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a standardized log entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "message": message,
            "environment": self.environment
        }
        
        if extra_data:
            entry["data"] = extra_data
            
        return entry
    
    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log debug information."""
        entry = self._create_log_entry(LogLevel.DEBUG, message, extra_data)
        self.logs.append(entry)
        if self.environment == "development":
            print(f"[DEBUG] {message}")
            if extra_data:
                print(f"  Data: {json.dumps(extra_data, indent=2)}")
    
    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log general information."""
        entry = self._create_log_entry(LogLevel.INFO, message, extra_data)
        self.logs.append(entry)
        print(f"[INFO] {message}")
        if extra_data and self.environment == "development":
            print(f"  Data: {json.dumps(extra_data, indent=2)}")
    
    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log warning information."""
        entry = self._create_log_entry(LogLevel.WARNING, message, extra_data)
        self.logs.append(entry)
        print(f"[WARNING] {message}")
        if extra_data:
            print(f"  Data: {json.dumps(extra_data, indent=2)}")
    
    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log error information."""
        entry = self._create_log_entry(LogLevel.ERROR, message, extra_data)
        self.logs.append(entry)
        print(f"[ERROR] {message}")
        if extra_data:
            print(f"  Data: {json.dumps(extra_data, indent=2)}")
    
    def log_chatgpt_request(self, prompt: str, model: str, temperature: float = 0.1):
        """Log ChatGPT API request details."""
        self.info("Sending request to ChatGPT API", {
            "model": model,
            "temperature": temperature,
            "prompt_length": len(prompt),
            "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt
        })
        
        # Also log full prompt in debug mode
        self.debug("Full ChatGPT prompt", {"full_prompt": prompt})
    
    def log_chatgpt_response(self, response: str, usage_data: Optional[Dict[str, Any]] = None):
        """Log ChatGPT API response details."""
        self.info("Received response from ChatGPT API", {
            "response_length": len(response),
            "response_preview": response[:200] + "..." if len(response) > 200 else response,
            "usage": usage_data
        })
        
        # Also log full response in debug mode
        self.debug("Full ChatGPT response", {"full_response": response})
    
    def log_error_with_context(self, error: Exception, context: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log an error with additional context."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        if extra_data:
            error_data.update(extra_data)
            
        self.error(f"Error occurred: {str(error)}", error_data)
    
    def get_processing_summary(self) -> str:
        """Get a summary of all logs for this processing session."""
        if not self.logs:
            return "No logs recorded."
        
        summary = f"Processing completed with {len(self.logs)} log entries:\n"
        
        for log in self.logs:
            timestamp = log["timestamp"].split("T")[1][:8]  # Just time portion
            summary += f"[{timestamp}] {log['level']}: {log['message']}\n"
        
        return summary
    
    def export_logs(self) -> str:
        """Export all logs as JSON string."""
        return json.dumps(self.logs, indent=2) 