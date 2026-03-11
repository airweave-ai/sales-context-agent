"""
Airweave client for cross-source context search.

Uses httpx to call the Airweave API directly (avoids SDK pydantic version conflicts).
Searches across Notion, Google Drive, GitHub, and other connected sources.
"""
import logging
from typing import List, Dict, Any, Optional

import httpx

from config import get_config

logger = logging.getLogger(__name__)


class AirweaveClient:
    """
    Async client for searching Airweave collections.

    Calls the Airweave REST API directly via httpx.
    """

    def __init__(self):
        config = get_config()
        self.api_key = config.airweave.api_key
        self.api_url = (config.airweave.api_url or "https://api.airweave.ai").rstrip("/")
        self.collection_id = config.airweave.collection_id

        if self.is_configured:
            logger.info(f"Airweave client configured (collection: {self.collection_id})")
        else:
            logger.warning("Airweave not configured - context search will use sample data")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.collection_id)

    async def search(
        self,
        query: str,
        source_filter: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search an Airweave collection.

        Args:
            query: Search query string
            source_filter: Optional source_name filter (e.g. "notion", "github")
            limit: Maximum number of results

        Returns:
            List of search result dicts with content, metadata, and score
        """
        if not self.is_configured:
            logger.debug("Airweave not configured, returning empty results")
            return []

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
            async with httpx.AsyncClient(timeout=60.0) as client:
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
            for item in data.get("results", data if isinstance(data, list) else []):
                results.append({
                    "content": item.get("content", ""),
                    "metadata": item.get("metadata", {}),
                    "payload": item.get("payload", {}),
                    "score": item.get("score", 0),
                })

            logger.info(f"Airweave search returned {len(results)} results for: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Airweave search failed: {e}", exc_info=True)
            return []


# Singleton instance
_airweave_client: Optional[AirweaveClient] = None


def get_airweave_client() -> AirweaveClient:
    """Get singleton Airweave client instance."""
    global _airweave_client
    if _airweave_client is None:
        _airweave_client = AirweaveClient()
    return _airweave_client
