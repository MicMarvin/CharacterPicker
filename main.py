# main.py
import logging
from PySide2 import QtCore, QtWidgets, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

import CharacterPicker.Utility.logging_setup as logging_setup
import CharacterPicker.Gui.main_window as main

import importlib
importlib.reload(main)

logger = logging.getLogger(__name__)

def maya_main_window():
    """Return Maya's main window widget (in Maya)."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def show_character_picker():
    """Show or re-show the CharacterPicker in Maya."""
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, main.CharacterPicker):
            widget.close()

    try:
        picker_window = main.CharacterPicker(parent=maya_main_window())
        picker_window.setObjectName("CharacterPickerWindow")  # Ensure unique name for MEL compatibility
        picker_window.setWindowFlags(QtCore.Qt.Window)
        picker_window.show()

        # Store picker window reference globally for MEL/Python commands
        import sys
        sys.modules['character_picker_main_window'] = picker_window

    except Exception as e:
        logger.error(f"Failed to launch Character Picker: {e}")
        

if __name__ == "__main__":
    show_character_picker()
