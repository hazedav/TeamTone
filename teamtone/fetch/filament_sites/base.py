"""Base interface for filament site scrapers"""

from abc import ABC, abstractmethod
from typing import Any


class FilamentScraper(ABC):
    """Abstract base class for filament data scrapers"""

    @property
    @abstractmethod
    def site_name(self) -> str:
        """Name of the site being scraped"""
        pass

    @property
    @abstractmethod
    def site_url(self) -> str:
        """Base URL of the site"""
        pass

    @abstractmethod
    def fetch(self, **kwargs) -> dict[str, Any]:
        """
        Fetch filament data from the site

        Returns:
            Dictionary containing the scraped filament data with structure:
            {
                "source_url": str,
                "source_name": str,
                "filaments": [
                    {
                        "manufacturer": str,
                        "material": str,
                        "color": str,
                        "hex": str,
                        "temp_hotend": int (optional),
                        "temp_bed": int (optional),
                    },
                    ...
                ]
            }
        """
        pass

    def convert_to_yaml_format(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert scraped data to the YAML format used in filaments.yaml

        Returns structured data ready to be merged with existing filaments.yaml
        """
        yaml_data = {}

        for filament in data.get('filaments', []):
            manufacturer = filament.get('manufacturer', 'Unknown')
            material = filament.get('material', 'PLA')
            color = filament.get('color', 'Unknown')

            # Initialize nested structure
            if manufacturer not in yaml_data:
                yaml_data[manufacturer] = {}
            if material not in yaml_data[manufacturer]:
                yaml_data[manufacturer][material] = {}

            # Add color data
            color_data = {
                'hex': filament.get('hex', '#000000'),
                'source': data.get('source_name', self.site_name)
            }

            if 'temp_hotend' in filament:
                color_data['temp_hotend'] = filament['temp_hotend']
            if 'temp_bed' in filament:
                color_data['temp_bed'] = filament['temp_bed']
            if 'link' in filament:
                color_data['link'] = filament['link']

            yaml_data[manufacturer][material][color] = color_data

        return yaml_data
