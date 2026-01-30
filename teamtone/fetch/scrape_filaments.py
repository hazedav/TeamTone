#!/usr/bin/env python3
"""
Scrape filament data and update filaments folder

This script fetches filament profiles from various sources and merges them
into the filaments/ folder, with one YAML file per manufacturer.
Use git to review changes before committing.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed.")
    print("Install with: uv sync")
    sys.exit(1)

from filament_sites import FilamentProfilesScraper


# Available scrapers
SCRAPERS = {
    "filamentprofiles": FilamentProfilesScraper,
    "3dfilamentprofiles": FilamentProfilesScraper,  # Alias
}


def sanitize_filename(name: str) -> str:
    """Convert manufacturer name to valid filename"""
    # Replace invalid characters with underscore
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Replace spaces and other whitespace with underscore
    name = re.sub(r"\s+", "_", name)
    # Remove leading/trailing underscores and dots
    name = name.strip("._")
    # Convert to lowercase for consistency
    name = name.lower()
    return name or "unknown"


def load_yaml(path: Path) -> dict:
    """Load YAML file, return empty dict if file doesn't exist"""
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(data: dict, path: Path) -> None:
    """Save data to YAML file"""
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )


def load_filaments_from_folder(folder: Path) -> dict:
    """
    Load all filament data from manufacturer YAML files in a folder

    Returns:
        Dictionary with structure: {manufacturer: {material: {color: data}}}
    """
    if not folder.exists():
        return {}

    all_data = {}

    for yaml_file in folder.glob("*.yaml"):
        manufacturer_data = load_yaml(yaml_file)
        if manufacturer_data:
            # The file name (without .yaml) is the manufacturer key
            # But the actual manufacturer name is stored in the data
            # We merge all manufacturers from this file
            all_data.update(manufacturer_data)

    return all_data


def save_filaments_to_folder(data: dict, folder: Path) -> list[Path]:
    """
    Save filament data to individual manufacturer YAML files

    Args:
        data: Dictionary with structure {manufacturer: {material: {color: data}}}
        folder: Path to filaments folder

    Returns:
        List of file paths that were written
    """
    folder.mkdir(parents=True, exist_ok=True)
    written_files = []

    for manufacturer, materials in data.items():
        # Create safe filename from manufacturer name
        filename = sanitize_filename(manufacturer) + ".yaml"
        file_path = folder / filename

        # Save this manufacturer's data
        manufacturer_data = {manufacturer: materials}
        save_yaml(manufacturer_data, file_path)
        written_files.append(file_path)

    return written_files


