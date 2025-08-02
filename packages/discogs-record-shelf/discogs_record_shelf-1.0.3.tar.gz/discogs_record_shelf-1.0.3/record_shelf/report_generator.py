"""
Report generator for music collection data
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import discogs_client
import pandas as pd
from tqdm import tqdm

from .config import Config


class ReportGenerator:
    """Generates custom reports from Discogs collection data"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize Discogs client
        self.client = discogs_client.Client(
            user_agent=config.user_agent, token=config.token
        )

    def get_user_categories(self, username: str) -> List[str]:
        """Get list of categories for a user"""
        try:
            user = self.client.user(username)
            collection_folders = user.collection_folders

            categories = []
            for folder in collection_folders:
                categories.append(folder.name)
                time.sleep(self.config.rate_limit_delay)

            return sorted(categories)

        except Exception as e:
            self.logger.error(f"Error fetching categories for {username}: {e}")
            raise

    def fetch_collection_data(
        self, username: str, category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch collection data for a user"""
        try:
            user = self.client.user(username)
            collection_items = []

            # Get collection folders
            folders = user.collection_folders

            for folder in tqdm(folders, desc="Processing folders"):
                # Skip if filtering by category and this isn't the target category
                if category_filter and folder.name != category_filter:
                    continue

                self.logger.info(f"Processing folder: {folder.name}")

                # Get releases in this folder
                releases = folder.releases

                for release in tqdm(
                    releases, desc=f"Processing {folder.name}", leave=False
                ):
                    try:
                        item_data = self._extract_release_data(release, folder.name)
                        collection_items.append(item_data)

                        # Rate limiting
                        time.sleep(self.config.rate_limit_delay)

                    except Exception as e:
                        self.logger.warning(
                            f"Error processing release {release.id}: {e}"
                        )
                        continue

            # Sort by category, then alphabetically by artist/title
            collection_items.sort(
                key=lambda x: (x["category"], x["artist"].lower(), x["title"].lower())
            )

            return collection_items

        except Exception as e:
            self.logger.error(f"Error fetching collection for {username}: {e}")
            raise

    def _extract_release_data(self, release: Any, category_name: str) -> Dict[str, Any]:
        """Extract relevant data from a release object"""
        try:
            # Get basic release info
            master_release = getattr(release, "master", None)

            return {
                "category": category_name,
                "artist": self._get_artist_name(release),
                "title": getattr(release, "title", ""),
                "label": self._get_label_name(release),
                "catalog_number": self._get_catalog_number(release),
                "format": self._get_format_info(release),
                "year": getattr(release, "year", ""),
                "genre": self._get_genres(release),
                "style": self._get_styles(release),
                "country": getattr(release, "country", ""),
                "discogs_id": getattr(release, "id", ""),
                "master_id": (
                    getattr(master_release, "id", "") if master_release else ""
                ),
                "rating": getattr(release, "rating", ""),
                "notes": getattr(release, "notes", ""),
            }

        except Exception as e:
            self.logger.warning(f"Error extracting release data: {e}")
            return {
                "category": category_name,
                "artist": "Unknown",
                "title": "Unknown",
                "label": "",
                "catalog_number": "",
                "format": "",
                "year": "",
                "genre": "",
                "style": "",
                "country": "",
                "discogs_id": "",
                "master_id": "",
                "rating": "",
                "notes": "",
            }

    def _get_artist_name(self, release: Any) -> str:
        """Extract artist name from release"""
        try:
            artists = getattr(release, "artists", [])
            if artists:
                return ", ".join([artist.name for artist in artists])
            return "Unknown Artist"
        except:
            return "Unknown Artist"

    def _get_label_name(self, release: Any) -> str:
        """Extract label name from release"""
        try:
            labels = getattr(release, "labels", [])
            if labels:
                return ", ".join([label.name for label in labels])
            return ""
        except:
            return ""

    def _get_catalog_number(self, release: Any) -> str:
        """Extract catalog number from release"""
        try:
            labels = getattr(release, "labels", [])
            if labels:
                cat_nums = [
                    getattr(label, "catno", "")
                    for label in labels
                    if hasattr(label, "catno")
                ]
                return ", ".join(filter(None, cat_nums))
            return ""
        except:
            return ""

    def _get_format_info(self, release: Any) -> str:
        """Extract format information from release"""
        try:
            formats = getattr(release, "formats", [])
            if formats:
                format_info = []
                for fmt in formats:
                    fmt_name = getattr(fmt, "name", "")
                    descriptions = getattr(fmt, "descriptions", [])
                    if descriptions:
                        fmt_name += f" ({', '.join(descriptions)})"
                    format_info.append(fmt_name)
                return ", ".join(format_info)
            return ""
        except:
            return ""

    def _get_genres(self, release: Any) -> str:
        """Extract genres from release"""
        try:
            genres = getattr(release, "genres", [])
            return ", ".join(genres) if genres else ""
        except:
            return ""

    def _get_styles(self, release: Any) -> str:
        """Extract styles from release"""
        try:
            styles = getattr(release, "styles", [])
            return ", ".join(styles) if styles else ""
        except:
            return ""

    def create_report(
        self, data: List[Dict[str, Any]], output_path: str, format_type: str = "xlsx"
    ) -> None:
        """Create a report from the collection data"""
        if not data:
            raise ValueError("No data to generate report")

        # Create DataFrame
        df = pd.DataFrame(data)

        # Reorder columns for better readability
        column_order = [
            "category",
            "artist",
            "title",
            "label",
            "catalog_number",
            "format",
            "year",
            "genre",
            "style",
            "country",
            "discogs_id",
            "master_id",
            "rating",
            "notes",
        ]

        # Only include columns that exist in the data
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]

        # Save based on format
        output_file_path = Path(output_path)

        if format_type == "xlsx":
            with pd.ExcelWriter(output_file_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Collection", index=False)

                # Create separate sheets for each category
                for category in df["category"].unique():
                    category_data = df[df["category"] == category]
                    sheet_name = category[:31]  # Excel sheet name limit
                    category_data.to_excel(writer, sheet_name=sheet_name, index=False)

        elif format_type == "csv":
            df.to_csv(output_file_path, index=False)

        elif format_type == "html":
            df.to_html(output_file_path, index=False, escape=False)

        self.logger.info(f"Report saved to {output_file_path}")

    def generate_summary_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the collection"""
        if not data:
            return {}

        df = pd.DataFrame(data)

        stats = {
            "total_items": len(df),
            "categories": df["category"].unique().tolist(),
            "items_per_category": df["category"].value_counts().to_dict(),
            "top_artists": df["artist"].value_counts().head(10).to_dict(),
            "top_labels": df["label"].value_counts().head(10).to_dict(),
            "formats": df["format"].value_counts().to_dict(),
            "years": df["year"].value_counts().sort_index().to_dict(),
        }

        return stats
