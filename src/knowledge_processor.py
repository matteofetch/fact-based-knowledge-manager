"""
Main knowledge processing service that orchestrates the entire flow.
"""
import os
from typing import Optional
from src.models import ProcessingRequest, ProcessingResponse, SlackMessage, KnowledgeBase
from src.chatgpt_service import ChatGPTService
from src.logger import KnowledgeLogger, LogLevel
from src.hardcoded_data import get_sample_slack_message, get_current_knowledge_base, get_knowledge_guidelines


class KnowledgeProcessor:
    """Main service for processing knowledge base updates."""
    
    def __init__(self, environment: str = None):
        # Initialize environment
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "development")
        
        # Initialize logger
        self.logger = KnowledgeLogger(environment)
        
        # Initialize ChatGPT service
        self.chatgpt_service = ChatGPTService(self.logger)
        
        self.logger.info("Knowledge processor initialized", {
            "environment": environment,
            "model": self.chatgpt_service.model
        })
    
    def process_hardcoded_flow(self) -> ProcessingResponse:
        """
        Execute the complete hardcoded flow for testing.
        This uses hardcoded data instead of live APIs.
        """
        self.logger.info("Starting hardcoded knowledge processing flow")
        
        try:
            # Step 1: Get hardcoded data
            self.logger.info("Loading hardcoded data")
            slack_message = get_sample_slack_message()
            current_knowledge_base = get_current_knowledge_base()
            guidelines = get_knowledge_guidelines()
            
            self.logger.info("Hardcoded data loaded successfully", {
                "slack_message_length": len(slack_message.content),
                "current_facts_count": len(current_knowledge_base.facts),
                "guidelines_length": len(guidelines)
            })
            
            # Step 2: Process the knowledge base update
            updated_knowledge_base = self.chatgpt_service.update_knowledge_base(
                slack_message=slack_message,
                current_knowledge_base=current_knowledge_base,
                guidelines=guidelines
            )
            
            if updated_knowledge_base is None:
                error_msg = "Failed to update knowledge base - ChatGPT service returned None"
                self.logger.error(error_msg)
                return ProcessingResponse(
                    updated_knowledge_base=current_knowledge_base,  # Return original as fallback
                    processing_log=self.logger.get_processing_summary(),
                    success=False,
                    error_message=error_msg
                )
            
            # Step 3: Log success and return
            self.logger.info("Knowledge processing flow completed successfully", {
                "original_facts_count": len(current_knowledge_base.facts),
                "updated_facts_count": len(updated_knowledge_base.facts),
                "facts_changed": len(updated_knowledge_base.facts) != len(current_knowledge_base.facts)
            })
            
            return ProcessingResponse(
                updated_knowledge_base=updated_knowledge_base,
                processing_log=self.logger.get_processing_summary(),
                success=True
            )
            
        except Exception as e:
            self.logger.log_error_with_context(e, "Hardcoded knowledge processing flow")
            return ProcessingResponse(
                updated_knowledge_base=get_current_knowledge_base(),  # Return original as fallback
                processing_log=self.logger.get_processing_summary(),
                success=False,
                error_message=f"Processing failed: {str(e)}"
            )
    
    def process_custom_input(self, request: ProcessingRequest) -> ProcessingResponse:
        """
        Process a custom knowledge update request.
        This will be used later when we have live API integrations.
        """
        self.logger.info("Starting custom knowledge processing flow")
        
        try:
            # Process the knowledge base update
            updated_knowledge_base = self.chatgpt_service.update_knowledge_base(
                slack_message=request.slack_message,
                current_knowledge_base=request.current_knowledge_base,
                guidelines=request.guidelines
            )
            
            if updated_knowledge_base is None:
                error_msg = "Failed to update knowledge base - ChatGPT service returned None"
                self.logger.error(error_msg)
                return ProcessingResponse(
                    updated_knowledge_base=request.current_knowledge_base,  # Return original as fallback
                    processing_log=self.logger.get_processing_summary(),
                    success=False,
                    error_message=error_msg
                )
            
            self.logger.info("Custom knowledge processing flow completed successfully")
            
            return ProcessingResponse(
                updated_knowledge_base=updated_knowledge_base,
                processing_log=self.logger.get_processing_summary(),
                success=True
            )
            
        except Exception as e:
            self.logger.log_error_with_context(e, "Custom knowledge processing flow")
            return ProcessingResponse(
                updated_knowledge_base=request.current_knowledge_base,  # Return original as fallback
                processing_log=self.logger.get_processing_summary(),
                success=False,
                error_message=f"Processing failed: {str(e)}"
            )
    
    def test_system_health(self) -> dict:
        """Test all system components and return health status."""
        self.logger.info("Testing system health")
        
        health_status = {
            "overall_status": "healthy",
            "components": {},
            "timestamp": self.logger._create_log_entry(LogLevel.INFO, "Health check")["timestamp"]
        }
        
        # Test ChatGPT API connection
        try:
            chatgpt_healthy = self.chatgpt_service.test_connection()
            health_status["components"]["chatgpt_api"] = {
                "status": "healthy" if chatgpt_healthy else "unhealthy",
                "details": "Connection successful" if chatgpt_healthy else "Connection failed"
            }
        except Exception as e:
            health_status["components"]["chatgpt_api"] = {
                "status": "unhealthy",
                "details": f"Error: {str(e)}"
            }
            health_status["overall_status"] = "degraded"
        
        # Test environment variables
        required_env_vars = ["OPENAI_API_KEY"]
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            health_status["components"]["environment"] = {
                "status": "unhealthy",
                "details": f"Missing environment variables: {', '.join(missing_vars)}"
            }
            health_status["overall_status"] = "unhealthy"
        else:
            health_status["components"]["environment"] = {
                "status": "healthy",
                "details": "All required environment variables present"
            }
        
        # Test hardcoded data loading
        try:
            slack_msg = get_sample_slack_message()
            kb = get_current_knowledge_base()
            guidelines = get_knowledge_guidelines()
            
            health_status["components"]["hardcoded_data"] = {
                "status": "healthy",
                "details": f"Loaded {len(kb.facts)} facts and {len(guidelines)} character guidelines"
            }
        except Exception as e:
            health_status["components"]["hardcoded_data"] = {
                "status": "unhealthy",
                "details": f"Failed to load hardcoded data: {str(e)}"
            }
            health_status["overall_status"] = "degraded"
        
        self.logger.info("System health check completed", {"status": health_status["overall_status"]})
        
        return health_status 