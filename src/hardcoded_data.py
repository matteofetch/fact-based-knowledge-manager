"""
Hardcoded data for the initial testing phase.
This will be replaced with live API integrations later.
"""
from src.models import Fact, KnowledgeBase, SlackMessage


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


def get_current_knowledge_base() -> KnowledgeBase:
    """Returns the hardcoded current knowledge base."""
    facts = [
        Fact(
            number=1,
            description="Rewards Network (RN) is a network of ~18 000 local restaurants whose receipts earn a %-back reward and will be ingested as regular Fetch offers.",
            last_validated="2025-04-15"
        ),
        Fact(
            number=2,
            description="RN integration currently has ~11,287 live offers (scaled from initial 140), with location matching and credit card capture issues having limited the rollout from the planned 14 400.",
            last_validated="2025-06-11"
        ),
        Fact(
            number=6,
            description="Key results include generating $10.6 M ARR by EOQ2 2025 and $11.6 M revenue in FY25. Current ARR is $8.7M as of June 2025.",
            last_validated="2025-06-11"
        ),
        Fact(
            number=7,
            description="Target is 90% of restaurants in-app by end of year. Current coverage is 62.0%.",
            last_validated="2025-06-11"
        ),
        Fact(
            number=8,
            description="Card-info capture goals rise to 65% of receipts in H1 and 80% in H2. Current capture rate is 53.8%.",
            last_validated="2025-06-11"
        ),
        Fact(
            number=22,
            description="Payment capture feature tooling code is complete but not yet released; will reduce support lift once deployed.",
            last_validated="2025-06-11"
        ),
        Fact(
            number=31,
            description="Payment capture feature has two components: rescan prompt (backend in review, mobile complete) and manual card input with cross-referencing validation (postponed while ChatGPT API improvements are in progress).",
            last_validated="2025-06-11"
        ),
        Fact(
            number=51,
            description="Current RN restaurant coverage is 62.0% with 11,287 active offers out of 18,000 possible restaurants in the network.",
            last_validated="2025-06-11"
        ),
        Fact(
            number=55,
            description="Payment capture feature was approved in March 2025 following a stakeholder presentation that addressed feature-risk concerns; a comprehensive risk analysis projected very low error rates for most users.",
            last_validated="2025-06-11"
        ),
        Fact(
            number=57,
            description="RN deactivates and activates offers daily based on restaurant participation. Offer reactivation functionality has not yet been implemented.",
            last_validated="2025-06-11"
        )
    ]
    
    return KnowledgeBase(
        title="Current RN Project Facts",
        facts=facts
    )


def get_knowledge_guidelines() -> str:
    """Returns the hardcoded knowledge management guidelines."""
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