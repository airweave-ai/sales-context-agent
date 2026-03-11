"""
Brief output handler.

Outputs the final brief as markdown and optionally posts to Slack.
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BriefOutputHandler:
    """
    Handles the output of the generated brief.

    Outputs the brief as markdown and optionally posts to Slack.
    """

    def __init__(self):
        self.slack_client = None
        self._init_slack()

    def _init_slack(self):
        """Initialize Slack client if configured."""
        enabled = os.getenv("SLACK_ENABLED", "false").lower() == "true"
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")

        if enabled and bot_token and self.channel_id:
            try:
                from clients.slack_client import get_slack_client
                self.slack_client = get_slack_client()
                logger.info("Slack client initialized for brief posting")
            except Exception as e:
                logger.warning(f"Failed to init Slack client: {e}")

    async def output(
        self,
        brief: Dict[str, Any],
        post_to_slack: bool = False,
    ) -> Dict[str, Any]:
        """
        Output the brief and optionally post to Slack.

        Args:
            brief: The synthesized account brief
            post_to_slack: Whether to post to Slack

        Returns:
            Dict with the brief and optional slack_result
        """
        result = {
            "brief": brief,
            "slack_result": None,
        }

        if post_to_slack:
            result["slack_result"] = await self._post_to_slack(brief)

        return result

    async def _post_to_slack(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Post the brief to Slack."""
        account = brief.get("account", "Unknown")
        topic = brief.get("topic", "Meeting")
        markdown = brief.get("markdown", "")

        if self.slack_client and self.slack_client.configured:
            try:
                # Build Slack blocks
                blocks = self._build_slack_blocks(account, topic, markdown)
                message = await self.slack_client.post_message(
                    channel=self.channel_id,
                    text=f"Pre-meeting brief: {account} - {topic}",
                    blocks=blocks,
                )
                return {
                    "channel": self.channel_id,
                    "message_ts": getattr(message, 'message_ts', None),
                    "posted": True,
                    "is_preview": False,
                }
            except Exception as e:
                logger.error(f"Failed to post brief to Slack: {e}")

        # Preview mode
        return {
            "channel": self.channel_id or "#sales-briefs",
            "message_ts": None,
            "posted": False,
            "is_preview": True,
        }

    def _build_slack_blocks(
        self,
        account: str,
        topic: str,
        markdown: str,
    ) -> list:
        """Build Slack Block Kit blocks for the brief."""
        # Truncate markdown for Slack (3000 char limit per block)
        sections = markdown.split("\n## ")
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Pre-Meeting Brief: {account}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Topic:* {topic}",
                },
            },
            {"type": "divider"},
        ]

        for section in sections[1:]:  # Skip the header section
            text = section[:3000]
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
            })

        return blocks
