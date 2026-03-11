"""
External service clients for the sales context agent.

Each client gracefully handles the case where it's not configured,
returning preview/mock data instead of failing.
"""
from .airweave_client import AirweaveClient, get_airweave_client
from .slack_client import SlackClient, SlackMessage, get_slack_client

__all__ = [
    "AirweaveClient",
    "get_airweave_client",
    "SlackClient",
    "SlackMessage",
    "get_slack_client",
]
