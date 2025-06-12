"""
Data models for the knowledge management system.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Fact(BaseModel):
    """Represents a single fact in the knowledge base."""
    number: int
    description: str
    last_validated: str  # ISO format date string
    
    def to_table_row(self) -> str:
        """Convert fact to markdown table row format."""
        return f"| **{self.number}** | {self.description} | {self.last_validated} |"


class KnowledgeBase(BaseModel):
    """Complete knowledge base with multiple facts."""
    title: str
    facts: List[Fact]
    
    def to_markdown(self) -> str:
        """Convert knowledge base to markdown format."""
        header = f"# {self.title}\n\n"
        table_header = "| **#** | **Fact** | **Time Last Validated** |\n"
        table_separator = "| ----- | -------- | ----------------------- |\n"
        
        fact_rows = "\n".join([fact.to_table_row() for fact in self.facts])
        
        return header + table_header + table_separator + fact_rows


class SlackMessage(BaseModel):
    """Represents a Slack message with project updates."""
    content: str
    timestamp: Optional[datetime] = None
    channel: Optional[str] = None
    user: Optional[str] = None


class ProcessingRequest(BaseModel):
    """Request payload for knowledge processing."""
    slack_message: SlackMessage
    current_knowledge_base: KnowledgeBase
    guidelines: str


class ProcessingResponse(BaseModel):
    """Response from knowledge processing."""
    updated_knowledge_base: KnowledgeBase
    processing_log: str
    success: bool
    error_message: Optional[str] = None


# ---------------------------------------------------------------------------
# Diff models
# ---------------------------------------------------------------------------


class KnowledgeBaseDiff(BaseModel):
    """Represents changes ChatGPT suggests to the knowledge base."""

    add: List[Fact] = []
    update: List[Fact] = []
    delete: List[int] = [] 