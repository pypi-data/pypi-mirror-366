#!/usr/bin/env python3
"""
Record Shelf

A tool for creating custom reports from music collection data
with sorting by category and then alphabetically.
"""

from typing import Optional

import click

from record_shelf.config import Config
from record_shelf.report_generator import ReportGenerator
from record_shelf.utils import setup_logging


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """Record Shelf - Music Collection Reports Tool"""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    setup_logging(debug)


@cli.command()
@click.option("--token", help="Discogs API token (or set DISCOGS_TOKEN env var)")
@click.option("--username", required=True, help="Discogs username")
@click.option(
    "--output", "-o", default="collection_report.xlsx", help="Output file path"
)
@click.option("--category", help="Filter by specific category (optional)")
@click.option(
    "--format",
    type=click.Choice(["xlsx", "csv", "html"]),
    default="xlsx",
    help="Output format",
)
@click.pass_context
def generate(
    ctx: click.Context,
    token: Optional[str],
    username: str,
    output: str,
    category: Optional[str],
    format: str,
) -> None:
    """Generate a custom Discogs collection report"""
    try:
        config = Config(token=token, debug=ctx.obj["debug"])
        generator = ReportGenerator(config)

        click.echo(f"Fetching collection for user: {username}")
        report_data = generator.fetch_collection_data(
            username, category_filter=category
        )

        click.echo(f"Generating report with {len(report_data)} items...")
        generator.create_report(report_data, output, format)

        click.echo(f"Report saved to: {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--token", help="Discogs API token (or set DISCOGS_TOKEN env var)")
@click.option("--username", required=True, help="Discogs username")
def list_categories(token: Optional[str], username: str) -> None:
    """List all categories in the user's collection"""
    try:
        config = Config(token=token)
        generator = ReportGenerator(config)

        categories = generator.get_user_categories(username)

        click.echo("Available categories:")
        for category in categories:
            click.echo(f"  - {category}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


def main() -> None:
    """Main entry point for the CLI application."""
    cli()


if __name__ == "__main__":
    main()
