"""
Airweave-powered context search for sales briefings.

Searches across Notion, Google Drive, and GitHub via Airweave
to gather context for account briefs.
"""
import os
import logging
from typing import List, Dict, Any, Optional

import httpx

logger = logging.getLogger(__name__)


class ContextSearcher:
    """
    Searches for context related to decomposed queries using Airweave.

    Each query is searched with its tagged source_name filter.
    Uses httpx to call the Airweave REST API directly.
    Falls back to sample data when Airweave is not configured.
    """

    def __init__(self):
        self.api_key = os.getenv("AIRWEAVE_API_KEY")
        self.api_url = (os.getenv("AIRWEAVE_API_URL", "https://api.airweave.ai")).rstrip("/")
        self.collection_id = os.getenv("AIRWEAVE_COLLECTION_ID")
        self.configured = bool(self.api_key and self.collection_id)

        if self.configured:
            logger.info("Airweave configured for context search")
        else:
            logger.warning("Airweave not configured - using sample search results")

    async def search(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Search for context across all decomposed queries.

        Args:
            queries: List of decomposed queries with query, source_name, rationale

        Returns:
            List of search results with query, source_name, title, content, url, score
        """
        if self.configured:
            return await self._airweave_search(queries)
        else:
            return self._sample_search(queries)

    async def _airweave_search(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search Airweave for each decomposed query."""
        all_results = []

        async with httpx.AsyncClient(timeout=60.0) as client:
            for q in queries:
                query_text = q.get("query", "")
                source_name = q.get("source_name")

                try:
                    results = await self._search_source(
                        client=client,
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
        client: httpx.AsyncClient,
        query: str,
        source_filter: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search a specific source in Airweave via REST API."""
        url = f"{self.api_url}/collections/{self.collection_id}/search"

        body: Dict[str, Any] = {
            "query": query,
            "limit": limit,
        }

        if source_filter:
            body["filter"] = {
                "must": [{
                    "key": "source_name",
                    "match": {"any": [source_filter]}
                }]
            }

        try:
            response = await client.post(
                url,
                json=body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()

            results = []
            items = data.get("results", data if isinstance(data, list) else [])
            for item in items[:limit]:
                metadata = item.get("metadata", item.get("payload", {}))
                results.append({
                    "title": metadata.get("title", item.get("title", "Untitled")),
                    "content": (item.get("content", "") or "")[:500],
                    "source": metadata.get("source_name", source_filter or "unknown"),
                    "url": metadata.get("url", item.get("url")),
                    "score": item.get("score", 0),
                })

            logger.info(f"Airweave: {len(results)} results for '{query[:50]}' (source={source_filter})")
            return results

        except Exception as e:
            logger.error(f"Airweave search failed for '{query[:50]}': {e}")
            return []

    def _sample_search(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return sample search results for demo mode."""
        from samples.briefings import get_sample_search_results
        return get_sample_search_results()
