import sys
from pathlib import Path

# The API modules live one level up and are imported flat, as in the container
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
