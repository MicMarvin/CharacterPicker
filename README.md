# CharacterPicker

CharacterPicker is a PySide2/Qt tool for Autodesk Maya that lets you build and run custom picker UIs for rig controls. It supports multi-character tabs, multiple pages per character, background images, and buttons that run Python, MEL, or selection commands.

## Features

- **Multi-character tabs** with custom icons and rename/close actions
- **Per-character pages** with backgrounds (SVG/PNG/JPG/BMP), scaling, and nudge controls
- **Toolbox-driven edit mode** for adding/updating buttons (shape, color/opacity, size, grid position, orientation)
- **Button command modes**: Python (exec), MEL (with `$pickerWindow` set), or Select (stores/selects a list of controls)
- **Animate vs. Edit mode toggle** (Y), context menus on tabs/pages/grid, and keyboard shortcuts for framing/zoom/delete
- **Save/load pickers** to JSON (see `character.json` sample); logs written to `%APPDATA%/CharacterPicker/logs/character_picker.log`

## Requirements

- Autodesk Maya (PySide2, shiboken2, maya.cmds/mel/OpenMayaUI available)
- Python access to this folder on `PYTHONPATH`/`MAYA_SCRIPT_PATH`
- Environment variable `RIGGING_TOOL_ROOT` pointing to the folder that contains `CharacterPicker/Icons` (usually the repo root)

## Setup

1. Place the `CharacterPicker` folder somewhere on disk (e.g. `Documents/maya/scripts/CharacterPicker`)
2. Ensure that parent folder is on `PYTHONPATH` (or add it in `userSetup.py`)
3. Set `RIGGING_TOOL_ROOT` to the same parent so icons resolve:

```python
import os, sys
root = r"C:/path/to/CharacterPicker"
if root not in sys.path:
    sys.path.append(root)
os.environ["RIGGING_TOOL_ROOT"] = root
```

## Usage

### Launching the Tool

To launch the CharacterPicker tool in Maya, use the following Python command:

```python
import CharacterPicker
CharacterPicker.show()
```

### Basic Workflow

1. **Create a new character tab** using the "+" button in the tab bar
2. **Add pages** to each character tab for different control sets
3. **Set background images** for pages (supports SVG, PNG, JPG, BMP formats)
4. **Add buttons** using the toolbox in edit mode
5. **Configure button commands** (Python, MEL, or Select modes)
6. **Save your picker** using the save functionality

### Editing Mode

- Toggle between **Edit** and **Animate** modes using the Y key or the mode toggle button
- Use **context menus** on tabs, pages, and grid items for quick actions
- **Keyboard shortcuts**:
  - `F` - Frame view to selected item
  - `Delete` - Delete selected item
  - `Ctrl + Mouse Wheel` - Zoom in/out
  - `Ctrl + Click` - Select multiple items

### Command Modes

- **Python**: Execute Python code directly
- **MEL**: Execute MEL commands with `$pickerWindow` variable set
- **Select**: Store and select a list of controls

## File Structure

```
CharacterPicker/
├── __init__.py
├── main.py
├── ui/
│   ├── character_picker_ui.py
│   └── ...
├── icons/
│   ├── character_icon.png
│   └── ...
├── utils/
│   ├── file_handler.py
│   └── ...
└── character.json
```

## Configuration

The tool uses a configuration system that stores settings in JSON format. The `character.json` sample file shows the expected structure for picker configurations.

## Logging

All tool activities are logged to:
`%APPDATA%/CharacterPicker/logs/character_picker.log`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.
