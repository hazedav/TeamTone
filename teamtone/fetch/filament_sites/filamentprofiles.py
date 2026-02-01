"""Scraper for 3dfilamentprofiles.com"""

import sys
import time
from typing import Any

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install requests beautifulsoup4")
    sys.exit(1)

from .base import FilamentScraper


class FilamentProfilesScraper(FilamentScraper):
    """Scraper for 3dfilamentprofiles.com"""

    # Chrome user agent to avoid being blocked
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

    # Default delay between requests (seconds)
    DEFAULT_DELAY = 1.0

    # Retry configuration for 429 errors
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0

    @property
    def site_name(self) -> str:
        return "3dfilamentprofiles.com"

    @property
    def site_url(self) -> str:
        return "https://3dfilamentprofiles.com"

    def fetch(
        self,
        per_page: int = 100,
        delay: float = None,
        fetch_only: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Fetch filament data from 3dfilamentprofiles.com

        Args:
            per_page: Number of results per page
            delay: Delay in seconds between requests (default: 1.0)
            fetch_only: If True, return raw HTML without parsing

        Returns:
            Dictionary containing the scraped filament data or raw HTML if fetch_only=True
        """
        if delay is None:
            delay = self.DEFAULT_DELAY

        url = f"{self.site_url}/filaments/all?perPage={per_page}"

        print(f"Fetching filament data from {url}...")
        if delay > 0:
            print(f"Using {delay}s throttle delay to prevent rate limiting...")

        # Add custom headers with Chrome user agent
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate" if not fetch_only else "identity",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # Fetch with retry logic for 429 errors
        response = None
        for attempt in range(self.MAX_RETRIES):
            try:
                # Add delay before request (except first attempt)
                if attempt > 0:
                    wait_time = self.RETRY_DELAY * attempt
                    print(
                        f"Retry {attempt}/{self.MAX_RETRIES - 1} after {wait_time}s..."
                    )
                    time.sleep(wait_time)
                elif delay > 0:
                    time.sleep(delay)

                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                break  # Success, exit retry loop

            except requests.exceptions.HTTPError as e:
                if response and response.status_code == 429:
                    if attempt < self.MAX_RETRIES - 1:
                        print("Rate limited (429). Retrying...")
                        continue
                    else:
                        print(f"Rate limited after {self.MAX_RETRIES} attempts.")
                        print(
                            "Try again later or increase the delay with --delay parameter."
                        )
                        sys.exit(1)
                else:
                    print(f"HTTP Error: {e}")
                    sys.exit(1)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                sys.exit(1)

        if response is None:
            print("Failed to fetch data after retries")
            sys.exit(1)

        # If fetch_only mode, return raw HTML without parsing
        if fetch_only:
            # Get encoding information
            detected_encoding = response.encoding or "utf-8"
            content_type = response.headers.get("Content-Type", "unknown")

            print("\nResponse Information:")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {content_type}")
            print(f"  Detected Encoding: {detected_encoding}")
            print(f"  Content Length: {len(response.content):,} bytes")

            return {
                "source_url": url,
                "source_name": self.site_name,
                "raw_html": response.text,
                "raw_html_length": len(response.text),
                "encoding": detected_encoding,
                "content_type": content_type,
            }

        # Parse the HTML
        soup = BeautifulSoup(response.content, "html.parser")

        filaments_data = {
            "source_url": url,
            "source_name": self.site_name,
            "raw_html_length": len(response.text),
            "filaments": [],
        }

        # Extract JSON data from Next.js script tag
        filaments_data["filaments"] = self._parse_filaments(soup)

        if not filaments_data["filaments"]:
            print("Warning: No filaments found. The page structure may have changed.")
            print(
                "You may need to inspect the HTML and update the JSON extraction logic."
            )

        print(f"Found {len(filaments_data['filaments'])} filaments")

        return filaments_data

    def _parse_filaments(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """
        Extract filament data from Next.js JSON embedded in script tags

        The site is a client-side rendered React app with data embedded in
        a script tag. The JSON is escaped with backslashes, so quotes appear
        as \\" instead of ".

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            List of filament dictionaries
        """
        import re

        filaments = []

        # Find all script tags
        scripts = soup.find_all("script")

        for script in scripts:
            script_text = script.string if script.string else ""

            # Look for JSON objects with filament data (escaped format)
            if (
                "brand_name" in script_text
                and "material" in script_text
                and "rgb" in script_text
            ):
                try:
                    # The JSON is escaped, so we need to match: \\"brand_name\\":\\"value\\"
                    # Pattern matches entire JSON objects to extract all fields
                    pattern = r'\{\\"id\\":\d+[^}]*\\"brand_name\\":\\"([^"\\]+)\\"[^}]*\\"material\\":\\"([^"\\]+)\\"[^}]*\\"material_type\\":\\"([^"\\]*)\\"[^}]*\\"color\\":\\"([^"\\]+)\\"[^}]*\\"rgb\\":\\"([^"\\]+)\\"[^}]*\}'

                    matches = re.finditer(pattern, script_text)

                    for match in matches:
                        full_match = match.group(0)
                        brand_name = match.group(1)
                        material = match.group(2)
                        material_type = match.group(3)
                        color = match.group(4)
                        rgb = match.group(5)

                        # Skip manufacturers that have dedicated scrapers
                        if brand_name.lower() == "polymaker":
                            continue

                        filament = {
                            "manufacturer": brand_name,
                            "material": material,
                            "color": color,
                            "hex": rgb,
                        }

                        # Add material_type if it's meaningful
                        if material_type and material_type not in (
                            "",
                            "-- Other --",
                            "null",
                        ):
                            # Combine material with type for richer info
                            filament["material"] = f"{material} {material_type}"

                        # Extract website URL if present (primary source)
                        website_match = re.search(
                            r'\\"website\\":\\"(https?://[^"\\]+)\\"', full_match
                        )
                        if website_match:
                            filament["link"] = website_match.group(1)
                        else:
                            # Extract Amazon ASIN from price_data as fallback
                            price_data_match = re.search(
                                r'\\"price_data\\":\{\\"bad\\":\\"([^"\\]+)\\"',
                                full_match,
                            )
                            if price_data_match:
                                asin = price_data_match.group(1)
                                filament["link"] = f"https://www.amazon.com/dp/{asin}"

                        filaments.append(filament)

                    # If we found filaments, we're done
                    if filaments:
                        break

                except (ValueError, AttributeError) as e:
                    print(f"Error parsing filament data: {e}")
                    continue

        return filaments
