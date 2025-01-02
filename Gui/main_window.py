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
        super().__init__(parent)
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

        self._edit_mode = True  # Start in Edit Mode

        # Initialize Edit Box
        self.edit_box = edit.EditBox(self.icon_dir, parent=self, tab_manager=self.tab_manager)
        self.edit_box.setVisible(self._edit_mode)
        outer_layout.addWidget(self.edit_box)
        self.menu_bar.toolbox_visibility_action.setChecked(self._edit_mode)

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

        # Manually force the UI to reflect the tab and page default name
        current_index = self.tab_manager.currentIndex()
        self.on_tab_changed(current_index)

    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value):
        if self._edit_mode == value:
            return
        self._edit_mode = value
        self.update_mode_state()

    def toggle_edit_mode(self):
        """Toggle Edit Mode."""
        self.edit_mode = not self.edit_mode

    def update_mode_state(self):
        """Update UI components based on the current mode."""
        # Update menu bar action text
        self.update_mode_text()

        # Show/Hide the EditBox
        self.edit_box.setVisible(self._edit_mode)

        # Safely update menu actions
        actions = [
            ("add_page_action", self.menu_bar.add_page_action),
            ("add_button_action", self.menu_bar.add_button_action),
            ("remove_page_action", self.menu_bar.remove_page_action),
            ("rename_page_action", self.menu_bar.rename_page_action),
            ("delete_button_action", self.menu_bar.delete_button_action),
        ]

        for action_name, action in actions:
            if action:
                try:
                    action.setEnabled(self._edit_mode)
                except RuntimeError as e:
                    print(f"Error updating {action_name}: {e}")
            else:
                print(f"Action {action_name} is already deleted or does not exist.")

        # # Trigger grid updates
        # for tab_widget in self.tab_manager.children():
        #     if isinstance(tab_widget, QtWidgets.QWidget) and hasattr(tab_widget, "stacked_widget"):
        #         for page in tab_widget.stacked_widget.children():
        #             if isinstance(page, grid.GridWidget):
        #                 page.update()

    def update_mode_text(self):
        """Update the text of the current_mode_action based on the mode."""
        if not self.menu_bar or not self.menu_bar.current_mode_action:
            print("Warning: MenuBar or current_mode_action is None.")
            return

        try:
            if self.edit_mode:
                self.menu_bar.current_mode_action.setText("Switch to Animate")
            else:
                self.menu_bar.current_mode_action.setText("Switch to Edit Mode")
        except RuntimeError as e:
            print(f"Error updating current_mode_action: {e}")

    def connect_signals(self):
        """Connect signals between components."""
        # Connect EditBox signals to appropriate methods
        self.edit_box.picker_added.connect(self.tab_manager.add_picker_button)
        self.edit_box.picker_updated.connect(self.update_picker_button)
        self.edit_box.add_button_signal.connect(self.tab_manager.add_button_to_current)

        self.edit_box.add_character_button.clicked.connect(self.handle_add_character)
        self.edit_box.save_character_button.clicked.connect(self.handle_save_character)
        self.edit_box.load_character_button.clicked.connect(self.handle_load_character)
        self.edit_box.remove_character_button.clicked.connect(self.remove_current_character)
        self.edit_box.add_page_button.clicked.connect(self.handle_add_page)
        self.edit_box.remove_page_button.clicked.connect(self.remove_current_page)

        # Connect Menubar signals to appropriate methods
        self.menu_bar.add_character_action.triggered.connect(self.handle_add_character)
        self.menu_bar.save_character_action.triggered.connect(self.handle_save_character)
        self.menu_bar.load_character_action.triggered.connect(self.handle_load_character)
        self.menu_bar.add_page_action.triggered.connect(self.handle_add_page)
        self.menu_bar.remove_page_action.triggered.connect(self.remove_current_page)
        self.menu_bar.add_button_action.triggered.connect(self.tab_manager.add_button_to_current)
        self.menu_bar.close_tab_action.triggered.connect(self.remove_current_character)
        self.menu_bar.current_mode_action.triggered.connect(self.toggle_edit_mode)
        self.menu_bar.toolbox_visibility_action.toggled.connect(self.toggle_toolbox_visibility)

        # Connect other signals
        self.tab_manager.currentChanged.connect(self.on_tab_changed) # Tab change
        self.tab_manager.currentPageChanged.connect(self.on_page_changed) # Page change

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
        """
        Handle adding a new page to the current tab.
        If no page_name is provided, prompt the user for one.
        """
        if not page_name:
            page_name, ok = QtWidgets.QInputDialog.getText(self, "Add Page", "Enter page name:")
            # 1) If the user canceled (ok == False), just exit—no alerts.
            if not ok:
                return
            # 2) If the user pressed OK but the name is empty/blank, show warning and exit.
            if not page_name.strip():
                QtWidgets.QMessageBox.warning(self, "Warning", "Page name cannot be empty.")
                return

        # If we get here, page_name is set, so proceed to add a page
        current_tab = self.tab_manager.currentWidget()
        if current_tab:
            self.tab_manager.add_page_to_current(page_name)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No current tab found.")

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
        """Handle removing the current page from the current tab's QStackedWidget
        and remove its navigation button."""
        # Get the current tab index
        current_index = self.tab_manager.currentIndex()
        # If it's the very last tab, likely the "NEW" tab — do nothing or show a warning
        if current_index == self.tab_manager.count() - 1:
            #QtWidgets.QMessageBox.warning(self, "Warning", "Cannot remove a page from the 'NEW' tab.")
            return

        # Get the actual current tab widget
        current_tab = self.tab_manager.currentWidget()
        if not current_tab or not hasattr(current_tab, 'stacked_widget'):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid character tab is selected.")
            return

        stacked_widget = current_tab.stacked_widget
        if stacked_widget.count() <= 1:
            # If there's only 1 page, decide if you want to allow removing it
            # or keep at least one page in the tab.
            #QtWidgets.QMessageBox.warning(self, "Warning", "Cannot remove the only page in this tab.")
            return

        # Find the current page in the stacked widget
        current_page = stacked_widget.currentWidget()
        if not current_page:
            QtWidgets.QMessageBox.information(self, "Info", "No current page to remove.")
            return

        # Find the corresponding button in page_buttons
        page_button = None
        for btn, page in current_tab.page_buttons.items():
            if page == current_page:
                page_button = btn
                break

        if not page_button:
            QtWidgets.QMessageBox.warning(self, "Warning", "Could not find a button for the current page.")
            return

        # Remove the button from the layout and the dictionary
        current_tab.page_button_layout.removeWidget(page_button)
        current_tab.page_buttons.pop(page_button, None)
        page_button.deleteLater()

        # Remove the page from the stacked widget
        stacked_widget.removeWidget(current_page)
        current_page.deleteLater()

        # Optionally, switch to the first page or the previous index
        if stacked_widget.count() > 0:
            stacked_widget.setCurrentIndex(0)  # or another logic to pick a new "current" page

        # Update the styles so the new current page button is highlighted
        self.tab_manager.update_page_button_styles()

        print("Current page removed successfully.")

    def toggle_toolbox_visibility(self, checked):
        """Show or hide the EditBox (ToolBox) based on the action's checked state."""
        self.edit_box.setVisible(checked)
        # Optional: Synchronize the state of edit mode with toolbox visibility
        self.edit_mode = checked

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
            self.edit_box.update_picker_button_fields(None)
        else:
            # Select: populate fields with button's data
            self.edit_box.update_picker_button_fields(btn)
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
        self.edit_box.update_picker_button_fields(None)

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
        """
        Handle tab change to update EditBox accordingly.
        Deselect the current picker button,
        then set the EditBox fields to match the new tab/page.
        """
        # 1) Deselect any picker button
        self.set_selected_picker_button(None)

        # 2) Pull the character name from the tab and show it in edit_box.character_name_input
        tab_name = self.tab_manager.tabText(index)  # e.g. "Character 1"
        self.edit_box.set_character_name_field(tab_name)

        # 3) Pull the current page name, if any
        current_tab = self.tab_manager.widget(index)
        if current_tab and hasattr(current_tab, "stacked_widget"):
            current_page = current_tab.stacked_widget.currentWidget()
            # If the page has a .page_name attribute
            page_name = getattr(current_page, "page_name", "")
            self.edit_box.set_page_name_field(page_name)

            # Update the character picture label
            pic_path = getattr(current_tab, "character_pic_path", None)
            if pic_path:
                self.edit_box.character_pic_filename.setText(os.path.basename(pic_path))
            else:
                self.edit_box.character_pic_filename.setText("None")

            # **Enable or disable the "Set Character Picture" button**
            if current_tab != self.tab_manager.widget(self.tab_manager.count() - 1):
                self.edit_box.character_pic_button.setEnabled(True)
            else:
                self.edit_box.character_pic_button.setEnabled(False)
        else:
            # No valid page => clear the field
            self.edit_box.set_page_name_field("")
            self.edit_box.character_pic_filename.setText("None")
            self.edit_box.character_pic_button.setEnabled(False)

    def on_page_changed(self, index):
        """
        Called whenever the current QStackedWidget in TabManager changes pages.
        Pull the new page's name into EditBox.page_name_input.
        """
        current_tab = self.tab_manager.currentWidget()
        if not current_tab or not hasattr(current_tab, 'stacked_widget'):
            self.edit_box.set_page_name_field("")
            return

        current_page = current_tab.stacked_widget.widget(index)
        if hasattr(current_page, "page_name"):
            self.edit_box.set_page_name_field(current_page.page_name)
        else:
            self.edit_box.set_page_name_field("")

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


