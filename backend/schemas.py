"""
Pydantic schemas for the sales context agent pipeline.

Provides strongly-typed data contracts for all stages of brief generation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Briefing Request (Input)
# ============================================================================

class BriefingRequest(BaseModel):
    """Input request for generating a pre-meeting brief."""
    account: str = Field(description="Account or company name")
    topic: str = Field(description="Meeting topic or agenda")
    attendees: Optional[List[str]] = Field(
        default=None, description="Meeting attendees (names and titles)"
    )


# ============================================================================
# Query Decomposition Stage
# ============================================================================

class DecomposedQuery(BaseModel):
    """A single search query generated from the briefing request."""
    query: str = Field(description="The search query text")
    source_name: str = Field(description="Source to search: notion, google_drive, github")
    rationale: str = Field(description="Why this query is relevant to the briefing")


# ============================================================================
# Search Stage
# ============================================================================

class SearchResult(BaseModel):
    """A single search result from Airweave."""
    query: str = Field(description="The query that produced this result")
    source_name: str = Field(description="Source: notion, google_drive, github")
    title: str = Field(description="Result title")
    content: str = Field(description="Result content or snippet")
    url: Optional[str] = Field(default=None, description="Link to the source document")
    score: float = Field(default=0.0, description="Relevance score")


# ============================================================================
# Synthesis Stage
# ============================================================================

class BriefSection(BaseModel):
    """A section of the generated account brief."""
    heading: str = Field(description="Section heading")
    content: str = Field(description="Section content in markdown")


class AccountBrief(BaseModel):
    """The final synthesized account brief."""
    account: str = Field(description="Account name")
    topic: str = Field(description="Meeting topic")
    generated_at: str = Field(description="When the brief was generated")
    sections: List[BriefSection] = Field(
        default_factory=list, description="Brief sections"
    )
    markdown: str = Field(default="", description="Full rendered markdown brief")


# ============================================================================
# Output Stage
# ============================================================================

class SlackPostResult(BaseModel):
    """Result of posting brief to Slack."""
    channel: str = Field(description="Channel ID or name")
    message_ts: Optional[str] = Field(default=None, description="Message timestamp")
    posted: bool = Field(default=False, description="Whether the post succeeded")
    is_preview: bool = Field(
        default=False, description="Preview mode (not actually posted)"
    )


class BriefOutput(BaseModel):
    """Final output of the pipeline."""
    brief: AccountBrief = Field(description="The generated account brief")
    slack_result: Optional[SlackPostResult] = Field(
        default=None, description="Slack posting result"
    )


# ============================================================================
# Pipeline Results
# ============================================================================

class PipelineResult(BaseModel):
    """Summary of pipeline execution."""
    run_id: str = Field(description="Unique run identifier")
    started_at: datetime = Field(description="When pipeline started")
    completed_at: Optional[datetime] = Field(
        default=None, description="When pipeline completed"
    )
    briefing_request: BriefingRequest = Field(description="The original request")
    queries_generated: int = Field(default=0, description="Number of search queries")
    results_found: int = Field(default=0, description="Total search results")
    brief: Optional[AccountBrief] = Field(default=None, description="The generated brief")
    status: str = Field(default="running")
    error_message: Optional[str] = Field(default=None, description="Error if failed")
