# Discogs Record Shelf

A Python tool for creating custom reports from your Discogs music collection with sorting by shelf and then alphabetically.

## Installation

```bash
pip install discogs-record-shelf
```

## Features

- Generate detailed collection reports in Excel, CSV, or HTML format
- Sort items by shelf, then alphabetically by artist and title
- Filter reports by specific shelves
- Export separate sheets for each shelf (Excel format)
- Command-line interface for easy automation
- Rate limiting to respect Discogs API limits
- Comprehensive logging and error handling

## Setup

### 1. Get a Discogs API Token

1. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
2. Create a new application or use an existing one
3. Generate a personal access token
4. Save your token - you'll need it to run the tool

### 2. Quick Start

After installation, the `record-shelf` command is available globally.

### 3. Set Environment Variable (Optional)

You can set your Discogs token as an environment variable:

```bash
export DISCOGS_TOKEN="your_token_here"
```

Or pass it directly via the `--token` option when running commands.

## Usage

### Generate a Full Collection Report

```bash
record-shelf generate --username YOUR_DISCOGS_USERNAME --output my_collection.xlsx
```

### Generate Report with Token

```bash
record-shelf generate --token YOUR_TOKEN --username YOUR_DISCOGS_USERNAME
```

### Filter by Specific Shelf

```bash
record-shelf generate --username YOUR_DISCOGS_USERNAME --shelf "Vinyl" --output vinyl_collection.xlsx
```

### Generate CSV Report

```bash
record-shelf generate --username YOUR_DISCOGS_USERNAME --format csv --output collection.csv
```

### List Available Shelves

```bash
record-shelf list-shelves --username YOUR_DISCOGS_USERNAME
```

### Enable Debug Logging

```bash
record-shelf --debug generate --username YOUR_DISCOGS_USERNAME
```

## Report Format

The generated reports include the following columns:

- **Shelf**: Collection folder/shelf name
- **Artist**: Artist name(s)
- **Title**: Release title
- **Label**: Record label(s)
- **Catalog Number**: Label catalog number(s)
- **Format**: Format details (e.g., "Vinyl, LP, Album")
- **Year**: Release year
- **Genre**: Music genre(s)
- **Style**: Music style(s)
- **Country**: Country of release
- **Discogs ID**: Unique Discogs release ID
- **Master ID**: Master release ID (if applicable)
- **Rating**: Your rating (if set)
- **Notes**: Your personal notes (if any)

## Output Formats

### Excel (.xlsx)
- Main "Collection" sheet with all items
- Separate sheet for each shelf
- Sortable columns and formatting

### CSV (.csv)
- Single file with all collection data
- Compatible with spreadsheet applications

### HTML (.html)
- Web-viewable table format
- Can be opened in any web browser

## Command Line Options

### Global Options
- `--debug`: Enable debug logging

### Generate Command
- `--token`: Discogs API token (or use DISCOGS_TOKEN env var)
- `--username`: Your Discogs username (required)
- `--output`, `-o`: Output file path (default: discogs_report.xlsx)
- `--shelf`: Filter by specific shelf name (optional)
- `--format`: Output format - xlsx, csv, or html (default: xlsx)

### List Shelves Command
- `--token`: Discogs API token (or use DISCOGS_TOKEN env var)
- `--username`: Your Discogs username (required)

## Rate Limiting

The tool includes built-in rate limiting to respect Discogs API limits:
- 1 second delay between API calls (configurable)
- Progress bars show processing status
- Automatic retry on rate limit errors

## Troubleshooting

### Common Issues

**Authentication Error**
- Verify your Discogs token is correct
- Ensure token has proper permissions
- Check if token is set via environment variable or --token option

**Empty Collection**
- Verify the username is correct
- Check if the collection is public
- Ensure the user has items in their collection

**Missing Shelves**
- Some collections may not have custom shelves
- Default shelf names vary by user

### Debug Mode

Run with `--debug` flag to see detailed logging:

```bash
record-shelf --debug generate --username YOUR_USERNAME
```

Logs are also saved to `record_shelf.log`.

## Development

### Project Structure

```
discogs-record-shelf/
├── record_shelf/
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # Main CLI application
│   ├── config.py        # Configuration management
│   ├── report_generator.py # Core report generation logic
│   └── utils.py         # Utility functions
├── docs/                # Documentation
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
├── README.md           # This file
└── LICENSE             # BSD 3-Clause License
```

### Adding New Features

1. Core logic goes in `report_generator.py`
2. CLI commands are added to `cli.py`
3. Configuration options go in `config.py`
4. Utilities and helpers go in `utils.py`

## License

This project is licensed under the BSD 3-Clause License. See the LICENSE file for details.

Please respect Discogs' Terms of Service and API rate limits when using this tool.

## Links

- **PyPI**: https://pypi.org/project/discogs-record-shelf/
- **GitHub**: https://github.com/bryankemp/discogs-record-shelf
- **Documentation**: https://discogs-record-shelf.readthedocs.io/

## Contributing

Feel free to submit issues and enhancement requests on GitHub!

