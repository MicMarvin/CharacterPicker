# menubar.py
from PySide2 import QtWidgets, QtCore


class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window  # Explicit reference

        # Define actions as instance variables for easy connection in MainWindow
        self.add_character_action = None
        self.save_character_action = None
        self.save_as_action = None
        self.load_character_action = None
        self.rename_character_action = None
        self.current_mode_action = None
        self.add_page_action = None
        self.add_button_action = None
        self.delete_button_action = None
        self.remove_page_action = None
        self.rename_page_action = None
        self.close_tab_action = None
        self.frame_action = None
        self.zoom_in_action = None
        self.zoom_out_action = None
        self.zoom_reset_action = None
        self.toolbox_visibility_action = None

        # Create menus
        self.create_menus()

    def create_menus(self):
        # File menu
        file_menu = self.addMenu("File")
        self.add_character_action = QtWidgets.QAction("New...", file_menu)
        file_menu.addAction(self.add_character_action)

        self.load_character_action = QtWidgets.QAction("Open...", file_menu)
        file_menu.addAction(self.load_character_action)

        file_menu.addSeparator()

        self.save_character_action = QtWidgets.QAction("Save", file_menu)
        file_menu.addAction(self.save_character_action)

        self.save_as_action = QtWidgets.QAction("Save As...", file_menu)
        file_menu.addAction(self.save_as_action)

        file_menu.addSeparator()

        self.rename_character_action = QtWidgets.QAction("Rename Tab", file_menu)
        file_menu.addAction(self.rename_character_action)

        self.close_tab_action = QtWidgets.QAction("Close Tab", file_menu)
        file_menu.addAction(self.close_tab_action)

        file_menu.addSeparator()

        exit_action = QtWidgets.QAction("Exit Picker", file_menu)
        file_menu.addAction(exit_action)
        exit_action.triggered.connect(self.main_window.close)

        self.load_character_action.setEnabled(False)

        # Edit menu
        edit_menu = self.addMenu("Edit")

        self.add_page_action = QtWidgets.QAction("Add Page", edit_menu)
        edit_menu.addAction(self.add_page_action)

        self.rename_page_action = QtWidgets.QAction("Rename Page", edit_menu)
        edit_menu.addAction(self.rename_page_action)

        self.remove_page_action = QtWidgets.QAction("Delete Page", edit_menu)
        edit_menu.addAction(self.remove_page_action)

        edit_menu.addSeparator()
        self.add_button_action = QtWidgets.QAction("Add Button", edit_menu)
        edit_menu.addAction(self.add_button_action)

        self.delete_button_action = QtWidgets.QAction("Delete Button", edit_menu)
        edit_menu.addAction(self.delete_button_action)

        edit_menu.addSeparator()

        self.current_mode_action = QtWidgets.QAction("Switch to Animate Mode", edit_menu)
        edit_menu.addAction(self.current_mode_action)

        # View menu
        view_menu = self.addMenu("View")

        self.frame_action = QtWidgets.QAction("Frame Selected/All", view_menu)
        view_menu.addAction(self.frame_action)

        self.zoom_in_action = QtWidgets.QAction("Zoom In", view_menu)
        view_menu.addAction(self.zoom_in_action)

        self.zoom_out_action = QtWidgets.QAction("Zoom Out", view_menu)
        view_menu.addAction(self.zoom_out_action)

        self.zoom_reset_action = QtWidgets.QAction("Reset Zoom", view_menu)
        view_menu.addAction(self.zoom_reset_action)

        view_menu.addSeparator()

        self.toolbox_visibility_action = QtWidgets.QAction("ToolBox", view_menu)
        self.toolbox_visibility_action.setCheckable(True)
        view_menu.addAction(self.toolbox_visibility_action)

        # Help menu
        help_menu = self.addMenu("Help")
        about_action = QtWidgets.QAction("About", help_menu)
        help_menu.addAction(about_action)
        about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        QtWidgets.QMessageBox.information(self, "About", "Character Picker Tool\nVersion 1.0")

