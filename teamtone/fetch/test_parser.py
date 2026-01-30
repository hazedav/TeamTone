#!/usr/bin/env python3
"""Test the updated parser"""

from bs4 import BeautifulSoup
import sys
sys.path.insert(0, '.')

from filament_sites.filamentprofiles import FilamentProfilesScraper

print("Loading HTML...")
with open('filaments.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Parsing HTML...")
soup = BeautifulSoup(html, 'html.parser')

print("Creating scraper...")
scraper = FilamentProfilesScraper()

print("Extracting filaments...")
filaments = scraper._parse_filaments(soup)

print(f"\nTotal filaments found: {len(filaments)}")

if filaments:
    print("\nFirst 5 filaments:")
    for i, f in enumerate(filaments[:5]):
        print(f"\n{i+1}. {f['manufacturer']} - {f['material']}")
        print(f"   Color: {f['color']}")
        print(f"   Hex: {f['hex']}")

    # Look for Abaflex
    print("\n" + "="*80)
    print("SEARCHING FOR ABAFLEX")
    print("="*80)
    abaflex = [f for f in filaments if 'Abaflex' in f['manufacturer']]
    if abaflex:
        print(f"\nFound {len(abaflex)} Abaflex filament(s):")
        for f in abaflex:
            print(f"\n  Manufacturer: {f['manufacturer']}")
            print(f"  Material: {f['material']}")
            print(f"  Color: {f['color']}")
            print(f"  Hex: {f['hex']}")

            # Check if it matches expected values
            if (f['manufacturer'] == 'Abaflex' and
                'PETG+' in f['material'] and
                f['color'] == 'Transparent' and
                f['hex'] == '#BEC3C6'):
                print("\n  ✓ MATCHES EXPECTED VALUES!")
            else:
                print("\n  ✗ Does not match expected values")
                print(f"     Expected: Abaflex, PETG+ Translucent, Transparent, #BEC3C6")
    else:
        print("\n✗ Abaflex not found!")
else:
    print("\n✗ No filaments found!")
