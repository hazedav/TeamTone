# Plan: Add Filament Types as First-Class Citizens

## Problem Statement
TeamTone currently mixes different filament types (PLA, PETG, ASA, ABS, etc.) in the same recommendation set. Users can't print a project using mixed materials, so recommendations should be filtered by filament type.

## Solution Overview
Add `filament_types.yaml` and `filament_types.py` to define base types and classify materials using **prefix matching**. No need to list every variant - "PLA Silk", "PLA Matte", "PLA CF" all match to **PLA**.

---

## Files to Create

### 1. `teamtone/filament_types.yaml`
Simple configuration defining base types only.

```yaml
# Base filament types - variants are detected via prefix matching
base_types:
  - PLA
  - PETG
  - ABS
  - ASA
  - TPU
  - PC
  - PA
  - PET
  - HIPS
  - PVA
  - PP
  - CPE
  - PCTG

# Materials that don't match any prefix go here
default_type: OTHER
```

### 2. `teamtone/filament_types.py`
Module for classification using prefix matching.

**Key Functions:**
```python
def get_base_types() -> List[str]:
    """Returns ['ABS', 'ASA', 'PA', 'PC', 'PETG', 'PLA', 'TPU', ...]"""

def classify_material(material: str) -> str:
    """Classify by prefix: 'PLA Silk' -> 'PLA', 'PETG Basic' -> 'PETG'"""
    # Check if material starts with any base type
    for base_type in base_types:
        if material.upper().startswith(base_type):
            return base_type
    return "OTHER"

def is_filament_type(material: str, base_type: str) -> bool:
    """Check if material belongs to type"""
```

---

## Files to Modify

### 3. `teamtone/filament_colors.py`
Add type-filtered query functions.

**New Functions:**
```python
def get_filaments_by_hex_and_type(hex_code: str, filament_type: Optional[str] = None) -> List[Dict]

def find_similar_filament_colors_by_type(
    target_hex: str,
    limit: int = 3,
    filament_type: Optional[str] = None
) -> List[Tuple[Dict, float]]
```

### 4. `teamtone/main.py`
Add filament type selection to CLI flow.

**New Function:**
```python
def select_filament_type() -> Optional[str]:
    """Prompt user to select a filament type."""
    # Shows: 0. All types, 1. PLA, 2. PETG, etc.
```

**Modified Flow:**
```
1. Select League
2. Select Team
3. Select Filament Type (or "All")  <-- NEW
4. Display filaments of selected type only
```

This flow lets users first identify their team, then filter by the filament type they plan to use.

**Modified Function:**
```python
def display_team_colors(team_name, league, filament_type=None):
    # Filter matches by type if specified
```

---

## Implementation Steps

0. **Save this plan to `plans/filament-types.md`**
   - Engineering requirements document and PR description

1. **Create `filament_types.yaml`**
   - Define base types list: PLA, PETG, ABS, ASA, TPU, PC, PA, PET, HIPS, PVA, PP, CPE, PCTG
   - Classification uses prefix matching (no variant lists needed)

2. **Create `filament_types.py`**
   - Load base types from YAML
   - Implement `classify_material()` using prefix matching
   - Implement `get_base_types()` and `is_filament_type()` helpers

3. **Update `filament_colors.py`**
   - Add `get_filaments_by_hex_and_type()`
   - Add `find_similar_filament_colors_by_type()`
   - Keep existing functions unchanged for backward compatibility

4. **Update `main.py`**
   - Add `select_filament_type()` function
   - Modify `display_team_colors()` to accept `filament_type` parameter
   - Update main loop: after team is selected, prompt for filament type before displaying results

5. **Create tests in `tests/test_filament_types.py`**
   - Test prefix classification: "PLA Silk" -> "PLA", "PETG Basic" -> "PETG"
   - Test unknown materials return "OTHER"
   - Test integration with filament_colors filtering

---

## Example Output (After Implementation)

```
======================================================================
  Chicago Blackhawks (NHL) [PLA]
======================================================================

Team Colors:
  - Red: #CF0A2C
  - Black: #000000
  - White: #FFFFFF

----------------------------------------------------------------------
Matching Filaments (PLA only):
----------------------------------------------------------------------

Red (#CF0A2C):
  Closest 3 match(es):
    - Hatchbox - PLA Matte - Cherry Red - #D2042D (98.6% + 5.0 rank)
    - Polymaker - PLA - Wine Red - #D60212 (96.2% + 5.6 rank)
    - eSUN - PLA Basic - Red - #E72F1D (94.1% + 4.5 rank)
```

---

## Verification
1. Run CLI and verify type selection appears after team selection
2. Select "PLA" and verify only PLA variants appear in results
3. Select "All types" and verify mixed results (existing behavior)
4. Run `pytest tests/` to verify all tests pass
