"""
Query decomposition for briefing requests.

Takes a briefing request (account + topic + attendees) and generates
targeted search queries, each tagged with the source to search.
"""
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class QueryDecomposer:
    """
    Decomposes a briefing request into targeted search queries.

    Each query is tagged with a source_name (notion, google_drive, github)
    so the search step can filter by source.
    """

    def __init__(self):
        self.llm = None
        self.last_reasoning = None
        self._init_llm()

    def _init_llm(self):
        """Initialize the LLM for query decomposition."""
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
                logger.info(f"Query decomposer using Anthropic ({model})")
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
                logger.info(f"Query decomposer using OpenAI ({model})")
                return
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")

        logger.warning("No LLM configured - using fallback decomposition")

    async def decompose(self, briefing_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decompose a briefing request into search queries.

        Args:
            briefing_request: Dict with account, topic, and optional attendees

        Returns:
            List of decomposed queries with query, source_name, and rationale
        """
        account = briefing_request.get("account", "")
        topic = briefing_request.get("topic", "")
        attendees = briefing_request.get("attendees", [])

        if self.llm:
            try:
                return await self._llm_decompose(account, topic, attendees)
            except Exception as e:
                logger.error(f"LLM decomposition failed: {e}", exc_info=True)

        return self._fallback_decompose(account, topic, attendees)

    async def _llm_decompose(
        self,
        account: str,
        topic: str,
        attendees: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Use LLM to generate targeted search queries."""
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        from pydantic import BaseModel, Field
        from typing import List as ListType

        class QueryPlan(BaseModel):
            queries: ListType[Dict[str, str]] = Field(
                description="List of search queries"
            )
            reasoning: str = Field(
                description="Why these queries were chosen"
            )

        parser = JsonOutputParser(pydantic_object=QueryPlan)

        attendee_text = ""
        if attendees:
            attendee_text = f"\nAttendees: {', '.join(attendees)}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a sales research assistant. Given a briefing request,
generate 4-6 targeted search queries to gather context for a pre-meeting brief.

Each query should target one of these sources:
- "notion": for CRM data, account pages, meeting notes, internal docs
- "google_drive": for account plans, proposals, product briefs, shared documents
- "github": for code changes, PRs, issues, and engineering work relevant to the account

Return a JSON object with:
- "queries": list of objects, each with "query" (search text), "source_name" (notion/google_drive/github), "rationale" (why this query matters)
- "reasoning": brief explanation of your search strategy

Guidelines:
- Start with CRM/account data from Notion
- Include relationship history (meeting notes, past conversations)
- Search for account plans and proposals in Google Drive
- Check GitHub for relevant product updates, bug fixes, or feature work
- Make queries specific enough to find relevant results
- Do not use em dashes in your output

{format_instructions}"""),
            ("human", """Briefing Request:
Account: {account}
Topic: {topic}{attendees}

Generate search queries to build a comprehensive pre-meeting brief."""),
        ])

        chain = prompt | self.llm | parser

        result = await chain.ainvoke({
            "account": account,
            "topic": topic,
            "attendees": attendee_text,
            "format_instructions": parser.get_format_instructions(),
        })

        self.last_reasoning = result.get("reasoning", "")

        queries = []
        for q in result.get("queries", []):
            queries.append({
                "query": q.get("query", ""),
                "source_name": q.get("source_name", "notion"),
                "rationale": q.get("rationale", ""),
            })

        return queries

    def _fallback_decompose(
        self,
        account: str,
        topic: str,
        attendees: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Generate queries without LLM using templates."""
        self.last_reasoning = "Generated using template-based decomposition (no LLM configured)"

        queries = [
            {
                "query": f"{account} account overview health score",
                "source_name": "notion",
                "rationale": "Pull CRM account data including health score, ARR, and key contacts",
            },
            {
                "query": f"{account} meeting notes conversations",
                "source_name": "notion",
                "rationale": "Find recent meeting notes and conversation history",
            },
            {
                "query": f"{account} account plan renewal",
                "source_name": "google_drive",
                "rationale": "Locate account plan with renewal timeline and expansion opportunities",
            },
            {
                "query": f"{account} {topic} product feedback",
                "source_name": "google_drive",
                "rationale": "Find relevant product briefs or feedback documents",
            },
            {
                "query": f"{account} issues bug reports feature requests",
                "source_name": "github",
                "rationale": "Check for open issues or recent work related to this account",
            },
        ]

        return queries
