"""
Task generation service using ChatGPT to create new knowledge management tasks.
"""
import os
import json
from typing import List, Optional
from src.chatgpt_service import ChatGPTService
from src.logger import KnowledgeLogger
from src.hardcoded_data import get_current_knowledge_base, get_knowledge_guidelines
from src.supabase_service import SupabaseService


class TaskGenerator:
    """Service for generating knowledge management tasks using ChatGPT."""
    
    def __init__(self, logger: KnowledgeLogger):
        self.logger = logger
        self.chatgpt_service = ChatGPTService(logger)
        self.supabase_service = SupabaseService()
        
    def _create_task_generation_prompt(
        self, 
        knowledge_base_content: str, 
        guidelines: str, 
        existing_tasks: List[str]
    ) -> str:
        """Create the prompt for ChatGPT to generate new tasks."""
        existing_tasks_text = "\n".join([f"- {task}" for task in existing_tasks]) if existing_tasks else "No existing tasks"
        
        prompt = f"""You are a knowledge management task generator. Your job is to analyze a fact-based knowledge base and generate actionable tasks to improve and maintain it.

## INPUT INFORMATION

### Current Knowledge Base
{knowledge_base_content}

### Knowledge Management Guidelines
{guidelines}

### Existing Tasks
{existing_tasks_text}

## YOUR TASK

Based on the knowledge base and guidelines, generate 3-5 specific, actionable tasks that would improve the knowledge base. Focus on:

1. **Data Quality Issues**: Missing validation dates, outdated information, inconsistent terminology
2. **Information Gaps**: Areas where more detail would be valuable
3. **Organizational Improvements**: Better categorization, consolidation opportunities
4. **Content Updates**: Facts that may need verification or updating
5. **Compliance**: Ensuring facts follow the guidelines properly

## REQUIREMENTS

- Each task should be specific and actionable
- Don't duplicate existing tasks
- Focus on high-impact improvements
- Tasks should be doable within a reasonable timeframe
- Prioritize operational utility and information currency

## OUTPUT FORMAT

Respond with ONLY a JSON array of task strings. No additional text, explanations, or formatting.

Example format:
["Task 1 description", "Task 2 description", "Task 3 description"]

Do not include any explanation or additional text outside the JSON array."""

        return prompt
    
    def _analyze_if_task_needs_human(self, task: str) -> bool:
        """Analyze a task to determine if it needs human input.
        
        Returns True if the task requires human judgment, external data, or decisions.
        Returns False if it can be executed automatically using available data.
        """
        task_lower = task.lower()
        
        # Keywords that typically indicate human input needed
        human_needed_keywords = [
            "clarify", "confirm", "verify with", "ask", "check with",
            "review with", "validate with", "coordinate with",
            "decision", "approve", "priority", "stakeholder",
            "external", "contact", "reach out", "interview",
            "survey", "gather feedback", "meeting", "discussion",
            "strategic", "business judgment", "policy",
            "manual review", "human verification"
        ]
        
        # Keywords that typically indicate automated execution possible
        automated_keywords = [
            "update", "merge", "consolidate", "audit", "scan",
            "refresh", "revise", "archive", "validate dates",
            "check existing", "review facts", "update validation",
            "remove duplicate", "fix", "correct", "standardize"
        ]
        
        # Check for human-needed indicators
        for keyword in human_needed_keywords:
            if keyword in task_lower:
                return True
        
        # If it's purely about updating existing data/facts, likely automated
        for keyword in automated_keywords:
            if keyword in task_lower:
                # Check if it's just updating existing knowledge base data
                if any(indicator in task_lower for indicator in ["facts", "knowledge base", "validation", "data"]):
                    return False
        
        # Default to needing human input for safety
        return True
    
    def _parse_task_response(self, response: str) -> List[str]:
        """Parse ChatGPT response into a list of tasks."""
        try:
            # Clean the response by removing any markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            tasks = json.loads(cleaned_response)
            
            if not isinstance(tasks, list):
                self.logger.warning("ChatGPT response is not a list", {"response": response})
                return []
                
            # Validate each task is a string
            valid_tasks = []
            for task in tasks:
                if isinstance(task, str) and task.strip():
                    valid_tasks.append(task.strip())
                else:
                    self.logger.warning(f"Invalid task format: {task}")
                    
            self.logger.info(f"Successfully parsed {len(valid_tasks)} tasks from ChatGPT response")
            return valid_tasks
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse ChatGPT response as JSON: {e}", {"response": response})
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error parsing tasks: {e}", {"response": response})
            return []
    
    def generate_tasks(self) -> Optional[List[str]]:
        """
        Generate new knowledge management tasks using ChatGPT.
        Returns list of task strings, or None if an error occurs.
        """
        try:
            self.logger.info("Starting task generation process")
            
            # Get current knowledge base
            knowledge_base = get_current_knowledge_base()
            if not knowledge_base:
                self.logger.error("Failed to load current knowledge base")
                return None
                
            # Get guidelines
            guidelines = get_knowledge_guidelines()
            if not guidelines:
                self.logger.error("Failed to load knowledge guidelines")
                return None
                
            # Get existing tasks from database
            existing_tasks = self.supabase_service.fetch_tasks()
            
            self.logger.info("Loaded data for task generation", {
                "facts_count": len(knowledge_base.facts),
                "guidelines_length": len(guidelines),
                "existing_tasks_count": len(existing_tasks)
            })
            
            # Create the prompt
            prompt = self._create_task_generation_prompt(
                knowledge_base.to_markdown(),
                guidelines,
                existing_tasks
            )
            
            # Log the request
            self.logger.log_chatgpt_request(prompt, self.chatgpt_service.model, 0.0)
            
            # Make the API call
            if self.chatgpt_service.model.startswith("o1") or self.chatgpt_service.model.startswith("o3"):
                response = self.chatgpt_service.client.chat.completions.create(
                    model=self.chatgpt_service.model,
                    messages=[
                        {"role": "user", "content": f"You are a knowledge management task generator. Follow instructions exactly.\n\n{prompt}"}
                    ],
                    max_completion_tokens=2000
                )
            else:
                response = self.chatgpt_service.client.chat.completions.create(
                    model=self.chatgpt_service.model,
                    messages=[
                        {"role": "system", "content": "You are a knowledge management task generator. Follow instructions exactly."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
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
            
            # Parse the response into tasks
            tasks = self._parse_task_response(response_content)
            
            if not tasks:
                self.logger.warning("No valid tasks generated from ChatGPT response")
                return []
                
            self.logger.info(f"Successfully generated {len(tasks)} new tasks")
            return tasks
            
        except Exception as e:
            self.logger.log_error_with_context(e, "Task generation", {
                "model": self.chatgpt_service.model
            })
            return None
    
    def generate_and_store_tasks(self) -> dict:
        """
        Generate new tasks and store them in the database.
        Returns a summary of the operation.
        """
        try:
            # Generate tasks
            new_tasks = self.generate_tasks()
            
            if new_tasks is None:
                return {
                    "success": False,
                    "error": "Failed to generate tasks",
                    "tasks_generated": 0,
                    "tasks_stored": 0
                }
                
            if not new_tasks:
                return {
                    "success": True,
                    "message": "No new tasks generated",
                    "tasks_generated": 0,
                    "tasks_stored": 0
                }
            
            # Store tasks in database
            stored_count = 0
            for task in new_tasks:
                needs_human = self._analyze_if_task_needs_human(task)
                success = self.supabase_service.add_task(task, needs_human)
                if success:
                    stored_count += 1
                    self.logger.info(f"Stored task (needs_human={needs_human}): {task[:50]}...")
                else:
                    self.logger.warning(f"Failed to store task: {task}")
            
            self.logger.info(f"Task generation complete: {len(new_tasks)} generated, {stored_count} stored")
            
            return {
                "success": True,
                "message": f"Successfully generated and stored {stored_count} tasks",
                "tasks_generated": len(new_tasks),
                "tasks_stored": stored_count,
                "new_tasks": new_tasks
            }
            
        except Exception as e:
            self.logger.log_error_with_context(e, "Task generation and storage")
            return {
                "success": False,
                "error": f"Error during task generation: {str(e)}",
                "tasks_generated": 0,
                "tasks_stored": 0
            } 