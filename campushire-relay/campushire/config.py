"""Application configuration for CampusHire Relay."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    app_name: str = "CampusHire Relay"
    room_name: str = os.getenv("SWITCH_ROOM_NAME", "#placement-drive-2027")
    switch_webhook_url: str = os.getenv("SWITCH_WEBHOOK_URL", "")
    port: int = int(os.getenv("PORT", "8080"))
    borderline_cgpa_delta: float = float(os.getenv("BORDERLINE_CGPA_DELTA", "0.1"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
