"""Scraper for store.sunlu.com"""

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


class SunluScraper(FilamentScraper):
    """Scraper for store.sunlu.com Shopify store"""

    # Chrome user agent to avoid being blocked
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

    # Default delay between requests (seconds)
    DEFAULT_DELAY = 1.0

    # Retry configuration for rate limiting
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0

    # Products sitemap URL
    SITEMAP_URL = "https://store.sunlu.com/sitemap_products_1.xml?from=4750103609430&to=10079275385114"

    # Collection URLs - each collection represents a material type
    COLLECTIONS = {
        "PLA": "https://store.sunlu.com/collections/pla",
        "PETG": "https://store.sunlu.com/collections/petg",
        "ABS": "https://store.sunlu.com/collections/abs",
        "ASA": "https://store.sunlu.com/collections/asa",
        "TPU": "https://store.sunlu.com/collections/tpu",
        "PLA+": "https://store.sunlu.com/collections/pla-plus",
    }

    @property
    def site_name(self) -> str:
        return "store.sunlu.com"

    @property
    def site_url(self) -> str:
        return "https://store.sunlu.com"

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
            if "/products/" in url:
                urls.append(url)

        print(f"  Found {len(urls)} product URLs in sitemap")
        return urls

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

    def _get_product_urls_from_collection(
        self, session: requests.Session, collection_url: str, delay: float
    ) -> list[str]:
        """Get all product URLs from a collection page"""
        product_urls = []
        page = 1

        while True:
            url = f"{collection_url}?page={page}"
            print(f"  Fetching collection page {page}...")
            response = self._fetch_with_retry(session, url, delay)

            if not response:
                break

            soup = BeautifulSoup(response.text, "html.parser")

            # Find product links - Shopify stores typically use these patterns
            found_products = False
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "/products/" in href and href not in product_urls:
                    # Normalize URL
                    if href.startswith("/"):
                        href = f"{self.site_url}{href}"
                    product_urls.append(href)
                    found_products = True

            # Check if there's a next page
            if not found_products:
                break

            # Look for pagination - if no next page link, we're done
            next_link = soup.find("a", {"rel": "next"}) or soup.find(
                "a", string=re.compile(r"next", re.I)
            )
            if not next_link:
                break

            page += 1

        return product_urls

    def _extract_material_from_url(self, url: str) -> str:
        """Extract material type from product URL or title"""
        url_lower = url.lower()

        # Check collection path
        if "/collections/pla-plus" in url_lower or "pla+" in url_lower:
            return "PLA+"
        if "/collections/pla" in url_lower:
            return "PLA"
        if "/collections/petg" in url_lower:
            return "PETG"
        if "/collections/abs" in url_lower:
            return "ABS"
        if "/collections/asa" in url_lower:
            return "ASA"
        if "/collections/tpu" in url_lower:
            return "TPU"

        # Check product URL for material keywords
        if "petg" in url_lower:
            return "PETG"
        if "pla+" in url_lower or "pla-plus" in url_lower:
            return "PLA+"
        if "pla" in url_lower:
            return "PLA"
        if "abs" in url_lower:
            return "ABS"
        if "asa" in url_lower:
            return "ASA"
        if "tpu" in url_lower:
            return "TPU"

        return "PLA"  # Default

    def _parse_color_table(self, soup: BeautifulSoup) -> list[tuple[str, str]]:
        """
        Parse color/hex table from product page.

        SUNLU product pages have tables with structure:
        <tr>
          <td>Black</td>
          <td>#000000</td>
          <td style="background-color: #000000;"></td>
        </tr>
        """
        colors = []

        # Find all tables in the page
        for table in soup.find_all("table"):
            rows = table.find_all("tr")

            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    # First cell: color name, second cell: hex code
                    color_name = cells[0].get_text(strip=True)
                    hex_cell = cells[1].get_text(strip=True)

                    # Validate hex code format
                    if re.match(r"^#?[0-9A-Fa-f]{6}$", hex_cell):
                        hex_code = hex_cell if hex_cell.startswith("#") else f"#{hex_cell}"
                        hex_code = hex_code.upper()

                        # Skip header rows or empty names
                        if color_name and color_name.lower() not in ["color", "colour", "name"]:
                            colors.append((color_name, hex_code))

        return colors

    def _parse_product_page(
        self, session: requests.Session, product_url: str, material: str, delay: float
    ) -> list[dict[str, Any]]:
        """Parse a product page to extract filament colors from table"""
        filaments = []

        response = self._fetch_with_retry(session, product_url, delay)
        if not response:
            return filaments

        soup = BeautifulSoup(response.text, "html.parser")

        # Get product title for logging
        title_tag = soup.find("h1") or soup.find("title")
        product_title = title_tag.get_text(strip=True) if title_tag else product_url

        # Extract colors from table
        colors = self._parse_color_table(soup)

        if colors:
            print(f"  Found {len(colors)} colors in: {product_title[:50]}...")
            for color_name, hex_code in colors:
                filament = {
                    "manufacturer": "SUNLU",
                    "material": material,
                    "color": color_name,
                    "hex": hex_code,
                    "link": product_url,
                }
                filaments.append(filament)
                print(f"    {color_name}: {hex_code}")

        return filaments

    def fetch(
        self,
        delay: float = None,
        collections: list[str] = None,
        product_urls: list[str] = None,
        max_products: int = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Fetch filament data from store.sunlu.com

        Args:
            delay: Delay in seconds between requests (default: 1.0)
            collections: List of collection names to scrape (default: all)
            product_urls: Direct list of product URLs to scrape (overrides collection discovery)
            max_products: Maximum number of products to fetch (for testing)

        Returns:
            Dictionary containing the scraped filament data
        """
        if delay is None:
            delay = self.DEFAULT_DELAY

        print("Starting SUNLU scraper...")
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

        # Process product URLs
        if product_urls:
            print(f"Processing {len(product_urls)} product URLs...")
            colors_found = 0
            for i, url in enumerate(product_urls, 1):
                if max_products and i > max_products:
                    break
                print(f"\n[{i}/{len(product_urls)}] {url}")
                material = self._extract_material_from_url(url)
                filaments = self._parse_product_page(session, url, material, delay)
                if filaments:
                    colors_found += len(filaments)
                filaments_data["filaments"].extend(filaments)

            print(f"\nPages with color tables: {colors_found > 0}")

        else:
            # Discover products from collections
            if collections is None:
                collections = list(self.COLLECTIONS.keys())

            all_urls = []
            for collection_name in collections:
                if collection_name not in self.COLLECTIONS:
                    print(f"Unknown collection: {collection_name}")
                    continue

                collection_url = self.COLLECTIONS[collection_name]
                print(f"\nDiscovering products from {collection_name} collection...")
                urls = self._get_product_urls_from_collection(session, collection_url, delay)
                print(f"  Found {len(urls)} products")

                for url in urls:
                    if url not in all_urls:
                        all_urls.append((url, collection_name))

            if max_products:
                all_urls = all_urls[:max_products]
                print(f"\nLimited to {max_products} products for testing")

            print(f"\nTotal unique products to process: {len(all_urls)}")

            for i, (url, material) in enumerate(all_urls, 1):
                print(f"\n[{i}/{len(all_urls)}] {url}")
                filaments = self._parse_product_page(session, url, material, delay)
                filaments_data["filaments"].extend(filaments)

        print(f"\nTotal filaments found: {len(filaments_data['filaments'])}")
        return filaments_data
