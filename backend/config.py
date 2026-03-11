"""
Application configuration for the Sales Context Agent.

Centralizes all configuration, making it easy to:
- Run with sample data (default, zero friction)
- Connect Airweave for real cross-source search
- Enable Slack for posting briefs to channels
"""
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from functools import lru_cache


@dataclass
class SlackConfig:
    """Slack configuration for posting briefs."""
    enabled: bool = False
    api_key: Optional[str] = None
    channel_id: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        return self.enabled and bool(self.api_key) and bool(self.channel_id)


@dataclass
class AirweaveConfig:
    """Airweave configuration (required for cross-source search)."""
    api_key: Optional[str] = None
    api_url: str = "https://api.airweave.ai"
    collection_id: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key) and bool(self.collection_id)


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Model preferences
    anthropic_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4o"

    @property
    def provider(self) -> Optional[str]:
        """Get the active LLM provider."""
        if self.anthropic_api_key:
            return "anthropic"
        elif self.openai_api_key:
            return "openai"
        return None

    @property
    def is_configured(self) -> bool:
        return self.provider is not None

    @property
    def model(self) -> Optional[str]:
        """Get the model name for the active provider."""
        if self.provider == "anthropic":
            return self.anthropic_model
        elif self.provider == "openai":
            return self.openai_model
        return None


@dataclass
class Config:
    """
    Main application configuration.

    Loads from environment variables.
    All integrations are optional for zero-friction demo experience.
    """
    airweave: AirweaveConfig = field(default_factory=AirweaveConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    slack: SlackConfig = field(default_factory=SlackConfig)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            airweave=AirweaveConfig(
                api_key=os.getenv("AIRWEAVE_API_KEY"),
                api_url=os.getenv("AIRWEAVE_API_URL", "https://api.airweave.ai"),
                collection_id=os.getenv("AIRWEAVE_COLLECTION_ID"),
            ),
            llm=LLMConfig(
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            ),
            slack=SlackConfig(
                enabled=os.getenv("SLACK_ENABLED", "false").lower() == "true",
                api_key=os.getenv("SLACK_BOT_TOKEN"),
                channel_id=os.getenv("SLACK_CHANNEL_ID"),
            ),
        )

    def get_status(self) -> Dict[str, Any]:
        """Get configuration status for API/UI."""
        return {
            "airweave": {
                "configured": self.airweave.is_configured,
                "collection_id": (
                    self.airweave.collection_id[:8] + "..."
                    if self.airweave.collection_id
                    else None
                ),
            },
            "llm": {
                "configured": self.llm.is_configured,
                "provider": self.llm.provider,
                "model": self.llm.model,
            },
            "integrations": {
                "slack": {
                    "enabled": self.slack.enabled,
                    "configured": self.slack.is_configured,
                    "mode": "live" if self.slack.is_configured else "preview",
                },
            },
        }


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get the application configuration (cached)."""
    return Config.from_env()


def reload_config() -> Config:
    """Force reload configuration from environment."""
    get_config.cache_clear()
    return get_config()
