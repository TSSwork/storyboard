import sys
from pathlib import Path

# The app lives next to this folder: ../research-story
APP = Path(__file__).resolve().parents[2] / "research-story"
sys.path.insert(0, str(APP))
