"""Scraper for us.polymaker.com"""

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


class PolymakerScraper(FilamentScraper):
    """Scraper for us.polymaker.com Shopify store"""

    # Chrome user agent to avoid being blocked
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

    # Default delay between requests (seconds)
    DEFAULT_DELAY = 1.0

    # Retry configuration for rate limiting
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0

    # Products sitemap URL (with required params from main sitemap)
    SITEMAP_URL = "https://us.polymaker.com/sitemap_products_1.xml?from=6616970690617&to=8101790285881"

    @property
    def site_name(self) -> str:
        return "us.polymaker.com"

    @property
    def site_url(self) -> str:
        return "https://us.polymaker.com"

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
                    print(f"Retry {attempt}/{self.MAX_RETRIES - 1} after {wait_time}s...")
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

    def _get_product_urls(self, session: requests.Session) -> list[str]:
        """Get all product URLs from sitemap"""
        print("Fetching product sitemap...")
        response = self._fetch_with_retry(session, self.SITEMAP_URL, 0)
        if not response:
            # Fallback: try the main sitemap to find products sitemap
            main_sitemap = self._fetch_with_retry(
                session, f"{self.site_url}/sitemap.xml", 0
            )
            if main_sitemap:
                try:
                    soup = BeautifulSoup(main_sitemap.content, "xml")
                except Exception:
                    soup = BeautifulSoup(main_sitemap.content, "html.parser")
                for loc in soup.find_all("loc"):
                    if "sitemap_products" in loc.text:
                        response = self._fetch_with_retry(session, loc.text, 0.5)
                        break

        if not response:
            print("Error: Could not fetch product sitemap")
            return []

        # Use html.parser as fallback if lxml not installed
        try:
            soup = BeautifulSoup(response.content, "xml")
        except Exception:
            soup = BeautifulSoup(response.content, "html.parser")
        urls = []

        for url_tag in soup.find_all("url"):
            loc = url_tag.find("loc")
            if loc and "/products/" in loc.text:
                # Filter out non-filament products
                product_url = loc.text
                if self._is_filament_product(product_url):
                    urls.append(product_url)

        print(f"Found {len(urls)} filament product URLs")
        return urls

    def _is_filament_product(self, url: str) -> bool:
        """Check if URL is likely a filament product (not accessories)"""
        # Exclude known non-filament products
        exclude_patterns = [
            "polybox",
            "polydryer",
            "nebulizer",
            "gift-card",
            "sample-box",
            "creator-spool",
            "bundle",
            "pack",
        ]
        url_lower = url.lower()
        return not any(pattern in url_lower for pattern in exclude_patterns)

    def _extract_material_type(self, product_title: str) -> str:
        """Extract material type from product title"""
        title_upper = product_title.upper()

        # Map of patterns to material types
        material_patterns = [
            ("PLA", "PLA"),
            ("PETG", "PETG"),
            ("ABS", "ABS"),
            ("ASA", "ASA"),
            ("TPU", "TPU"),
            ("PC", "PC"),
            ("COPA", "PA"),
            ("PA12", "PA12"),
            ("PA6", "PA6"),
            ("PA612", "PA612"),
            ("PPS", "PPS"),
            ("PET", "PET"),
            ("PBT", "PBT"),
        ]

        for pattern, material in material_patterns:
            if pattern in title_upper:
                return material

        return "PLA"  # Default to PLA for Polymaker products

    def _parse_product_page(
        self, session: requests.Session, product_url: str, delay: float
    ) -> list[dict[str, Any]]:
        """Parse a product page to extract filament data with hex codes"""

        filaments = []

        # Fetch both the product JSON and the HTML page
        json_url = f"{product_url}.json"
        json_response = self._fetch_with_retry(session, json_url, delay)
        html_response = self._fetch_with_retry(session, product_url, delay * 0.3)

        if not json_response:
            return filaments

        try:
            product_data = json_response.json().get("product", {})
        except (ValueError, KeyError):
            return filaments

        product_title = product_data.get("title", "")
        material = self._extract_material_type(product_title)
        variants = product_data.get("variants", [])

        print(f"  Processing: {product_title} ({len(variants)} variants)")

        # Extract variant hex codes from the HTML page metafields
        variant_hex_map = {}
        if html_response:
            variant_hex_map = self._extract_variant_hex_codes(html_response.text)

        # Build variant ID to color name mapping, dedupe by color
        seen_colors = set()
        for variant in variants:
            variant_id = str(variant.get("id"))
            # Parse color from variant title (format: "1.75mm / 1kg / Black" - color is LAST)
            title_parts = variant.get("title", "").split(" / ")
            # Color is typically the last part, skip size/weight parts
            color_name = None
            for part in reversed(title_parts):
                if part not in ["1.75mm", "2.85mm", "1kg", "3kg", "Default Title"]:
                    color_name = part
                    break

            # Skip if no color found or already seen
            if not color_name or color_name in seen_colors:
                continue

            # Get hex code from the map
            hex_code = variant_hex_map.get(variant_id)

            if hex_code:
                seen_colors.add(color_name)
                filament = {
                    "manufacturer": "Polymaker",
                    "material": material,
                    "color": color_name,
                    "hex": hex_code,
                    "link": f"{product_url}?variant={variant_id}",
                }
                filaments.append(filament)
                print(f"    Found: {color_name} -> {hex_code}")

        return filaments

    def _extract_variant_hex_codes(self, html: str) -> dict[str, str]:
        """Extract hex codes for all variants from page HTML metafields"""
        variant_hex_map = {}

        # Pattern to find variant IDs with hex_code in metafields
        # The structure is: "variant_id": {...metafields...{..."hex_code":"#XXXXXX"...}}
        # Use a simpler pattern that matches the variant ID followed by hex_code
        # Variant IDs are 14+ digit numbers
        pattern = r'"(\d{14,})"[^}]*?"hex_code"[:\s]*"(#?[0-9A-Fa-f]{6})"'

        matches = re.findall(pattern, html)
        for variant_id, hex_code in matches:
            # Normalize hex code
            if not hex_code.startswith("#"):
                hex_code = f"#{hex_code}"
            hex_code = hex_code.upper()
            variant_hex_map[variant_id] = hex_code

        return variant_hex_map

    def _extract_hex_from_page(self, html: str) -> str | None:
        """Extract hex code from page HTML"""
        # Pattern 1: "Hex Code: #XXXXXX" or "HEX Code: #XXXXXX"
        patterns = [
            r"[Hh][Ee][Xx]\s*[Cc]ode[:\s]+#?([0-9A-Fa-f]{6})",
            r"[Hh][Ee][Xx][:\s]+#?([0-9A-Fa-f]{6})",
            r'"hex_code"[:\s]+"#?([0-9A-Fa-f]{6})"',
            r'"hexCode"[:\s]+"#?([0-9A-Fa-f]{6})"',
            r"color[_-]?hex[:\s]+#?([0-9A-Fa-f]{6})",
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                hex_value = match.group(1).upper()
                return f"#{hex_value}"

        return None

    def fetch(
        self,
        delay: float = None,
        max_products: int = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Fetch filament data from us.polymaker.com

        Args:
            delay: Delay in seconds between requests (default: 1.0)
            max_products: Maximum number of products to fetch (for testing)

        Returns:
            Dictionary containing the scraped filament data
        """
        if delay is None:
            delay = self.DEFAULT_DELAY

        print("Starting Polymaker scraper...")
        print(f"Using {delay}s delay between requests...")

        session = self._get_session()
        product_urls = self._get_product_urls(session)

        if max_products:
            product_urls = product_urls[:max_products]
            print(f"Limited to {max_products} products for testing")

        filaments_data = {
            "source_url": self.site_url,
            "source_name": self.site_name,
            "filaments": [],
        }

        for i, url in enumerate(product_urls, 1):
            print(f"\n[{i}/{len(product_urls)}] {url}")
            filaments = self._parse_product_page(session, url, delay)
            filaments_data["filaments"].extend(filaments)

        print(f"\nTotal filaments found: {len(filaments_data['filaments'])}")
        return filaments_data
