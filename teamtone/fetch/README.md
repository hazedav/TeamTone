# Filament Data Scraper

Automatically fetch and merge filament data from external sources into `filaments.yaml`.

## Architecture

- `scrape_filaments.py` - Main script that updates filaments.yaml directly
- `filament_sites/` - Site-specific scraper implementations
  - `base.py` - Abstract base class defining the scraper interface
  - `filamentprofiles.py` - Scraper for 3dfilamentprofiles.com
  - *(Add more scrapers here as needed)*

## Installation

```bash
cd teamtone
uv sync
```

## Usage

### Basic Usage

Scrape and merge into filaments.yaml:

```bash
python fetch/scrape_filaments.py
```

### Preview Changes First

Use `--dry-run` to see what would change:

```bash
python fetch/scrape_filaments.py --dry-run
```

### Other Options

```bash
# List available sites
python fetch/scrape_filaments.py --list-sites

# Scrape more results
python fetch/scrape_filaments.py --per-page 200

# Use a different site
python fetch/scrape_filaments.py --site filamentprofiles

# Increase delay to avoid rate limiting (useful for large scrapes)
python fetch/scrape_filaments.py --per-page 200 --delay 2.0

# Disable throttling (not recommended)
python fetch/scrape_filaments.py --delay 0
```

### Command Line Options

- `--site` - Source site to scrape (default: filamentprofiles)
- `--per-page` - Number of results per page (default: 100)
- `--delay` - Delay in seconds between requests to prevent rate limiting (default: 1.0)
- `--dry-run` - Preview changes without modifying files
- `--list-sites` - List available scraper sites and exit

## Workflow

1. **Scrape data:**
   ```bash
   python fetch/scrape_filaments.py
   ```

2. **Review changes:**
   ```bash
   git diff teamtone/filaments.yaml
   ```

3. **Commit if good:**
   ```bash
   git add teamtone/filaments.yaml
   git commit -m "Update filament data from 3dfilamentprofiles.com"
   ```

## CI Integration

```yaml
# .github/workflows/update-filaments.yml
name: Update Filament Data

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: |
          cd teamtone
          uv sync

      - name: Scrape filament data
        run: |
          cd teamtone
          python fetch/scrape_filaments.py

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add teamtone/filaments.yaml
          git diff --quiet && git diff --staged --quiet || \
            git commit -m "chore: update filament data" && git push
```

## Adding New Scrapers

1. Create `filament_sites/newsource.py`:

```python
from .base import FilamentScraper

class NewSourceScraper(FilamentScraper):
    @property
    def site_name(self) -> str:
        return "NewSource.com"

    @property
    def site_url(self) -> str:
        return "https://newsource.com"

    def fetch(self, **kwargs) -> dict:
        # Implement scraping logic
        return {
            "source_url": self.site_url,
            "source_name": self.site_name,
            "filaments": [
                {
                    "manufacturer": "Brand",
                    "material": "PLA",
                    "color": "Red",
                    "hex": "#FF0000",
                    "temp_hotend": 205,  # optional
                    "temp_bed": 60,      # optional
                },
                # ... more filaments
            ]
        }
```

2. Add import to `filament_sites/__init__.py`:

```python
from .newsource import NewSourceScraper

__all__ = [..., "NewSourceScraper"]
```

3. Register in `scrape_filaments.py`:

```python
SCRAPERS = {
    ...,
    'newsource': NewSourceScraper,
}
```

## How It Works

1. Script fetches data from the specified site
2. Converts to standardized format matching filaments.yaml structure
3. Deep merges new data into existing filaments.yaml
4. Overwrites filaments.yaml with merged data
5. Use `git diff` to review before committing

The merge strategy:
- Existing manufacturers/materials/colors are preserved
- New entries are added
- Duplicate entries are overwritten with new data
- No data is deleted (only additions/updates)

## Rate Limiting & Anti-Blocking

The scraper includes built-in protection against rate limiting:

### Features

1. **Custom User Agent** - Mimics Chrome browser to avoid blocks
   ```
   Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
   (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36
   ```

2. **Request Throttling** - Default 1 second delay between requests
   - Configurable via `--delay` parameter
   - Set to 0 to disable (not recommended)

3. **Automatic Retries** - Handles 429 (Too Many Requests) errors
   - Up to 3 retry attempts
   - Exponential backoff (5s, 10s, 15s)
   - Clear error messages if all retries fail

4. **Realistic Headers** - Includes Accept, Accept-Language, DNT, etc.

### Troubleshooting Rate Limits

If you encounter 429 errors:

```bash
# Increase delay between requests
python fetch/scrape_filaments.py --delay 2.0

# Reduce results per page and increase delay
python fetch/scrape_filaments.py --per-page 50 --delay 3.0
```

The scraper will automatically retry on 429 errors, but if you consistently get blocked, increase the `--delay` value.

## Customizing Site Scrapers

Site-specific scrapers need customization based on actual HTML structure:

1. Visit the URL in a browser
2. Inspect page source (F12)
3. Update CSS selectors in the scraper's `_parse_*` methods
4. Test with `--dry-run` to verify

See [filamentprofiles.py](filament_sites/filamentprofiles.py) for parsing strategies.
