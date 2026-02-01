# Claude Code Instructions

## Project Overview
TeamTone matches sports team colors to 3D printer filaments using LAB color space calculations.

## Before Committing
Always run linting before considering work complete:
```bash
make lint
```

Fix any linting errors before committing.

## Code Style
- Follow existing patterns in the codebase
- Use type hints for function signatures
- Keep functions focused and well-documented
- Tests go in `teamtone/test_*.py` following pytest conventions

## Testing
Run tests before committing:
```bash
make test
```

## Key Files
- `teamtone/main.py` - CLI entry point
- `teamtone/filament_colors.py` - Color matching functions
- `teamtone/filament_types.py` - Filament type classification
- `teamtone/filament_scoring.py` - Weighted scoring system
- `teamtone/filaments/*.yaml` - Filament color data (716 manufacturers)
- `teamtone/teams/*.yaml` - Team color data (5 leagues)
