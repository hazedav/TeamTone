#!/usr/bin/env python3
"""
TeamTone CLI Runner
Quick script to launch the interactive team color matcher
"""

import sys
from pathlib import Path

# Add teamtone to path
sys.path.insert(0, str(Path(__file__).parent))

from teamtone.main import main

if __name__ == "__main__":
    main()
