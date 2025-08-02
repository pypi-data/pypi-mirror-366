"""
Utility functions for Record Shelf
"""

import logging
import sys
from typing import Any, Dict


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("record_shelf.log"),
        ],
    )


def print_stats(stats: Dict[str, Any]) -> None:
    """Print collection statistics in a readable format"""
    if not stats:
        print("No statistics available.")
        return

    print(f"\n=== Collection Statistics ===")
    print(f"Total Items: {stats.get('total_items', 0)}")

    if "items_per_category" in stats:
        print(f"\nItems per Category:")
        for category, count in stats["items_per_category"].items():
            print(f"  {category}: {count}")

    if "top_artists" in stats:
        print(f"\nTop 10 Artists:")
        for artist, count in list(stats["top_artists"].items())[:10]:
            print(f"  {artist}: {count}")

    if "formats" in stats:
        print(f"\nFormats:")
        for format_type, count in stats["formats"].items():
            if format_type:  # Skip empty formats
                print(f"  {format_type}: {count}")


def validate_username(username: str) -> bool:
    """Validate Discogs username format"""
    if not username:
        return False

    # Basic validation - Discogs usernames can contain letters, numbers, underscores, hyphens
    import re

    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, username))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility"""
    import re

    # Remove or replace problematic characters
    sanitized = re.sub(r'[<>:"/\|?*]', "_", filename)
    return sanitized.strip()
