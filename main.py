# main.py
from PySide2 import QtCore, QtWidgets, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

import CharacterPicker.Gui.main_window as main

import importlib
importlib.reload(main)


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
        picker_window.setWindowFlags(QtCore.Qt.Window)
        picker_window.show()
        print("Character Picker launched successfully.")
    except Exception as e:
        print(f"Failed to launch Character Picker: {e}")


if __name__ == "__main__":
    show_character_picker()
