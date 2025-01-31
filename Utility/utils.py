# utils.py
import random
from pathlib import Path
import os

ICON_DIR = Path(os.environ["RIGGING_TOOL_ROOT"]) / "CharacterPicker" / "Icons"

def get_random_icon(icon_dir=ICON_DIR, icons=None):
    """Return a random icon path using pathlib for better cross-platform compatibility."""
    if icons is None:
        icons = ["unknownMan.svg", "unknownWoman.svg"]
    
    return str(icon_dir / random.choice(icons))
