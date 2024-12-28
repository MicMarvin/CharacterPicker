# menubar.py
from PySide2 import QtWidgets, QtCore
import os


class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent=None):
        super(MenuBar, self).__init__(parent)

        # Define actions as instance variables for easy connection in MainWindow
        self.add_character_action = None
        self.save_character_action = None
        self.load_character_action = None
        self.add_page_action = None
        self.add_button_action = None
        self.remove_page_action = None
        self.close_tab_action = None

        # Create menus
        self.create_menus()

    def create_menus(self):
        # File menu
        file_menu = self.addMenu("File")
        self.add_character_action = file_menu.addAction("New Character")
        self.save_character_action = file_menu.addAction("Save Character...")
        self.load_character_action = file_menu.addAction("Load Character...")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit menu
        edit_menu = self.addMenu("Edit")
        self.add_page_action = edit_menu.addAction("Add Page")
        self.add_button_action = edit_menu.addAction("Add Button")
        edit_menu.addSeparator()
        self.remove_page_action = edit_menu.addAction("Remove Page")
        self.close_tab_action = edit_menu.addAction("Close Character")

        # Help menu
        help_menu = self.addMenu("Help")
        help_menu.addAction("About", self.show_about_dialog)

    def show_about_dialog(self):
        QtWidgets.QMessageBox.information(self, "About", "Character Picker Tool\nVersion 1.0")
