import os
import sys
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import CharacterPicker.tabs as tabs
import CharacterPicker.picker_v_01 as picker
import CharacterPicker.data_handler as data
import importlib
importlib.reload(picker)
importlib.reload(tabs)

ICON_DIR = os.path.join(os.environ["RIGGING_TOOL_ROOT"], "CharacterPicker", "Icons")


def maya_main_window():
    """Return Maya's main window widget."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class CharacterPicker(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CharacterPicker, self).__init__(parent or maya_main_window())
        self.setWindowTitle("Character Picker")
        self.resize(600, 1200)
        self.setMinimumSize(400, 800)  # Set a minimum size to avoid UI breaking

        # Add the menu bar
        self.create_menu_bar()

        # Add a central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Outer layout
        outer_layout = QtWidgets.QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabBar(tabs.FixedSizeTabBar())
        outer_layout.addWidget(self.tab_widget)

        # Add a default character tab and the "Add Character Tab"
        self.add_character_tab("Character 1")  # Add the first character tab
        self.add_character_tab()  # Add the "Add Character Tab"

        # Create the editBox layout at the bottom
        self.editBox = QtWidgets.QGroupBox("Edit Settings")
        outer_layout.addWidget(self.editBox)

        editBox_layout = QtWidgets.QVBoxLayout(self.editBox)

        # Form layout for rows, columns, and cell size
        form_layout = QtWidgets.QFormLayout()
        editBox_layout.addLayout(form_layout)

        # Rows SpinBox
        self.rows_spin = QtWidgets.QSpinBox()
        self.rows_spin.setMinimum(1)
        self.rows_spin.setValue(20)  # Default
        form_layout.addRow("Rows:", self.rows_spin)

        # Columns SpinBox
        self.cols_spin = QtWidgets.QSpinBox()
        self.cols_spin.setMinimum(1)
        self.cols_spin.setValue(10)  # Default
        form_layout.addRow("Columns:", self.cols_spin)

        # Cell Size SpinBox
        self.cell_size_spin = QtWidgets.QSpinBox()
        self.cell_size_spin.setMinimum(10)
        self.cell_size_spin.setMaximum(200)
        self.cell_size_spin.setValue(40)  # Default cell size
        form_layout.addRow("Cell Size:", self.cell_size_spin)

        # Buttons layout for adding/removing characters
        button_layout = QtWidgets.QHBoxLayout()
        editBox_layout.addLayout(button_layout)

        self.add_character_button = QtWidgets.QPushButton("Add New Character")
        self.add_character_button.clicked.connect(self.add_new_character_button_clicked)
        button_layout.addWidget(self.add_character_button)

        self.remove_character_button = QtWidgets.QPushButton("Remove Current Character")
        self.remove_character_button.clicked.connect(self.close_current_tab)
        button_layout.addWidget(self.remove_character_button)

        # Connect signals for spin boxes if you'd like to react to changes
        # For instance, whenever rows/cols/cell_size is changed, you could update the current page.
        # self.rows_spin.valueChanged.connect(self.update_current_page_grid)
        # self.cols_spin.valueChanged.connect(self.update_current_page_grid)
        # self.cell_size_spin.valueChanged.connect(self.update_current_page_grid)

    def add_new_character_button_clicked(self):
        self.add_character_tab(f"Character {self.tab_widget.count()}")

    def create_menu_bar(self):
        """Add a menu bar with options."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New Character", self.new_character)
        file_menu.addAction("Save Character...", self.save_character)
        file_menu.addAction("Load Character...", lambda:self.load_character())
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Add Page", self.add_page_to_current)
        edit_menu.addAction("Add Button", self.add_button_to_current)
        edit_menu.addSeparator()
        edit_menu.addAction("Close Current Tab", self.close_current_tab)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self.show_about_dialog)

    def new_character(self):
        QtWidgets.QMessageBox.information(self, "New Character", "Create a new character.")

    def save_character(self):
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            QtWidgets.QMessageBox.warning(self, "Warning", "No character tab selected.")
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Character", "character.json", "JSON Files (*.json)"
        )
        if not file_path:
            return

        character_name = self.tab_widget.tabText(self.tab_widget.currentIndex())
        pages = {page_name:page for page_name, page in getattr(current_tab, "page_buttons", {}).items()}
        data.save_character_data(file_path, character_name, pages)
        QtWidgets.QMessageBox.information(self, "Save Complete", "Character saved successfully!")

    def load_character(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Character", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            character_data = data.load_character_data(file_path)
            self.add_character_from_data(character_data)
            QtWidgets.QMessageBox.information(self, "Load Complete", "Character loaded successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load character: {e}")

    def close_current_tab(self):
        """Close the currently selected character tab."""
        current_index = self.tab_widget.currentIndex()
        # Silently skip removing the "Add Character Tab"
        if current_index == self.tab_widget.count() - 1:
            return
        if current_index != -1:
            self.tab_widget.removeTab(current_index)
            # Select the tab to the left, if available
            new_index = max(0, current_index - 1)
            self.tab_widget.setCurrentIndex(new_index)

    def add_page_to_current(self):
        """Add a new page to the current character tab."""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid tab selected.")
            return

        page_name, ok = QtWidgets.QInputDialog.getText(self, "New Page", "Enter page name:")
        if ok and page_name.strip():
            stacked_widget = current_tab.stacked_widget
            new_page = picker.PickerPage()
            stacked_widget.addWidget(new_page)

            page_button = QtWidgets.QPushButton(page_name)
            page_button.clicked.connect(
                lambda checked=False, page=new_page:(
                    stacked_widget.setCurrentWidget(page), self.update_page_button_styles()
                )
            )

            current_tab.page_buttons[page_button] = new_page
            current_tab.layout().itemAt(0).layout().addWidget(page_button)
            stacked_widget.setCurrentWidget(new_page)
            self.update_page_button_styles()

    def add_button_to_current(self):
        """Add a button to the current page."""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid tab selected.")
            return

        current_page = current_tab.stacked_widget.currentWidget()
        if isinstance(current_page, picker.PickerPage):
            current_page.create_button(QtCore.QPoint(0, 0))  # Default position
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Current page is not a valid PickerPage.")

    def show_about_dialog(self):
        QtWidgets.QMessageBox.about(self, "About", "Character Picker Tool\nVersion 1.0\nCreated for Maya Animators.")

    def add_character_tab(self, character_name=None):
        if character_name is None:  # Add the "Add Character Tab"
            add_tab_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(add_tab_widget)
            label = QtWidgets.QLabel("To begin, add a character")
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label)

            icon_path = os.path.join(ICON_DIR, "plus.svg")
            icon = QtGui.QIcon(icon_path)
            self.tab_widget.setIconSize(QtCore.QSize(50, 50))
            self.tab_widget.addTab(add_tab_widget, icon, "NEW")
            self.tab_widget.tabBar().tabBarClicked.connect(self.on_tab_bar_clicked)
        else:
            character_tab = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(character_tab)

            page_buttons_layout = QtWidgets.QHBoxLayout()
            layout.addLayout(page_buttons_layout)

            stacked_widget = QtWidgets.QStackedWidget()
            layout.addWidget(stacked_widget)

            main_page = picker.PickerPage(rows=20, cols=10)
            stacked_widget.addWidget(main_page)

            main_button = QtWidgets.QPushButton("Main")
            main_button.clicked.connect(lambda:stacked_widget.setCurrentWidget(main_page))
            page_buttons_layout.addWidget(main_button)

            character_tab.stacked_widget = stacked_widget
            character_tab.page_buttons = {main_button:main_page}

            random_icon_path = tabs.get_random_icon(ICON_DIR)
            tab_icon = QtGui.QIcon(random_icon_path)
            self.tab_widget.insertTab(self.tab_widget.count() - 1, character_tab, tab_icon, character_name)
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 2)
            self.update_page_button_styles()

    def on_tab_bar_clicked(self, index):
        if index == self.tab_widget.count() - 1:
            self.add_character_tab(f"Character {self.tab_widget.count()}")

    def update_page_button_styles(self):
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            return
        stacked_widget = current_tab.stacked_widget
        current_page = stacked_widget.currentWidget()

        for button, page in current_tab.page_buttons.items():
            if page == current_page:
                button.setStyleSheet("""
                    QPushButton {
                        border: 2px solid #f9aa26;
                        background-color: #373737;
                        color: #FFFFFF;
                        font-size: 16px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #373737;
                        color: #FFFFFF;
                    }
                    QPushButton:pressed {
                        background-color: #2d2d2d;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #2d2d2d;
                        background-color: #373737;
                        color: #A6A6A6;
                        font-size: 16px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        border: 2px solid #f9aa26;
                        color: #FFFFFF;
                    }
                    QPushButton:pressed {
                        background-color: #2d2d2d;
                    }
                """)


def show_character_picker():
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, CharacterPicker):
            widget.close()

    picker_window = CharacterPicker()
    picker_window.setWindowFlags(QtCore.Qt.Window)
    picker_window.show()


if __name__ == "__main__":
    show_character_picker()
