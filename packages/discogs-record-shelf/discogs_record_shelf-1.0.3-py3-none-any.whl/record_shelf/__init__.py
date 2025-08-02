"""
Record Shelf

A tool for creating custom reports from music collection data
with sorting by category and then alphabetically.
"""

__version__ = "1.0.3"
__author__ = "Bryan Kemp"
__email__ = "bryan@kempville.com"

from .config import Config
from .report_generator import ReportGenerator

__all__ = ["Config", "ReportGenerator"]
