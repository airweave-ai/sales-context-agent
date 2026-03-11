"""
Slack client with preview fallback.

When Slack is not configured, returns preview message objects instead of
posting real messages. This allows the demo to work without Slack access.
"""
import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from config import get_config

logger = logging.getLogger(__name__)


@dataclass
class SlackMessage:
    """Represents a Slack message (real or preview)."""
    channel: str
    text: str
    blocks: List[Dict[str, Any]]
    thread_ts: Optional[str] = None
    message_ts: Optional[str] = None
    is_preview: bool = False


class SlackClient:
    """
    Slack client using slack_sdk.
    
    When disabled/not configured, returns preview objects instead of 
    posting real messages.
    """
    
    def __init__(self):
        config = get_config()
        self.bot_token = config.slack.api_key
        self.channel_id = config.slack.channel_id
        self.enabled = config.slack.enabled
        
        self._configured = self.enabled and bool(self.bot_token) and bool(self.channel_id)
        self._client = None
        
        if self._configured:
            self._init_client()
            logger.info("Slack integration ENABLED - will post real messages")
        else:
            logger.info("Slack integration DISABLED - will generate previews only")
    
    def _init_client(self):
        """Initialize Slack client."""
        if self._configured and self._client is None:
            try:
                from slack_sdk.web.async_client import AsyncWebClient
                self._client = AsyncWebClient(token=self.bot_token)
            except ImportError:
                logger.error(
                    "Slack SDK not installed. Install with: pip install slack-sdk"
                )
                self._configured = False
    
    @property
    def is_configured(self) -> bool:
        """Check if Slack is properly configured."""
        return self._configured
    
    async def post_alert(
        self,
        signature: str,
        severity: str,
        root_cause: str,
        affected_orgs: List[str],
        linear_ticket: Optional[Any] = None,
        error_count: int = 1,
    ) -> SlackMessage:
        """
        Post an error alert to Slack, or return a preview if not configured.
        
        Args:
            signature: Error signature
            severity: Severity level (S1-S4)
            root_cause: Root cause description
            affected_orgs: List of affected organization names
            linear_ticket: Optional LinearTicket object
            error_count: Number of errors in cluster
            
        Returns:
            SlackMessage object (real or preview)
        """
        blocks = self._build_alert_blocks(
            signature=signature,
            severity=severity,
            root_cause=root_cause,
            affected_orgs=affected_orgs,
            linear_ticket=linear_ticket,
            error_count=error_count,
        )
        text = f"[{severity}] {signature[:80]}"
        
        if not self._configured:
            return self._create_preview(text, blocks)
        
        try:
            response = await self._client.chat_postMessage(
                channel=self.channel_id,
                text=text,
                blocks=blocks,
            )
            
            logger.info(f"Posted Slack alert: {response['ts']}")
            
            return SlackMessage(
                channel=self.channel_id,
                text=text,
                blocks=blocks,
                thread_ts=response["ts"],
                message_ts=response["ts"],
                is_preview=False,
            )
            
        except Exception as e:
            logger.error(f"Failed to post Slack message: {e}")
            return self._create_preview(text, blocks, error=str(e))
    
    async def post_thread_reply(
        self,
        thread_ts: str,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Post a reply in a thread.
        
        Args:
            thread_ts: Thread timestamp to reply to
            text: Message text
            blocks: Optional Block Kit blocks
            
        Returns:
            True if successful
        """
        if not self._configured:
            logger.info(f"[PREVIEW] Would reply to thread {thread_ts}: {text[:100]}...")
            return True
        
        try:
            await self._client.chat_postMessage(
                channel=self.channel_id,
                thread_ts=thread_ts,
                text=text,
                blocks=blocks,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to post thread reply: {e}")
            return False
    
    def _build_alert_blocks(
        self,
        signature: str,
        severity: str,
        root_cause: str,
        affected_orgs: List[str],
        linear_ticket: Optional[Any] = None,
        error_count: int = 1,
    ) -> List[Dict[str, Any]]:
        """Build Slack Block Kit message."""
        severity_emoji = {
            "S1": ":red_circle:",
            "S2": ":large_orange_circle:",
            "S3": ":large_yellow_circle:",
            "S4": ":large_blue_circle:",
        }.get(severity, ":white_circle:")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{severity_emoji} {severity}: {signature[:60]}",
                    "emoji": True,
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Root Cause:* {root_cause[:300]}",
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Errors:* {error_count}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Orgs Affected:* {len(affected_orgs)}",
                    },
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Affected:* {', '.join(affected_orgs[:5])}{'...' if len(affected_orgs) > 5 else ''}",
                    }
                ]
            },
        ]
        
        # Add Linear ticket link if available
        if linear_ticket and not getattr(linear_ticket, 'is_preview', True):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":ticket: *Ticket:* <{linear_ticket.url}|{linear_ticket.identifier}>",
                }
            })
        
        # Add mute buttons (only if Slack is actually enabled)
        if self._configured:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Mute 1h", "emoji": True},
                        "action_id": "mute_1h",
                        "value": signature[:100],
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Mute 8h", "emoji": True},
                        "action_id": "mute_8h",
                        "value": signature[:100],
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Mute 24h", "emoji": True},
                        "action_id": "mute_24h",
                        "value": signature[:100],
                    },
                ]
            })
        
        blocks.append({"type": "divider"})
        
        return blocks
    
    def _create_preview(
        self,
        text: str,
        blocks: List[Dict[str, Any]],
        error: Optional[str] = None,
    ) -> SlackMessage:
        """Create a preview message object."""
        preview_ts = f"preview-{uuid.uuid4().hex[:8]}"
        
        return SlackMessage(
            channel="preview",
            text=text if not error else f"{text} (Error: {error})",
            blocks=blocks,
            thread_ts=preview_ts,
            message_ts=preview_ts,
            is_preview=True,
        )


# Singleton instance
_slack_client: Optional[SlackClient] = None


def get_slack_client() -> SlackClient:
    """Get singleton Slack client instance."""
    global _slack_client
    if _slack_client is None:
        _slack_client = SlackClient()
    return _slack_client
