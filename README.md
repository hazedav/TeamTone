# TeamTone

![CI](https://github.com/your-username/teamtone/actions/workflows/ci.yml/badge.svg)

**TeamTone** is a tool that helps makers match their favorite sports teams' official colors with real-world 3D printer filaments.

Instead of guessing which filament is “close enough,” TeamTone analyzes team color palettes and compares them against filament color catalogs to identify the closest matches using objective color-distance calculations.

Print your team. Perfectly matched.

---

## 🏟️ What TeamTone Does

* Takes a sports team's official colors (RGB / HEX)
* Compares them against 18,470+ available 3D printer filament colors
* Calculates the closest visual match using LAB color space (perceptual accuracy)
* Returns ranked filament recommendations with similarity percentages
* Provides direct purchase links and printing temperature recommendations
* Prioritizes widely-available filaments from top manufacturers

Perfect for:

* Team logos and emblems
* Fan gear and accessories
* Signs, badges, and decor
* Stadium models and dioramas
* Any print where color accuracy matters

---

## ✨ Features

* 🎨 Accurate color matching using color-distance calculations (LAB color space with ΔE metric)
* 🏟️ Supports teams with multi-color palettes
* 🧵 18,470+ filament colors from 716 manufacturers
* 🔍 Ranks filament matches by closeness (similarity percentage)
* 🛒 Purchase links included for easy ordering (62% of filaments)
* ⭐ Prioritizes top 10 manufacturers for better availability
* 🌡️ Temperature recommendations (hotend & bed) where available
* 🛠️ Maker-friendly and easy to extend

---

## 🧠 How It Works (High Level)

1. Team colors are loaded in RGB or HEX format
2. Filament colors are normalized into the same color space
3. Colors are converted into a perceptual color space (such as LAB)
4. A color-distance metric is applied to find the closest matches
5. Results are ranked and returned per team color

---

## 🚀 Getting Started

> **Note:** Installation and usage instructions may vary depending on how you deploy TeamTone (CLI, library, or web app).

### Clone the Repository

```bash
git clone https://github.com/your-username/teamtone.git
cd teamtone
```

### Install Dependencies

```bash
# Using uv (recommended)
uv sync
```

### Run TeamTone

```bash
# Interactive CLI - select league and team, see matching filaments
python run_teamtone.py

# Or run as a module
python -m teamtone.main
```

---

## 📊 Example Output

```text
======================================================================
  Los Angeles Lakers (NBA)
======================================================================

Team Colors:
  - Purple: #552583
  - Gold: #FDB927
  - Black: #000000

----------------------------------------------------------------------
Matching Filaments:
----------------------------------------------------------------------

Purple (#552583):
  No exact matches found
  Closest 3 match(es):
    - add:north - PLA Economy - Glitz Purple - #57257F (97.5% similar)
    - ELEGOO - PLA Silk Triple - Blue / Purple / Black - #57217D,#1450A1,#292D34 (97.3% similar)
    - Geeetech - PETG Basic - Purple - #4B267E (95.7% similar)

  Nearest match with purchase link:
    - Polymaker - PolyTerra PLA Matte - Lavender Purple - #5F2A84 (96.8% similar) [https://us.polymaker.com/products/...]

  Nearest match from top manufacturer:
    - eSUN - PLA+ - Purple - #5A2F8D (96.2% similar) [https://www.amazon.com/dp/B01EKEMFQS]

Gold (#FDB927):
  No exact matches found
  Closest 3 match(es):
    - eSUN - PLA Glitter - eTwinkling Gold - #FFBB29 (99.3% similar) [https://www.esun3d.com/...]
    - FlashForge - ABS Pro - Yellow - #FFBD2C (98.3% similar)
    - SUNLU - PLA Basic - Transparent Orange - #F8B525 (98.2% similar)

  Nearest match from top manufacturer:
    - Hatchbox - PLA - True Gold - #FFB521 (98.9% similar) [https://www.amazon.com/dp/B00UEYJZ4O]

Black (#000000):
  Found 1449 exact match(es), showing top 3:
    - Hatchbox - PLA - Black (Hotend: 210C, Bed: 50C) [https://www.amazon.com/dp/B00J0ECR5I]
    - eSUN - PLA+ - Black (Hotend: 205C, Bed: 60C) [https://www.esun3d.com/pla-pro-product/]
    - Polymaker - PolyLite PLA - Black (Hotend: 215C, Bed: 60C) [https://us.polymaker.com/...]
```

---

## 🧵 Supported Filaments

TeamTone currently includes **18,470+ filament colors** from **716 manufacturers**, sourced from:

* **3dfilamentprofiles.com** - Community-maintained database
* **FilamentColors.xyz** - Colorimeter-measured samples with temperature data
* Support for all material types: PLA, PETG, ABS, TPU, Nylon, and more

The database is organized by manufacturer, making it easy to filter or search by brand. Scrapers are included to keep data up-to-date.

---

## 🛣️ Roadmap

* [x] Purchase links and temperature data
* [x] Top manufacturer prioritization
* [x] Interactive CLI with league/team navigation
* [ ] Add CLI flags for filtering by material or brand
* [ ] Export results as CSV / JSON
* [ ] Web-based UI
* [ ] API endpoint for programmatic access
* [ ] Community-submitted filament data
* [ ] Support for custom team colors

---

## 🤝 Contributing

Contributions are welcome!

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Install dependencies: `uv sync`
4. Make your changes
5. Run the test suite: `make test`
6. Run the linter: `make lint`
7. Format your code: `make format`
8. Submit a pull request with a clear description

### Continuous Integration

All pull requests automatically run:
- Code linting with ruff
- Test suite with pytest

Make sure your changes pass both checks before submitting.

If you're adding filament data or improving color matching, please include sample data and tests where possible.

---

## ⚠️ Disclaimer

Team names, logos, and colors are the property of their respective owners. TeamTone is not affiliated with or endorsed by any sports league or team.

---

## 📄 License

Specify your license here (e.g. MIT, Apache 2.0).

---

## ⭐ Acknowledgements

Built for makers, by makers — and sports fans who care about color accuracy.
