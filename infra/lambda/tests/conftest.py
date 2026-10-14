import sys
from pathlib import Path

# Lambda modules live one level up and are imported flat, as in the deployed zip
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
