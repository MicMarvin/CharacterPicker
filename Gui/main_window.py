# main_window.py
from PySide2 import QtCore, QtWidgets, QtGui
import CharacterPicker.Gui.menubar as menubar
import CharacterPicker.Gui.edit_box as edit
import CharacterPicker.Gui.tab_manager as tab
import CharacterPicker.Gui.context_menu as context
import CharacterPicker.Logic.grid_widget as grid
import os
import importlib

importlib.reload(menubar)
importlib.reload(edit)
importlib.reload(tab)
importlib.reload(context)
importlib.reload(grid)

class CharacterPicker(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CharacterPicker, self).__init__(parent)
        self.setWindowTitle("Character Picker")
        self.resize(659, 1210)
        self.setMinimumSize(400, 800)  # Set a minimum size to avoid UI breaking

        try:
            self.icon_dir = os.path.join(os.environ["RIGGING_TOOL_ROOT"], "CharacterPicker", "Icons")
            if not os.path.exists(self.icon_dir):
                raise FileNotFoundError(f"Icons directory not found: {self.icon_dir}")
        except Exception as e:
            print(f"Error setting up icons: {e}")

        # Initialize menu bar
        self.menu_bar = menubar.MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Initialize central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Outer layout
        outer_layout = QtWidgets.QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(10, 0, 10, 10)
        outer_layout.setSpacing(10)

        # Initialize Tab Manager
        self.tab_manager = tab.TabManager(self.icon_dir, self)
        outer_layout.addWidget(self.tab_manager)

        # Initialize Edit Box
        self.edit_box = edit.EditBox(self.icon_dir, self)
        outer_layout.addWidget(self.edit_box)

        # Initialize Context Menu
        self.context_menu = context.ContextMenu(self)

        # Connect signals
        self.connect_signals()

        # Initialize selected button
        self.selected_picker_button = None

        # Create a default 1x1 button using the unified create_picker_button
        current_tab = self.tab_manager.currentWidget()
        if hasattr(current_tab, "stacked_widget"):
            main_page = current_tab.stacked_widget.widget(0)
            if isinstance(main_page, grid.GridWidget):
                # Optionally, you can add a default button here if needed
                self.set_selected_picker_button(None)  # Ensure no button is selected initially

    def connect_signals(self):
        """Connect signals between components."""
        # Connect EditBox signals to appropriate methods
        self.edit_box.picker_added.connect(self.tab_manager.add_picker_button)
        self.edit_box.picker_updated.connect(self.update_picker_button)
        self.edit_box.add_button_signal.connect(self.tab_manager.add_button_to_current)

        self.edit_box.add_character_button.clicked.connect(self.handle_add_character)
        self.edit_box.remove_character_button.clicked.connect(self.remove_current_character)
        self.edit_box.add_page_button.clicked.connect(self.handle_add_page)
        self.edit_box.remove_page_button.clicked.connect(self.remove_current_page)
        self.edit_box.mode_toggle_btn.clicked.connect(self.toggle_edit_mode)

        # Connect Menubar signals to appropriate methods
        self.menu_bar.add_character_action.triggered.connect(self.handle_add_character)
        self.menu_bar.save_character_action.triggered.connect(self.handle_save_character)
        self.menu_bar.load_character_action.triggered.connect(self.handle_load_character)
        self.menu_bar.add_page_action.triggered.connect(self.handle_add_page)
        self.menu_bar.remove_page_action.triggered.connect(self.remove_current_page)
        self.menu_bar.add_button_action.triggered.connect(self.tab_manager.add_button_to_current)
        self.menu_bar.close_tab_action.triggered.connect(self.remove_current_character)

        # Connect other signals
        self.tab_manager.currentChanged.connect(self.on_tab_changed)

    def handle_add_character(self):
        """Handle adding a new character tab."""
        self.tab_manager.add_character_tab(f"Character {self.tab_manager.count()}")

    def handle_save_character(self):
        """Handle the 'Save Character' action from the menu."""
        self.save_character()

    def handle_load_character(self):
        """Handle the 'Load Character' action from the menu."""
        self.load_character()

    def handle_add_page(self, page_name=None):
        """Handle adding a new page."""
        if not page_name:  # If no page name is provided, prompt the user
            page_name, ok = QtWidgets.QInputDialog.getText(self, "Add Page", "Enter page name:")
            if not ok or not page_name.strip():
                QtWidgets.QMessageBox.warning(self, "Warning", "Page name cannot be empty.")
                return

        current_tab = self.tab_manager.currentWidget()
        if current_tab:
            self.tab_manager.add_page_to_current(page_name)

    def remove_current_character(self):
        """Handle removing the current character."""
        current_index = self.tab_manager.currentIndex()
        if current_index == self.tab_manager.count() - 1:
            return

        # Remove the current tab
        self.tab_manager.removeTab(current_index)

        # Select the tab to the left (if it exists)
        if current_index > 0:
            self.tab_manager.setCurrentIndex(current_index - 1)
        else:
            self.tab_manager.setCurrentIndex(0)

    def remove_current_page(self):
        """Handle removing the current page."""
        print(f"Removing Page")

    def toggle_edit_mode(self, checked):
        """Toggle between Edit Mode and Animate Mode."""
        edit_mode = self.edit_box.mode_toggle_btn.isChecked()
        current_tab = self.tab_manager.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            return

        current_page = current_tab.stacked_widget.currentWidget()
        if hasattr(current_page, "grid_widget"):
            current_page.grid_widget.edit_mode = edit_mode

        if edit_mode:
            self.edit_box.mode_toggle_btn.setText("Switch to Animate Mode")
            self.edit_box.setVisible(True)
        else:
            self.edit_box.mode_toggle_btn.setText("Switch to Edit Mode")
            self.edit_box.setVisible(False)

    def set_selected_picker_button(self, btn):
        """
        Select or deselect a picker button.
        """
        # Deselect previously selected button
        if self.selected_picker_button and self.selected_picker_button != btn:
            self.selected_picker_button.set_default_style()

        self.selected_picker_button = btn

        if btn is None:
            # Deselect: clear fields and reset UI
            self.edit_box.set_selected_picker_button(None)
        else:
            # Select: populate fields with button's data
            self.edit_box.set_selected_picker_button(btn)
            btn.set_selected_style()

    def update_picker_button(self, picker_data):
        """Handle updating the selected picker button based on data from EditBox."""
        if not self.selected_picker_button:
            QtWidgets.QMessageBox.warning(self, "Warning", "No picker button selected to update.")
            return

        label = picker_data.get("label", self.selected_picker_button.text())
        grid_pos = picker_data.get("grid_pos", (self.selected_picker_button.grid_x, self.selected_picker_button.grid_y))
        size_in_cells = picker_data.get("size_in_cells", (
            self.selected_picker_button.width_in_cells, self.selected_picker_button.height_in_cells))

        # Update picker button attributes
        self.selected_picker_button.setText(label)
        self.selected_picker_button.grid_x, self.selected_picker_button.grid_y = grid_pos
        self.selected_picker_button.width_in_cells, self.selected_picker_button.height_in_cells = size_in_cells
        self.selected_picker_button.setFixedSize(self.selected_picker_button.width_in_cells * 40,
                                                 self.selected_picker_button.height_in_cells * 40)  # Adjust cell size as needed

        # Update grid placement
        current_tab = self.tab_manager.currentWidget()
        if current_tab and hasattr(current_tab, "stacked_widget"):
            current_page = current_tab.stacked_widget.currentWidget()
            if isinstance(current_page, grid.GridWidget):
                current_page.add_picker_button(self.selected_picker_button)  # Re-add to grid to update position

    def delete_selected_picker_button(self):
        """Handle deletion of the selected picker button."""
        if not self.selected_picker_button:
            QtWidgets.QMessageBox.warning(self, "Warning", "No picker button selected to delete.")
            return

        # Remove from the grid
        self.selected_picker_button.setParent(None)
        self.selected_picker_button.deleteLater()
        self.selected_picker_button = None

        # Update EditBox UI
        self.edit_box.set_selected_picker_button(None)

    def on_picker_event(self, event_type, picker_button):
        """Handle picker button events from GridWidget."""
        if event_type == "selected":
            self.set_selected_picker_button(picker_button)
        elif event_type == "moved":
            # Handle moved event if needed
            pass
        elif event_type == "deselect":
            self.set_selected_picker_button(None)

    def on_tab_changed(self, index):
        """Handle tab change to update EditBox accordingly."""
        self.set_selected_picker_button(None)

    def show_about_dialog(self):
        """Show the About dialog."""
        QtWidgets.QMessageBox.information(self, "About", "Character Picker Tool\nVersion 1.0")

    def save_character(self):
        """Placeholder method for saving a character."""
        # Implement saving logic here
        QtWidgets.QMessageBox.information(self, "Save Character", "Character saved successfully.")

    def load_character(self):
        """Placeholder method for loading a character."""
        # Implement loading logic here
        QtWidgets.QMessageBox.information(self, "Load Character", "Character loaded successfully.")
