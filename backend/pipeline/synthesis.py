"""
Brief synthesis from search results.

Takes all search results and uses an LLM to synthesize a structured
markdown brief with key sections for the sales rep.
"""
import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class BriefSynthesizer:
    """
    Synthesizes search results into a structured account brief.

    Produces sections: Account Snapshot, Relationship History,
    Open Concerns to Address, Relevant Product Updates, Suggested Talking Points.
    """

    def __init__(self):
        self.llm = None
        self.last_reasoning = None
        self._init_llm()

    def _init_llm(self):
        """Initialize the LLM for synthesis."""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if anthropic_key and len(anthropic_key) > 10:
            try:
                from langchain_anthropic import ChatAnthropic
                model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
                self.llm = ChatAnthropic(
                    model=model,
                    anthropic_api_key=anthropic_key,
                    temperature=0,
                )
                logger.info(f"Brief synthesizer using Anthropic ({model})")
                return
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}")

        if openai_key and len(openai_key) > 10:
            try:
                from langchain_openai import ChatOpenAI
                model = os.getenv("OPENAI_MODEL", "gpt-4o")
                self.llm = ChatOpenAI(
                    model=model,
                    openai_api_key=openai_key,
                    temperature=0,
                )
                logger.info(f"Brief synthesizer using OpenAI ({model})")
                return
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

        logger.warning("No LLM configured - using sample brief")

    async def synthesize(
        self,
        briefing_request: Dict[str, Any],
        search_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Synthesize search results into a structured account brief.

        Args:
            briefing_request: The original briefing request
            search_results: All search results from the search step

        Returns:
            Dict with account, topic, generated_at, sections, and markdown
        """
        account = briefing_request.get("account", "Unknown")
        topic = briefing_request.get("topic", "Meeting")
        attendees = briefing_request.get("attendees", [])

        if self.llm and search_results:
            try:
                return await self._llm_synthesize(
                    account, topic, attendees, search_results
                )
            except Exception as e:
                logger.error(f"LLM synthesis failed: {e}", exc_info=True)

        return self._fallback_synthesize(account, topic)

    async def _llm_synthesize(
        self,
        account: str,
        topic: str,
        attendees: List[str],
        search_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Use LLM to synthesize the brief."""
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        from pydantic import BaseModel, Field
        from typing import List as ListType

        class SynthesizedBrief(BaseModel):
            sections: ListType[Dict[str, str]] = Field(
                description="Brief sections with heading and content"
            )

        parser = JsonOutputParser(pydantic_object=SynthesizedBrief)

        # Format search results for the prompt
        results_text = self._format_results_for_prompt(search_results)

        attendee_text = ""
        if attendees:
            attendee_text = f"\nAttendees: {', '.join(attendees)}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a sales briefing assistant. Given search results from
multiple sources (Notion CRM, Google Drive, GitHub), synthesize a structured
pre-meeting brief for a sales rep.

The brief must have exactly these 5 sections:
1. "Account Snapshot" - Key account metrics (ARR, plan, health score, seats, usage stats). Use a markdown table for structured data.
2. "Relationship History" - Recent interactions, meetings, escalations, sentiment. Use bullet points with dates.
3. "Open Concerns to Address" - Issues the customer has raised, risks to address. Numbered list.
4. "Relevant Product Updates" - Engineering work, releases, bug fixes relevant to this account. Bullet points.
5. "Suggested Talking Points" - Specific, actionable recommendations for the meeting. Numbered list with bold headers.

Guidelines:
- Be specific and actionable. Include numbers, dates, and names.
- Reference specific documents, PRs, and issues by name.
- Focus on what the sales rep needs to know to walk in prepared.
- Keep each section concise but thorough.
- Do not use em dashes anywhere. Use regular hyphens instead.
- Format content as markdown.

Return a JSON object with:
- "sections": list of objects with "heading" and "content" (markdown string)

{format_instructions}"""),
            ("human", """Briefing Request:
Account: {account}
Topic: {topic}{attendees}

Search Results:
{results}

Synthesize a pre-meeting brief from these results."""),
        ])

        chain = prompt | self.llm | parser

        result = await chain.ainvoke({
            "account": account,
            "topic": topic,
            "attendees": attendee_text,
            "results": results_text,
            "format_instructions": parser.get_format_instructions(),
        })

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        sections = result.get("sections", [])

        # Build the full markdown
        markdown = f"# Pre-Meeting Brief: {account}\n\n"
        markdown += f"**Meeting Topic:** {topic}\n"
        markdown += f"**Generated:** {now}\n\n---\n"

        for section in sections:
            heading = section.get("heading", "")
            content = section.get("content", "")
            markdown += f"\n## {heading}\n\n{content}\n"

        return {
            "account": account,
            "topic": topic,
            "generated_at": now,
            "sections": sections,
            "markdown": markdown,
        }

    def _format_results_for_prompt(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results as text for the LLM prompt."""
        parts = []
        for i, result in enumerate(search_results, 1):
            source = result.get("source_name", "unknown")
            title = result.get("title", "Untitled")
            content = result.get("content", "")
            url = result.get("url", "")

            parts.append(
                f"[{i}] Source: {source} | Title: {title}\n"
                f"URL: {url}\n"
                f"Content:\n{content}\n"
            )

        return "\n---\n".join(parts)

    def _fallback_synthesize(self, account: str, topic: str) -> Dict[str, Any]:
        """Return sample brief when no LLM is available."""
        from samples.briefings import get_sample_brief
        return get_sample_brief()
