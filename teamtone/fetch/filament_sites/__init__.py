"""Filament site scrapers package"""

from .base import FilamentScraper
from .filamentprofiles import FilamentProfilesScraper
from .overture import OvertureScraper
from .polymaker import PolymakerScraper
from .sunlu import SunluScraper

# All available scraper classes
SCRAPER_CLASSES: list[type[FilamentScraper]] = [
    FilamentProfilesScraper,
    OvertureScraper,
    PolymakerScraper,
    SunluScraper,
]


def get_dedicated_manufacturers() -> set[str]:
    """
    Get the set of manufacturer names that have dedicated scrapers.

    Returns:
        Set of lowercase manufacturer names (e.g., {"polymaker", "sunlu", "overture"})
    """
    manufacturers = set()
    for scraper_class in SCRAPER_CLASSES:
        # Instantiate to access the manufacturer property
        scraper = scraper_class()
        if scraper.manufacturer is not None:
            manufacturers.add(scraper.manufacturer.lower())
    return manufacturers


__all__ = [
    "FilamentScraper",
    "FilamentProfilesScraper",
    "OvertureScraper",
    "PolymakerScraper",
    "SunluScraper",
    "SCRAPER_CLASSES",
    "get_dedicated_manufacturers",
]
