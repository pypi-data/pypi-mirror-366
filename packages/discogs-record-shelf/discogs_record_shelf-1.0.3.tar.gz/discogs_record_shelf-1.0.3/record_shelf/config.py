"""
Configuration module for Record Shelf
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration"""

    token: Optional[str] = None
    user_agent: str = "RecordShelf/1.0"
    debug: bool = False
    rate_limit_delay: float = 1.0  # seconds between API calls

    def __post_init__(self) -> None:
        # Get token from environment if not provided
        if not self.token:
            self.token = os.getenv("DISCOGS_TOKEN")

        if not self.token:
            raise ValueError(
                "Discogs API token is required. "
                "Provide it via --token option or DISCOGS_TOKEN environment variable."
            )

    @property
    def discogs_headers(self) -> dict:
        """Headers for Discogs API requests"""
        return {
            "User-Agent": self.user_agent,
            "Authorization": f"Discogs token={self.token}",
        }
