# utils.py
import os
import random

ICON_DIR = os.path.join(os.environ.get("RIGGING_TOOL_ROOT", ""), "CharacterPicker", "Icons")


def get_random_icon(icon_dir=ICON_DIR, icons=None):
    """Return a random icon path."""
    if icons is None:
        icons = ["unknownMan.svg", "unknownWoman.svg"]
    return os.path.join(icon_dir, random.choice(icons))
