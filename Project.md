# CharacterPicker - Project Notes (AI Reference)

## Purpose
- Guidance for AI-assisted changes (UI tweaks, picker behavior, bug fixes) without breaking existing workflows in Maya.

## Tech Stack
- Autodesk Maya (PySide2/Qt, shiboken2, maya.OpenMayaUI/mel/cmds).
- Python (Maya-bundled version; tested with PySide2 APIs and importlib.reload usage).
- Icons resolved via env var `RIGGING_TOOL_ROOT` pointing to repo root (`.../CharacterPicker`).

## Key Areas
- Entry point: `main.py` (`show_character_picker` builds the UI) -> `Gui/main_window.py:CharacterPicker`.
- GUI composition: `Gui/tab_manager.py` (tabs/pages), `Gui/edit_box.py` (toolbox controls), `Gui/context_menu.py`, `Gui/custom_widgets.py` (collapsible/tool widgets), `Gui/menubar.py`.
- Picker logic: `Logic/grid_widget.py` (canvas, events, zoom/frame), `Logic/picker.py` (button creation/commands/shapes), `Logic/data_handler.py` (save/load JSON contracts).
- Utilities/assets: `Utility/logging_setup.py`, `Utility/utils.py`, `Icons/` (backgrounds, tab icons), sample config `character.json`, logs in `%APPDATA%/CharacterPicker/logs/character_picker.log`.

## Coding Expectations
- Favor small, targeted diffs; preserve existing behavior and UI signal wiring.
- Keep modules reload-friendly (importlib.reload patterns already used); avoid renaming files/classes/functions unless necessary.
- Maintain command modes (Python/MEL/Select) and JSON schema used by `data_handler.py`/`tab_manager.py`; do not change button data keys lightly.
- Respect Maya environment assumptions: run inside Maya UI thread, keep `RIGGING_TOOL_ROOT` usage for assets, and avoid blocking the event loop.
- Follow current naming/style patterns and directory structure when adding modules or icons.

## Constraints & Risks
- High impact areas: grid/picker interaction (`Logic/grid_widget.py`, `Logic/picker.py`) and tab/page lifecycle (`Gui/tab_manager.py`, `Gui/main_window.py`). Changes can break selection, zoom, or edit/animate mode.
- Saving/loading must stay backward compatible with existing picker JSON; avoid schema changes without migration.
- Maya context required; avoid code paths that assume standalone execution or that rename the MEL-visible window/object names.
- Minimal refactors; prioritize behavior-preserving fixes over rewrites.

## Backlog/Focus Areas
- UI quality-of-life: toolbox usability, context menu polish, page/tab ergonomics.
- Picker reliability: selection toggling, zoom/frame behavior, edit vs animate mode clarity.
- Data handling: robust save/load dialogs, validation of `character.json`-style configs.
- New picker features or commands added incrementally while keeping existing tab/page flow intact.
