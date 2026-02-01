"""Scraper for overture3d.com"""

import re
import sys
import time
import warnings
from typing import Any

try:
    import requests
    from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

    # Suppress XML parsed as HTML warning when lxml not available
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install requests beautifulsoup4")
    sys.exit(1)

from .base import FilamentScraper


def _hex_to_luminance(hex_code: str) -> float:
    """
    Calculate perceived luminance of a hex color (0.0 = black, 1.0 = white).

    Uses the relative luminance formula from WCAG 2.0.
    """
    hex_code = hex_code.lstrip("#")
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


class OvertureScraper(FilamentScraper):
    """Scraper for overture3d.com Shopify store"""

    # Chrome user agent to avoid being blocked
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

    # Default delay between requests (seconds)
    DEFAULT_DELAY = 1.0

    # Retry configuration for rate limiting
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0

    # Products sitemap URL
    SITEMAP_URL = "https://overture3d.com/sitemap_products_1.xml?from=3528604418112&to=9121586118910"

    @property
    def site_name(self) -> str:
        return "overture3d.com"

    @property
    def site_url(self) -> str:
        return "https://overture3d.com"

    @property
    def manufacturer(self) -> str:
        return "Overture"

    def _get_session(self) -> requests.Session:
        """Create a requests session with appropriate headers"""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": self.USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        return session

    def _fetch_with_retry(
        self, session: requests.Session, url: str, delay: float
    ) -> requests.Response | None:
        """Fetch URL with retry logic for rate limiting"""
        for attempt in range(self.MAX_RETRIES):
            try:
                if attempt > 0:
                    wait_time = self.RETRY_DELAY * attempt
                    print(
                        f"Retry {attempt}/{self.MAX_RETRIES - 1} after {wait_time}s..."
                    )
                    time.sleep(wait_time)
                elif delay > 0:
                    time.sleep(delay)

                response = session.get(url, timeout=30)
                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                if response and response.status_code == 429:
                    if attempt < self.MAX_RETRIES - 1:
                        print("Rate limited (429). Retrying...")
                        continue
                    else:
                        print(f"Rate limited after {self.MAX_RETRIES} attempts.")
                        return None
                else:
                    print(f"HTTP Error for {url}: {e}")
                    return None

            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")
                return None

        return None

    def _get_product_urls_from_sitemap(
        self, session: requests.Session, delay: float
    ) -> list[str]:
        """Discover all product URLs from the sitemap"""
        print("Fetching product URLs from sitemap...")
        response = self._fetch_with_retry(session, self.SITEMAP_URL, delay)

        if not response:
            print("Warning: Could not fetch sitemap")
            return []

        # Parse XML sitemap
        try:
            soup = BeautifulSoup(response.content, "xml")
        except Exception:
            soup = BeautifulSoup(response.content, "html.parser")

        urls = []
        for loc in soup.find_all("loc"):
            url = loc.get_text(strip=True)
            if "/products/" in url and self._is_filament_product(url):
                urls.append(url)

        print(f"  Found {len(urls)} filament product URLs in sitemap")
        return urls

    def _is_filament_product(self, url: str) -> bool:
        """Check if URL is likely a filament product (not accessories)"""
        exclude_patterns = [
            "dryer",
            "enclosure",
            "nozzle",
            "hotend",
            "extruder",
            "kit",
            "tool",
            "plate",
            "bed",
            "gift",
            "bundle",
        ]
        url_lower = url.lower()
        return not any(pattern in url_lower for pattern in exclude_patterns)

    def _extract_material_from_url(self, url: str) -> str:
        """Extract material type from product URL or title"""
        url_lower = url.lower()

        # Check for specific material patterns in URL
        material_patterns = [
            ("petg", "PETG"),
            ("pla+", "PLA+"),
            ("pla-plus", "PLA+"),
            ("pla", "PLA"),
            ("abs", "ABS"),
            ("asa", "ASA"),
            ("tpu", "TPU"),
            ("pc", "PC"),
            ("silk", "PLA Silk"),
            ("matte", "PLA Matte"),
        ]

        for pattern, material in material_patterns:
            if pattern in url_lower:
                return material

        return "PLA"  # Default

    def _parse_product_page(
        self, session: requests.Session, product_url: str, delay: float
    ) -> list[dict[str, Any]]:
        """Parse a product page to extract filament colors from data-hex_code attributes"""
        filaments = []

        response = self._fetch_with_retry(session, product_url, delay)
        if not response:
            return filaments

        soup = BeautifulSoup(response.text, "html.parser")

        # Get product title for material detection and logging
        title_tag = soup.find("h1") or soup.find("title")
        product_title = title_tag.get_text(strip=True) if title_tag else product_url

        # Extract material from title or URL
        material = self._extract_material_from_title(product_title)
        if material == "PLA":
            material = self._extract_material_from_url(product_url)

        # Find all labels with data-hex_code attribute
        # Structure: <label data-hex_code="#142B4B"><span class="js-value">Starry Blue</span></label>
        color_labels = soup.find_all("label", attrs={"data-hex_code": True})

        if color_labels:
            print(f"  Found {len(color_labels)} colors in: {product_title[:50]}...")
            for label in color_labels:
                hex_code = label.get("data-hex_code", "").strip()

                # Get color name from span with js-value class
                color_span = label.find("span", class_="js-value")
                if color_span:
                    color_name = color_span.get_text(strip=True)
                else:
                    # Fallback: try to get text from label
                    color_name = label.get_text(strip=True)

                # Validate hex code format
                if hex_code and re.match(r"^#?[0-9A-Fa-f]{6}$", hex_code):
                    if not hex_code.startswith("#"):
                        hex_code = f"#{hex_code}"
                    hex_code = hex_code.upper()

                    if color_name:
                        filament = {
                            "manufacturer": "Overture",
                            "material": material,
                            "color": color_name,
                            "hex": hex_code,
                            "link": product_url,
                        }
                        filaments.append(filament)
                        print(f"    {color_name}: {hex_code}")

            # Fix any swapped Black/White hex codes
            filaments = self._fix_swapped_black_white(filaments)

        return filaments

    def _fix_swapped_black_white(
        self, filaments: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Fix swapped Black/White hex codes.

        Some product pages have Black and White hex codes incorrectly swapped.
        This detects when Black has a light hex or White has a dark hex and fixes it.
        """
        # Find Black and White entries
        black_entry = None
        white_entry = None

        for filament in filaments:
            color_lower = filament["color"].lower()
            if color_lower == "black":
                black_entry = filament
            elif color_lower == "white":
                white_entry = filament

        # If we have both, check if they're swapped
        if black_entry and white_entry:
            black_lum = _hex_to_luminance(black_entry["hex"])
            white_lum = _hex_to_luminance(white_entry["hex"])

            # Black should be dark (luminance < 0.5), White should be light (luminance > 0.5)
            # If Black is lighter than White, they're swapped
            if black_lum > white_lum:
                print("    [FIX] Swapped Black/White hex codes detected, correcting...")
                black_entry["hex"], white_entry["hex"] = (
                    white_entry["hex"],
                    black_entry["hex"],
                )

        return filaments

    def _extract_material_from_title(self, title: str) -> str:
        """Extract material type from product title"""
        title_upper = title.upper()

        # Order matters - check more specific patterns first
        material_patterns = [
            ("PETG", "PETG"),
            ("PLA+", "PLA+"),
            ("PLA PLUS", "PLA+"),
            ("SILK PLA", "PLA Silk"),
            ("PLA SILK", "PLA Silk"),
            ("MATTE PLA", "PLA Matte"),
            ("PLA MATTE", "PLA Matte"),
            ("PLA", "PLA"),
            ("ABS", "ABS"),
            ("ASA", "ASA"),
            ("TPU", "TPU"),
            ("PC", "PC"),
            ("NYLON", "PA"),
        ]

        for pattern, material in material_patterns:
            if pattern in title_upper:
                return material

        return "PLA"  # Default

    def fetch(
        self,
        delay: float = None,
        product_urls: list[str] = None,
        max_products: int = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Fetch filament data from overture3d.com

        Args:
            delay: Delay in seconds between requests (default: 1.0)
            product_urls: Direct list of product URLs to scrape (overrides sitemap)
            max_products: Maximum number of products to fetch (for testing)

        Returns:
            Dictionary containing the scraped filament data
        """
        if delay is None:
            delay = self.DEFAULT_DELAY

        print("Starting Overture scraper...")
        print(f"Using {delay}s delay between requests...")

        session = self._get_session()

        filaments_data = {
            "source_url": self.site_url,
            "source_name": self.site_name,
            "filaments": [],
        }

        # Discover product URLs from sitemap if not provided
        if product_urls is None:
            product_urls = self._get_product_urls_from_sitemap(session, delay)

        if max_products:
            product_urls = product_urls[:max_products]
            print(f"Limited to {max_products} products for testing")

        # Process product URLs
        print(f"Processing {len(product_urls)} product URLs...")
        for i, url in enumerate(product_urls, 1):
            print(f"\n[{i}/{len(product_urls)}] {url}")
            filaments = self._parse_product_page(session, url, delay)
            filaments_data["filaments"].extend(filaments)

        print(f"\nTotal filaments found: {len(filaments_data['filaments'])}")
        return filaments_data
