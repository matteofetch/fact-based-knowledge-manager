"""
Hardcoded data for the initial testing phase.
This will be replaced with live API integrations later.
"""
from src.models import Fact, KnowledgeBase, SlackMessage
from src.supabase_service import SupabaseService
import csv
from pathlib import Path


def get_sample_slack_message() -> SlackMessage:
    """Returns a hardcoded sample Slack message with project metrics."""
    content = """Here's this week's Atlas update:
- 11,156 offers live (last: 11,287)  
- Restaurant coverage: 62.0% (last: 62.7%)
- Card capture rate: 53.8% (last: 54.1%)
- ARR: $8.7M (last: $8.5M)

Additional context: The slight decrease in offers is due to some restaurants temporarily opting out during the holiday season. We expect this to recover in the new year. The ARR increase is strong despite the slight dip in other metrics."""
    
    return SlackMessage(
        content=content,
        channel="#atlas-updates",
        user="project-manager"
    )


CSV_FALLBACK_PATH = Path(__file__).resolve().parent / "full-hardcoded-facts.csv"


def _local_facts():
    """Load fallback facts from `full-facts-temp.csv` so it stays in sync with Supabase."""
    if CSV_FALLBACK_PATH.exists():
        facts = []
        with open(CSV_FALLBACK_PATH, newline="", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            header_map = {
                "#": "number",
                "number": "number",
                "Fact": "description",
                "description": "description",
                "Time Last Validated": "last_validated",
                "last_validated": "last_validated",
            }
            for raw in reader:
                row = {header_map.get(k, k): v for k, v in raw.items()}
                try:
                    num = int(row["number"].strip())
                except Exception:
                    continue
                facts.append(
                    Fact(
                        number=num,
                        description=row["description"].strip(),
                        last_validated=row["last_validated"].strip(),
                    )
                )
        if facts:
            return facts
    # minimal fallback if CSV missing
    return [
        Fact(number=1, description="Fallback KB not available", last_validated="1970-01-01")
    ]


def get_current_knowledge_base() -> KnowledgeBase:
    """Fetch knowledge base from Supabase; fall back to local hardcoded copy."""
    from src.supabase_service import SupabaseService  # inline import

    sb = SupabaseService()
    kb = sb.fetch_knowledge_base()
    if kb:
        return kb

    # fallback
    return KnowledgeBase(title="Current RN Project Facts", facts=_local_facts())


def _local_guidelines() -> str:
    """Local fallback copy of the knowledge management guidelines."""
    return """# Knowledge Management Guidelines

## About This Knowledge Base
This is a fact-based knowledge management system for tracking project information. Each fact has a number, description, and validation date. The goal is maintaining accurate, current, and useful information that serves as a reliable source for answering operational questions.

## Core Principles

1. Operational Utility Focus
- Prioritize facts that help users understand current system operations over historical project details
- Ask: "Would this fact help someone understand how the system works today?"
- Keep historical context only when it explains current state or decisions

2. Temporal Clarity
- Distinguish between current operational facts ("X system processes Y") vs historical/planning facts ("Phase N aimed to achieve Y")
- Remove outdated project terminology from operational facts while preserving it in historical timeline facts
- Convert completed planning items from future tense ("will implement") to appropriate current state ("implemented" or "was planned")

3. Information Currency
- Update facts with current data when available (actual performance vs forecasts, current metrics vs estimates)
- Track validation dates - more recent validation indicates more reliable information
- Replace outdated targets/goals with current reality when projects are complete

4. Context Enhancement
- Add relevant context about why decisions were made, what problems were solved, or what challenges occurred
- This helps users understand not just what happened but why, making facts more actionable

## Fact Management Best Practices

Content Quality:
- Each fact should be specific, actionable, and contribute to system understanding
- Fact Completeness: Every fact must make sense as a standalone statement with sufficient context - avoid facts that require other facts to be understood
- Duplication Prevention: Always check existing facts before adding new content. Search for related concepts, similar metrics, or overlapping information to avoid creating duplicate or conflicting facts
- Objectivity Maintenance: Store only directly observable facts and measurable data. Facts must describe what happened, not what it means.

Prohibited content in facts:
- Interpretive language: "suggests," "indicates," "appears to show," "likely means," "may impact," "potential," "concerning trends"
- Analysis or conclusions: "churn problem," "performance challenges," "systematic issue"
- Speculation about causes: "due to," "because of," "resulting from" (unless directly confirmed)
- Future implications: "may lead to," "could result in," "risks causing"

Required approach: Record raw data points and measurements only. Save analysis, interpretation, causes, and implications for conversation or separate analysis sessions.

Examples:
- Good: "Card capture rate declined from 54.1% to 53.8% over two weeks"
- Bad: "Card capture rate declined from 54.1% to 53.8%, indicating a concerning trend"

- Eliminate redundancy through smart consolidation when multiple facts cover the same concept
- Keep facts separate when they address distinct aspects better understood individually

Language Standards:
- Use present tense for current operations ("system does X")
- Use past tense for completed project activities ("rollout completed in April")
- Avoid future tense unless describing confirmed future plans
- Update terminology consistently across related facts when changes occur

Structural Organization:
- Maintain consistent numbering even when deleting facts (gaps are acceptable)
- Update validation dates when facts are modified or confirmed
- Group related concepts logically while keeping individual facts atomic

## Document Integration Process
When incorporating new information from external documents:

1. Analysis Phase:
- Identify what information is new vs. confirms existing facts
- Note any contradictions or evolutions from current facts
- Distinguish project-relevant information from personal/task-specific details

2. Implementation:
- Update terminology consistently across all related facts
- Preserve valuable historical context that explains current decisions
- Track status evolution clearly (implemented vs. planned vs. historical)
- Use judgment to integrate information while maintaining fact completeness and context standards

## Knowledge Management Tasks System
- Proactively identify information gaps, outdated content, and improvement opportunities
- Prioritize high-impact updates (performance metrics, operational status) over lower-priority restructuring
- Use task tracking to manage ongoing knowledge base maintenance
- Filter out personal tasks that don't belong in shared knowledge management

## Decision-Making Framework
When uncertain about fact management decisions:
1. Utility Test: Does this change make the knowledge base more useful for current operations?
2. Clarity Test: Does this change make information clearer and more accessible?
3. Currency Test: Does this change improve information accuracy and timeliness?
4. Context Test: Does this change help users understand not just what but why?
5. Completeness Test: Can this fact be understood without requiring other facts for context?"""


def get_knowledge_guidelines() -> str:
    """Fetch guidelines from Supabase; fall back to local copy on failure."""
    sb = SupabaseService()
    supabase_copy = sb.fetch_guidelines()
    if supabase_copy:
        return supabase_copy
    return _local_guidelines() 