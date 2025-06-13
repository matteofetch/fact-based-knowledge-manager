"""
Task execution service for automated knowledge management tasks.
"""
import os
import json
from typing import List, Optional, Dict, Any
from src.chatgpt_service import ChatGPTService
from src.logger import KnowledgeLogger
from src.hardcoded_data import get_current_knowledge_base, get_knowledge_guidelines
from src.supabase_service import SupabaseService
from src.models import KnowledgeBase


class TaskExecutor:
    """Service for executing automated knowledge management tasks using ChatGPT."""
    
    def __init__(self, logger: KnowledgeLogger):
        self.logger = logger
        self.chatgpt_service = ChatGPTService(logger)
        self.supabase_service = SupabaseService()
        
    def _create_task_execution_prompt(
        self, 
        knowledge_base_content: str, 
        guidelines: str, 
        tasks_to_execute: List[str]
    ) -> str:
        """Create the prompt for ChatGPT to execute tasks and update the knowledge base."""
        tasks_text = "\n".join([f"- {task}" for task in tasks_to_execute])
        
        prompt = f"""You are a fact-based knowledge management system. Your task is to execute specific knowledge management tasks by updating the knowledge base according to the guidelines.

## INPUT INFORMATION

### Current Knowledge Base
{knowledge_base_content}

### Knowledge Management Guidelines
{guidelines}

### Tasks to Execute
{tasks_text}

## YOUR TASK

Execute each of the listed tasks by updating the knowledge base accordingly. For each task:

1. **Analyze what the task requires** - understand what changes need to be made
2. **Apply the changes** - update existing facts, merge duplicates, refresh data, fix issues, etc.
3. **Follow all guidelines** especially regarding objectivity, temporal clarity, and fact completeness
4. **Update validation dates** to today's date (2025-01-15) for any facts you modify or confirm
5. **Maintain fact numbering** - use existing numbers for updated facts, reuse numbers when merging facts

## EXECUTION GUIDELINES

- **For consolidation tasks**: Merge duplicate facts into the most comprehensive version, retire redundant ones
- **For validation tasks**: Update validation dates for facts that are confirmed as current
- **For refresh tasks**: Update metrics and data with the most recent available information
- **For audit tasks**: Review and fix language, formatting, or compliance issues
- **For organization tasks**: Improve structure while maintaining content integrity

## OUTPUT FORMAT

Respond with ONLY a properly formatted markdown table of the updated knowledge base, following this exact format:

# Current RN Project Facts

| **#** | **Fact** | **Time Last Validated** |
| ----- | -------- | ----------------------- |
| **1** | [Fact description] | [YYYY-MM-DD] |
| **2** | [Fact description] | [YYYY-MM-DD] |

Do not include any explanation, analysis, or additional text. Only return the updated knowledge base table."""

        return prompt
    
    def execute_automated_tasks(self) -> Dict[str, Any]:
        """
        Execute all automated tasks that don't require human input.
        Returns a summary of the execution results.
        """
        try:
            self.logger.info("Starting automated task execution process")
            
            # Get automated tasks
            automated_tasks = self.supabase_service.fetch_automated_tasks()
            
            if not automated_tasks:
                return {
                    "success": True,
                    "message": "No automated tasks to execute",
                    "tasks_executed": 0,
                    "tasks_completed": 0,
                    "knowledge_base_updated": False
                }
            
            task_titles = [task["title"] for task in automated_tasks]
            self.logger.info(f"Found {len(automated_tasks)} automated tasks to execute")
            
            # Get current knowledge base
            knowledge_base = get_current_knowledge_base()
            if not knowledge_base:
                self.logger.error("Failed to load current knowledge base")
                return {
                    "success": False,
                    "error": "Failed to load current knowledge base",
                    "tasks_executed": 0,
                    "tasks_completed": 0
                }
                
            # Get guidelines
            guidelines = get_knowledge_guidelines()
            if not guidelines:
                self.logger.error("Failed to load knowledge guidelines")
                return {
                    "success": False,
                    "error": "Failed to load knowledge guidelines",
                    "tasks_executed": 0,
                    "tasks_completed": 0
                }
            
            self.logger.info("Loaded data for task execution", {
                "facts_count": len(knowledge_base.facts),
                "guidelines_length": len(guidelines),
                "tasks_count": len(automated_tasks)
            })
            
            # Create the execution prompt
            prompt = self._create_task_execution_prompt(
                knowledge_base.to_markdown(),
                guidelines,
                task_titles
            )
            
            # Log the request
            self.logger.log_chatgpt_request(prompt, self.chatgpt_service.model, 0.0)
            
            # Make the API call to execute tasks
            if self.chatgpt_service.model.startswith("o1") or self.chatgpt_service.model.startswith("o3"):
                response = self.chatgpt_service.client.chat.completions.create(
                    model=self.chatgpt_service.model,
                    messages=[
                        {"role": "user", "content": f"You are a precise fact-based knowledge management system. Execute the tasks exactly as specified.\n\n{prompt}"}
                    ],
                    max_completion_tokens=4000
                )
            else:
                response = self.chatgpt_service.client.chat.completions.create(
                    model=self.chatgpt_service.model,
                    messages=[
                        {"role": "system", "content": "You are a precise fact-based knowledge management system. Execute the tasks exactly as specified."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4000
                )
            
            # Extract response content and usage data
            response_content = response.choices[0].message.content
            usage_data = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # Log the response
            self.logger.log_chatgpt_response(response_content, usage_data)
            
            # Parse the response into an updated knowledge base
            updated_knowledge_base = self.chatgpt_service._parse_knowledge_base_response(response_content)
            
            if not updated_knowledge_base or not updated_knowledge_base.facts:
                self.logger.error("Failed to parse updated knowledge base from ChatGPT response")
                return {
                    "success": False,
                    "error": "Failed to parse updated knowledge base",
                    "tasks_executed": len(automated_tasks),
                    "tasks_completed": 0
                }
            
            # Update Supabase with the new knowledge base
            update_success = self.supabase_service.upsert_knowledge_base(updated_knowledge_base)
            
            if not update_success:
                self.logger.error("Failed to update knowledge base in Supabase")
                return {
                    "success": False,
                    "error": "Failed to update knowledge base in Supabase",
                    "tasks_executed": len(automated_tasks),
                    "tasks_completed": 0
                }
            
            # Remove completed tasks
            completed_count = 0
            for task in automated_tasks:
                if self.supabase_service.delete_task(task["id"]):
                    completed_count += 1
                    self.logger.info(f"Deleted completed task: {task['title'][:50]}...")
                else:
                    self.logger.warning(f"Failed to delete task {task['id']}: {task['title'][:50]}...")
            
            self.logger.info(f"Task execution complete: {len(automated_tasks)} executed, {completed_count} removed, knowledge base updated")
            
            return {
                "success": True,
                "message": f"Successfully executed {len(automated_tasks)} automated tasks",
                "tasks_executed": len(automated_tasks),
                "tasks_completed": completed_count,
                "knowledge_base_updated": True,
                "facts_count": len(updated_knowledge_base.facts),
                "executed_tasks": task_titles
            }
            
        except Exception as e:
            self.logger.log_error_with_context(e, "Automated task execution", {
                "model": self.chatgpt_service.model
            })
            return {
                "success": False,
                "error": f"Error during task execution: {str(e)}",
                "tasks_executed": 0,
                "tasks_completed": 0
            } 