"""
ChatGPT API service for knowledge base processing.
"""
import os
import json
from typing import Optional
from openai import OpenAI
from src.models import KnowledgeBase, SlackMessage, Fact
from src.logger import KnowledgeLogger


class ChatGPTService:
    """Service for interacting with ChatGPT API for knowledge base updates."""
    
    def __init__(self, logger: KnowledgeLogger):
        self.logger = logger
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # Switch to gpt-4o for reliable knowledge processing
        self.temperature = 0.1  # Low temperature for consistent, factual responses
        
    def _create_knowledge_update_prompt(
        self, 
        slack_message: SlackMessage, 
        current_knowledge_base: KnowledgeBase, 
        guidelines: str
    ) -> str:
        """Create the prompt for ChatGPT to update the knowledge base."""
        prompt = f"""You are a fact-based knowledge management system. Your task is to update a knowledge base based on new information from a Slack message, following specific guidelines.

## INPUT INFORMATION

### Current Knowledge Base
{current_knowledge_base.to_markdown()}

### New Information from Slack
Channel: {slack_message.channel or "Unknown"}
User: {slack_message.user or "Unknown"}
Message:
{slack_message.content}

### Knowledge Management Guidelines
{guidelines}

## YOUR TASK

Analyze the Slack message and update the knowledge base according to the guidelines. You should:

1. **Update existing facts** with new data where applicable (especially metrics and current status)
2. **Add new facts** if the Slack message contains information not covered in existing facts
3. **Update validation dates** to today's date (2025-01-15) for any facts you modify or confirm
4. **Maintain fact numbering** - use existing numbers for updated facts, assign new numbers for new facts
5. **Follow all guidelines** especially regarding objectivity, temporal clarity, and fact completeness

## OUTPUT FORMAT

Respond with ONLY a properly formatted markdown table of the updated knowledge base, following this exact format:

# Current RN Project Facts

| **#** | **Fact** | **Time Last Validated** |
| ----- | -------- | ----------------------- |
| **1** | [Fact description] | [YYYY-MM-DD] |
| **2** | [Fact description] | [YYYY-MM-DD] |

Do not include any explanation, analysis, or additional text. Only return the updated knowledge base table."""

        return prompt
    
    def _parse_knowledge_base_response(self, response: str) -> KnowledgeBase:
        """Parse ChatGPT response back into a KnowledgeBase object."""
        self.logger.debug("Parsing ChatGPT response into knowledge base structure")
        
        lines = response.strip().split('\n')
        facts = []
        
        # Find the title
        title = "Current RN Project Facts"  # Default
        for line in lines:
            if line.startswith('#') and not line.startswith('##'):
                title = line.strip('# ').strip()
                break
        
        # Parse the table rows
        in_table = False
        for line in lines:
            line = line.strip()
            
            # Skip header and separator rows
            if line.startswith('| **#**') or line.startswith('| -----'):
                in_table = True
                continue
                
            # Parse fact rows
            if in_table and line.startswith('| **') and line.endswith(' |'):
                try:
                    # Split by | and clean up
                    parts = [part.strip() for part in line.split('|')[1:-1]]  # Remove empty first/last
                    if len(parts) >= 3:
                        # Extract fact number (remove ** formatting)
                        number_str = parts[0].replace('**', '').strip()
                        number = int(number_str)
                        
                        # Extract description and validation date
                        description = parts[1].strip()
                        last_validated = parts[2].strip()
                        
                        fact = Fact(
                            number=number,
                            description=description,
                            last_validated=last_validated
                        )
                        facts.append(fact)
                        
                        self.logger.debug(f"Parsed fact #{number}: {description[:50]}...")
                        
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Failed to parse table row: {line}", {"error": str(e)})
                    continue
        
        self.logger.info(f"Successfully parsed {len(facts)} facts from ChatGPT response")
        
        return KnowledgeBase(title=title, facts=facts)
    
    def update_knowledge_base(
        self, 
        slack_message: SlackMessage, 
        current_knowledge_base: KnowledgeBase, 
        guidelines: str
    ) -> Optional[KnowledgeBase]:
        """
        Send knowledge base update request to ChatGPT and return updated knowledge base.
        Returns None if an error occurs.
        """
        try:
            self.logger.info("Starting knowledge base update process")
            
            # Create the prompt
            prompt = self._create_knowledge_update_prompt(slack_message, current_knowledge_base, guidelines)
            
            # Log the request
            self.logger.log_chatgpt_request(prompt, self.model, self.temperature or 0.0)
            
            # Make the API call
            # Note: o1 models don't support system messages or temperature
            if self.model.startswith("o1"):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": f"You are a precise fact-based knowledge management system. Follow instructions exactly.\n\n{prompt}"}
                    ],
                    max_completion_tokens=4000
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise fact-based knowledge management system. Follow instructions exactly."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
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
            
            # Parse the response into a knowledge base
            updated_knowledge_base = self._parse_knowledge_base_response(response_content)
            
            self.logger.info(f"Successfully updated knowledge base with {len(updated_knowledge_base.facts)} facts")
            
            return updated_knowledge_base
            
        except Exception as e:
            self.logger.log_error_with_context(e, "ChatGPT API call for knowledge base update", {
                "slack_message_content": slack_message.content[:100] + "..." if len(slack_message.content) > 100 else slack_message.content,
                "current_facts_count": len(current_knowledge_base.facts)
            })
            return None
    
    def test_connection(self) -> bool:
        """Test if ChatGPT API connection is working."""
        try:
            self.logger.info("Testing ChatGPT API connection")
            
            # Simple test message for connection
            test_content = "Hello, please respond with 'Connection successful'"
            
            if self.model.startswith("o1"):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": test_content}],
                    max_completion_tokens=50  # o1 models need more tokens for reasoning
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": test_content}],
                    max_tokens=10
                )
            
            response_content = response.choices[0].message.content
            success = "Connection successful" in response_content or "successful" in response_content.lower()
            
            if success:
                self.logger.info("ChatGPT API connection test successful")
            else:
                self.logger.warning("ChatGPT API connection test returned unexpected response", {"response": response_content})
                
            return success
            
        except Exception as e:
            self.logger.log_error_with_context(e, "ChatGPT API connection test")
            return False 