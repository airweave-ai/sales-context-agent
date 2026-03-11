"""
Airweave-powered context search for sales briefings.

Searches across Notion, Google Drive, and GitHub via Airweave
to gather context for account briefs.
"""
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ContextSearcher:
    """
    Searches for context related to decomposed queries using Airweave.

    Each query is searched with its tagged source_name filter.
    Falls back to sample data when Airweave is not configured.
    """

    def __init__(self):
        self._init_airweave()

    def _init_airweave(self):
        """Initialize the Airweave client."""
        api_key = os.getenv("AIRWEAVE_API_KEY")
        api_url = os.getenv("AIRWEAVE_API_URL", "https://api.airweave.ai")
        self.collection_id = os.getenv("AIRWEAVE_COLLECTION_ID")

        if api_key and self.collection_id:
            try:
                from airweave import AirweaveSDK
                self.client = AirweaveSDK(
                    api_key=api_key,
                    base_url=api_url
                )
                self.configured = True
                logger.info("Airweave client initialized for context search")
            except Exception as e:
                logger.warning(f"Failed to initialize Airweave: {e}")
                self.client = None
                self.configured = False
        else:
            self.client = None
            self.configured = False
            logger.warning("Airweave not configured - using sample search results")

    async def search(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Search for context across all decomposed queries.

        Args:
            queries: List of decomposed queries with query, source_name, rationale

        Returns:
            List of search results with query, source_name, title, content, url, score
        """
        if self.configured and self.client:
            return await self._airweave_search(queries)
        else:
            return self._sample_search(queries)

    async def _airweave_search(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search Airweave for each decomposed query."""
        all_results = []

        for q in queries:
            query_text = q.get("query", "")
            source_name = q.get("source_name")

            try:
                results = await self._search_source(
                    query=query_text,
                    source_filter=source_name,
                    limit=5,
                )
                for result in results:
                    all_results.append({
                        "query": query_text,
                        "source_name": result.get("source", source_name or "unknown"),
                        "title": result.get("title", "Untitled"),
                        "content": result.get("content", ""),
                        "url": result.get("url"),
                        "score": result.get("score", 0),
                    })
            except Exception as e:
                logger.error(f"Search failed for query '{query_text}': {e}")

        return all_results

    async def _search_source(
        self,
        query: str,
        source_filter: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search a specific source in Airweave."""
        try:
            search_params = {
                "query": query,
                "limit": limit,
            }

            if source_filter:
                search_params["source_name"] = source_filter

            response = await self.client.search.search(
                collection_id=self.collection_id,
                **search_params
            )

            results = []
            for item in response.results[:limit]:
                results.append({
                    "title": getattr(item, 'title', 'Untitled'),
                    "content": getattr(item, 'content', '')[:500],
                    "source": getattr(item, 'source_name', 'unknown'),
                    "url": getattr(item, 'url', None),
                    "score": getattr(item, 'score', 0),
                })

            return results

        except Exception as e:
            logger.error(f"Search failed for source {source_filter}: {e}")
            return []

    def _sample_search(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return sample search results for demo mode."""
        from samples.briefings import get_sample_search_results
        return get_sample_search_results()
