#!/usr/bin/env python3
"""
SimpleNote to Obsidian Import Script
Entry point for running the importer
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simplenote_importer import main

if __name__ == "__main__":
    main()