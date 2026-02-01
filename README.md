# TeamTone

![CI](https://github.com/hazedav/TeamTone/actions/workflows/ci.yml/badge.svg)

**TeamTone** is a tool that helps makers match their favorite sports teams' official colors with real-world 3D printer filaments.

Instead of guessing which filament is “close enough,” TeamTone analyzes team color palettes and compares them against filament color catalogs to identify the closest matches using objective color-distance calculations.

Print your team. Perfectly matched.

---

## 🏟️ What TeamTone Does

* Takes a sports team's official colors (RGB / HEX)
* Compares them against 18,038+ available 3D printer filament colors
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
* 🧵 18,038+ filament colors from 716 manufacturers
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
5. Results are ranked by **weighted score** (color similarity + manufacturer bonus)

---

## 📊 Filament Scoring

TeamTone uses a **weighted scoring system** that balances color accuracy with manufacturer reliability. This ensures you get recommendations that are both visually accurate and easy to purchase.

### Weighted Score Formula

```
Weighted Score = Color Similarity (%) + Manufacturer Rank Bonus
```

### Color Similarity

Color similarity is calculated using the **CIELAB color space** with the **ΔE (Delta E)** metric, which measures perceptual color difference. A 100% match means identical colors; lower percentages indicate greater visual difference.

### Manufacturer Rank Bonus

Top manufacturers receive a bonus based on their rank (1-10):

| Rank | Manufacturer | Bonus |
|------|--------------|-------|
| 1 | Polymaker | +5.6 |
| 2 | Hatchbox | +5.0 |
| 3 | eSUN | +4.5 |
| 4 | Prusament | +3.9 |
| 5 | SUNLU | +3.4 |
| 6 | Overture | +2.8 |
| 7 | MatterHackers | +2.2 |
| 8 | ColorFabb | +1.7 |
| 9 | Eryone | +1.1 |
| 10 | Atomic Filament | +0.6 |
| Unranked | Others | +0.0 |

### Why This Matters

The ~5% bonus spread means:
- A **95% similar** match from a **#1 manufacturer** (95 + 5.6 = 100.6) beats a **100% similar** match from an **unranked manufacturer** (100 + 0 = 100)
- You get filaments that are both close in color *and* widely available from trusted brands
- The output transparently shows both components: `(98.6% similar + 5.0 rank bonus)`

### Example

For Chicago Blackhawks Red (#CF0A2C):
```
Closest 3 match(es) (weighted by manufacturer rank):
  - Hatchbox - PLA Matte - Cherry Red - #D2042D (98.6% similar + 5.0 rank bonus)
  - HP 3DF - PLA Silk - Silk Red - #D3102E (98.8% similar)
  - eSUN - PLA+ - Fire Engine Red - #CE2029 (98.1% similar + 4.5 rank bonus)
```

Hatchbox appears first despite 98.6% similarity because its weighted score (103.6) exceeds HP 3DF's unranked score (98.8).

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
  Closest 3 match(es) (weighted by manufacturer rank):
    - eSUN - PLA+ - Purple - #5A2F8D (96.2% similar + 4.5 rank bonus) [https://www.amazon.com/dp/B01EKEMFQS]
    - add:north - PLA Economy - Glitz Purple - #57257F (97.5% similar)
    - Eryone - PLA Silk Triple - Blue / Purple / Black - #57217D,#1450A1,#292D34 (97.3% similar + 1.1 rank bonus)

Gold (#FDB927):
  No exact matches found
  Closest 3 match(es) (weighted by manufacturer rank):
    - Hatchbox - PLA - True Gold - #FFB521 (98.9% similar + 5.0 rank bonus) [https://www.amazon.com/dp/B00UEYJZ4O]
    - eSUN - PLA Glitter - eTwinkling Gold - #FFBB29 (99.3% similar + 4.5 rank bonus) [https://www.esun3d.com/...]
    - SUNLU - PLA Basic - Transparent Orange - #F8B525 (98.2% similar + 3.4 rank bonus)

Black (#000000):
  Found 1449 exact match(es), showing top 3:
    - Hatchbox - PLA - Black (Hotend: 210C, Bed: 50C) [https://www.amazon.com/dp/B00J0ECR5I]
    - eSUN - PLA+ - Black (Hotend: 205C, Bed: 60C) [https://www.esun3d.com/pla-pro-product/]
    - Polymaker - PolyLite PLA - Black (Hotend: 215C, Bed: 60C) [https://us.polymaker.com/...]
```

---

## 🧵 Supported Filaments

TeamTone currently includes **18,038+ filament colors** from **716 manufacturers**, sourced from:

* **3dfilamentprofiles.com** - Community-maintained database
* **us.polymaker.com** - Official Polymaker store with hex codes from product pages
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
3. Install dependencies: `make install`
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