def merge_filament_data(existing: dict, new: dict) -> dict:
    """
    Deep merge new filament data into existing data

    Structure: {manufacturer: {material: {color: {hex, source, temp_hotend, temp_bed}}}}
    """
    result = existing.copy()

    for manufacturer, materials in new.items():
        if manufacturer not in result:
            result[manufacturer] = {}

        for material, colors in materials.items():
            if material not in result[manufacturer]:
                result[manufacturer][material] = {}

            for color, data in colors.items():
                # Add or update the color
                result[manufacturer][material][color] = data

    return result


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Scrape filament data and update filaments/ folder"
    )
    parser.add_argument(
        "--site",
        choices=list(SCRAPERS.keys()),
        default="filamentprofiles",
        help="Source site to scrape (default: filamentprofiles)",
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=100,
        help="Number of results per page (default: 100)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between requests to prevent rate limiting (default: 1.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to filaments/ folder",
    )
    parser.add_argument(
        "--list-sites",
        action="store_true",
        help="List available scraper sites and exit",
    )
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        help="Fetch raw HTML only without parsing (for debugging)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="raw_fetch.html",
        help="Output file for --fetch-only mode (default: raw_fetch.html)",
    )

    args = parser.parse_args()

    if args.list_sites:
        print("Available scraper sites:")
        seen = set()
        for name, scraper_class in SCRAPERS.items():
            if scraper_class not in seen:
                instance = scraper_class()
                print(f"  {name:20} -> {instance.site_url}")
                seen.add(scraper_class)
        return

    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    filaments_folder = project_root / "filaments"

    # Initialize the scraper
    scraper_class = SCRAPERS[args.site]
    scraper = scraper_class()

    print(f"Using scraper: {scraper.site_name}")
    print(f"Site URL: {scraper.site_url}")

    # Fetch the data
    try:
        raw_data = scraper.fetch(
            per_page=args.per_page, delay=args.delay, fetch_only=args.fetch_only
        )
    except Exception as e:
        print(f"Error during scraping: {e}")
        sys.exit(1)

    # If fetch-only mode, dump raw HTML and exit
    if args.fetch_only:
        output_path = Path(args.output)
        raw_html = raw_data.get("raw_html", "")

        if not raw_html:
            print("Error: No raw HTML data returned from scraper")
            sys.exit(1)

        # Check if content looks like text
        preview = raw_html[:200].replace("\n", " ").strip()
        has_null_bytes = "\x00" in raw_html[:1000]

        print("\nContent Analysis:")
        print(f"  Encoding: {raw_data.get('encoding', 'unknown')}")
        print(f"  Content-Type: {raw_data.get('content_type', 'unknown')}")
        print(f"  Has null bytes: {has_null_bytes}")
        print(f"  Preview: {preview}...")

        if has_null_bytes:
            print("\n⚠ Warning: Content appears to be binary, not text!")
            print("  The site may be returning compressed or binary data.")

        output_path.write_text(raw_html, encoding="utf-8")
        print(f"\n✓ Raw HTML saved to {output_path}")
        print(f"  Size: {len(raw_html):,} characters")
        print(f"  Source: {raw_data.get('source_url', 'Unknown')}")
        print("\nYou can now inspect this file to understand the page structure.")
        return

    # Convert to YAML format
    new_data = scraper.convert_to_yaml_format(raw_data)

    print(f"\nScraped {len(raw_data.get('filaments', []))} filaments")

    # Count entries in new data
    total_colors = sum(
        len(colors)
        for manufacturer in new_data.values()
        for material in manufacturer.values()
        for colors in [material]
    )
    print(
        f"Converted to {total_colors} color entries across {len(new_data)} manufacturers"
    )

    # Load existing data from folder
    existing_data = load_filaments_from_folder(filaments_folder)

    # Merge
    merged_data = merge_filament_data(existing_data, new_data)

    if args.dry_run:
        print("\n=== DRY RUN - No files modified ===")
        print(f"\nWould update: {filaments_folder}")
        print(
            f"Existing entries: {sum(len(colors) for mfr in existing_data.values() for mat in mfr.values() for colors in [mat])}"
        )
        print(
            f"After merge: {sum(len(colors) for mfr in merged_data.values() for mat in mfr.values() for colors in [mat])}"
        )

        # Show what would be added
        new_manufacturers = set(new_data.keys()) - set(existing_data.keys())
        if new_manufacturers:
            # Count and show sample of new manufacturers (limit to avoid encoding errors)
            print(f"\nNew manufacturers: {len(new_manufacturers)}")
            sample = list(sorted(new_manufacturers))[:10]
            for mfr in sample:
                filename = sanitize_filename(mfr)
                print(f"  - {mfr} -> {filename}.yaml")
            if len(new_manufacturers) > 10:
                print(f"  ... and {len(new_manufacturers) - 10} more")

        return

    # Save merged data to folder (one file per manufacturer)
    written_files = save_filaments_to_folder(merged_data, filaments_folder)

    print(f"\n[OK] Updated {filaments_folder}")
    print(f"  Files written: {len(written_files)}")
    print(
        f"  Total entries: {sum(len(colors) for mfr in merged_data.values() for mat in mfr.values() for colors in [mat])}"
    )
    print("\nNext steps:")
    print("  git status teamtone/filaments/     # See changed files")
    print("  git diff teamtone/filaments/       # Review changes")
    print("  git add teamtone/filaments/        # Stage if looks good")


if __name__ == "__main__":
    main()
