# main_window.py
from PySide2 import QtCore, QtWidgets, QtGui
import CharacterPicker.Gui.menubar as menubar
import CharacterPicker.Gui.edit_box as edit
import CharacterPicker.Gui.tab_manager as tab
import CharacterPicker.Gui.context_menu as context
import CharacterPicker.Gui.custom_widgets as custom
import CharacterPicker.Logic.grid_widget as grid
import CharacterPicker.Logic.picker as picker
import os
import importlib

importlib.reload(menubar)
importlib.reload(edit)
importlib.reload(tab)
importlib.reload(context)
importlib.reload(grid)
importlib.reload(custom)
importlib.reload(picker)

class CharacterPicker(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Character Picker")
        self.resize(659, 1210)
        self.setMinimumSize(400, 800)  # Set a minimum size to avoid UI breaking

        # tracks which GridWidget we’re currently connected to
        self._connected_grid = None

        try:
            self.icon_dir = os.path.join(os.environ["RIGGING_TOOL_ROOT"], "CharacterPicker", "Icons")
            if not os.path.exists(self.icon_dir):
                raise FileNotFoundError(f"Icons directory not found: {self.icon_dir}")
        except Exception as e:
            print(f"Error setting up icons: {e}")

        # Initialize ContextMenu
        self.context_menu = context.ContextMenu(self)

        # Initialize menu bar
        self.menu_bar = menubar.MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Initialize Tab Manager
        self.tab_manager = tab.TabManager(self.icon_dir, character_picker=self, context_menu=self.context_menu)

        # Initialize central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Outer layout
        outer_layout = QtWidgets.QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(10, 0, 10, 10)
        outer_layout.setSpacing(10)
        outer_layout.addWidget(self.tab_manager)

        # Initialize Edit Box (content for the ToolBox)
        self.edit_box = edit.EditBox(self.icon_dir, main_window=self, tab_manager=self.tab_manager, context_menu=self.context_menu)

        # Initialize ToolBox
        self.tool_box_collapsible = custom.CollapsibleBox("ToolBox", use_custom_icons=True)
        self.tool_box_collapsible.setObjectName("ToolBox")
        self.tool_box_collapsible.setStyleSheet("""
            #ToolBox > QFrame {
                border: 1px solid #2d2d2d;  /* Black border */
                background-color: #373737; /* Grey background */
            }
        """)

        outer_layout.addWidget(self.tool_box_collapsible)

        # Add Edit Box content to the ToolBox
        tool_box_content_layout = QtWidgets.QVBoxLayout()
        tool_box_content_layout.addWidget(self.edit_box)
        self.tool_box_collapsible.setContentLayout(tool_box_content_layout)

        # Ensure '_edit_mode' is defined
        self._edit_mode = False

        # Now call the property to set the final desired state
        self.edit_mode = True

        # Initialize selected button
        self.selected_picker_button = None

        # Manually force the UI to reflect the tab and page default name
        current_index = self.tab_manager.currentIndex()
        self.on_tab_changed(current_index)

        # Connect signals
        self.connect_signals()

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
        """Called by 'Switch to Edit/Animate Mode' action."""
        self.edit_mode = not self._edit_mode  # <-- use the property

    def toggle_tool_box(self, open: bool):
        """Called by 'View -> ToolBox' menu action."""
        self.edit_mode = open  # <-- use the property

    def on_toolbox_toggled(self, is_open: bool):
        """Called when user clicks the arrow on CollapsibleBox."""
        if self._edit_mode != is_open:
            self.edit_mode = is_open  # <-- use the property

    def update_mode_state(self):
        """Update UI components based on the current mode."""
        # Step 1) Physically open/close the ToolBox
        if self.tool_box_collapsible.is_open != self._edit_mode:
            self.tool_box_collapsible.toggle_button.setChecked(self._edit_mode)
            self.tool_box_collapsible.on_toggle()

        # Step 2) Update the toolbox_visibility_action
        toolbox_visibility_action = self.menu_bar.toolbox_visibility_action
        if toolbox_visibility_action:
            toolbox_visibility_action.setChecked(self._edit_mode)

        # Step 3) The "Switch to Animate/Edit Mode" text
        text = "Switch to Animate Mode" if self._edit_mode else "Switch to Edit Mode"

        # Menubar current_mode_action
        if self.menu_bar.current_mode_action:
            self.menu_bar.current_mode_action.setText(text)

        # ContextMenu current_mode_action
        if self.context_menu and self.context_menu.current_mode_action:
            self.context_menu.current_mode_action.setText(text)

        # Step 4) Enable or disable context menu actions
        for action in [
            self.context_menu.add_button_action,
            self.context_menu.delete_button_action,
            self.context_menu.add_page_action,
            self.context_menu.remove_page_action
        ]:
            if action:
                action.setEnabled(self._edit_mode)

        # Step 5) Enable/disable relevant menu actions
        for action_name, action in [
            ("add_page_action", self.menu_bar.add_page_action),
            ("add_button_action", self.menu_bar.add_button_action),
            ("remove_page_action", self.menu_bar.remove_page_action),
            ("rename_page_action", self.menu_bar.rename_page_action),
            ("delete_button_action", self.menu_bar.delete_button_action),
        ]:
            if action:
                action.setEnabled(self._edit_mode)
            else:
                print(f"Action {action_name} does not exist.")

    def connect_signals(self):
        """Connect signals between components."""
        current_grid = self.tab_manager.get_current_grid_widget()
        if current_grid:
            current_grid.picker_event.connect(self.on_picker_button_event)
            self._connected_grid = current_grid

        # Connect EditBox signals to appropriate methods
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
        self.menu_bar.rename_character_action.triggered.connect(self.rename_current_character)
        self.menu_bar.add_page_action.triggered.connect(self.handle_add_page)
        self.menu_bar.rename_page_action.triggered.connect(self.rename_current_page)
        self.menu_bar.remove_page_action.triggered.connect(self.remove_current_page)
        self.menu_bar.add_button_action.triggered.connect(self.handle_menu_add_button)
        self.menu_bar.delete_button_action.triggered.connect(self.delete_selected_picker_button)
        self.menu_bar.close_tab_action.triggered.connect(self.remove_current_character)
        self.menu_bar.current_mode_action.triggered.connect(self.toggle_edit_mode)
        self.menu_bar.toolbox_visibility_action.toggled.connect(self.toggle_tool_box)

        # Connect ContextMenu actions to appropriate methods
        self.context_menu.change_background_action.triggered.connect(self.tab_manager.set_current_page_background)
        self.context_menu.change_picture_action.triggered.connect(self.edit_box.set_character_pic)
        self.context_menu.add_button_action.triggered.connect(self.handle_menu_add_button)
        self.context_menu.delete_button_action.triggered.connect(self.handle_context_delete_button)
        self.context_menu.add_tab_action.triggered.connect(self.handle_add_character)
        self.context_menu.rename_tab_action.triggered.connect(self.rename_current_character)
        self.context_menu.close_tab_action.triggered.connect(self.remove_current_character)
        self.context_menu.add_page_action.triggered.connect(self.handle_add_page)
        self.context_menu.rename_page_action.triggered.connect(self.rename_current_page)
        self.context_menu.remove_page_action.triggered.connect(self.remove_current_page)
        self.context_menu.current_mode_action.triggered.connect(self.toggle_edit_mode)

        # Connect other signals
        self.tab_manager.currentChanged.connect(self.on_tab_changed) # Tab change
        self.tab_manager.currentPageChanged.connect(self.on_page_changed) # Page change
        # Connect the toggle signal for resizing
        self.tool_box_collapsible.toggled.connect(self.resize_for_toolbox)
        self.tool_box_collapsible.toggled.connect(self.on_toolbox_toggled)

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
        The first three pages are named 'Main', 'Face', and 'Prop' automatically.
        Subsequent pages prompt the user for a name.
        """
        # Check the current tab
        current_tab = self.tab_manager.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid character tab found.")
            return

        # Determine the next page name based on the number of existing pages
        page_count = current_tab.stacked_widget.count()
        if page_count == 0:
            page_name = "Body"
        elif page_count == 1:
            page_name = "Face"
        elif page_count == 2:
            page_name = "Prop"
        else:
            # Prompt for a name if no name is provided
            if not page_name:
                page_name, ok = QtWidgets.QInputDialog.getText(self, "Add Page", "Enter page name:")
                if not ok:  # User canceled
                    return
                if not page_name.strip():  # Empty name provided
                    QtWidgets.QMessageBox.warning(self, "Warning", "Page name cannot be empty.")
                    return

        # Add the page to the current tab
        self.tab_manager.add_page_to_current(page_name)

    def handle_context_delete_button(self):
        """
        Called when user chooses 'Delete Button' from the right-click context menu.
        """
        btn = self.context_menu.selected_button

        self.delete_selected_picker_button(btn)

    def handle_menu_add_button(self, checked=False):
        """
        Called when the user picks "Add Button" from the menu action.
        Always create a new picker button by deselecting any currently selected button first.
        """
        # Force deselection
        self.set_selected_picker_button(None)
        # Then call the same method the ToolBox uses
        self.edit_box.handle_submit_clicked()

    def rename_current_character(self):
        """Logic to rename the selected tab."""
        current_index = self.tab_manager.currentIndex()  # Use TabManager's currentIndex
        if current_index == self.tab_manager.count() - 1:  # Prevent renaming the "Add Character" tab
            QtWidgets.QMessageBox.warning(self, "Warning", "Cannot rename the 'Add Character' tab.")
            return

        # Get the current tab name and prompt for a new name
        current_tab_name = self.tab_manager.tabText(current_index)
        new_tab_name, ok = QtWidgets.QInputDialog.getText(
            self, "Rename Tab", f"Enter a new name for '{current_tab_name}':"
        )

        # Validate and apply the new name
        if ok and new_tab_name.strip():
            self.tab_manager.setTabText(current_index, new_tab_name.strip())
        elif ok:  # If the user pressed OK but provided no input
            QtWidgets.QMessageBox.warning(self, "Warning", "Tab name cannot be empty.")

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

    def rename_current_page(self):
        """Logic to rename the currently selected page."""
        # Get the current tab
        current_tab = self.tab_manager.currentWidget()
        if not current_tab or not hasattr(current_tab, 'stacked_widget'):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid character tab is selected.")
            return

        # Get the current page
        stacked_widget = current_tab.stacked_widget
        current_page = stacked_widget.currentWidget()
        if not current_page or not hasattr(current_page, "page_name"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid page is selected.")
            return

        # Prompt the user for a new page name
        current_page_name = getattr(current_page, "page_name", "")
        new_page_name, ok = QtWidgets.QInputDialog.getText(
            self, "Rename Page", f"Enter a new name for '{current_page_name}':"
        )

        # Validate and apply the new page name
        if ok and new_page_name.strip():
            current_page.page_name = new_page_name.strip()

            # Update the corresponding button in the page_button_layout
            for page_button, page_obj in current_tab.page_buttons.items():
                if page_obj == current_page:
                    page_button.setText(new_page_name.strip())
                    break
        elif ok:  # If the user pressed OK but provided no input
            QtWidgets.QMessageBox.warning(self, "Warning", "Page name cannot be empty.")

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

    def resize_for_toolbox(self, is_open, height_change, is_top_level=False):
        """
        Adjust the window height dynamically for both top-level ToolBox and sub-sections.

        :param is_open: Whether the toggled item is being opened or closed.
        :param height_change: The height adjustment to apply (positive for open, negative for close).
        :param is_top_level: Whether this is for the top-level ToolBox (default: False).
        """
        # Current window size
        current_size = self.size()

        # Ensure height change is calculated properly
        if height_change == 0:
            print("No height change detected.")
            return

        if not is_open:
            # Reverse the height change for collapsing
            height_change = -abs(height_change)

        # Apply the new height
        new_height = current_size.height() + height_change

        # Ensure we don't go below the minimum height
        new_height = max(self.minimumHeight(), new_height)

        # Apply the resize
        self.resize(current_size.width(), new_height)

    def submit_picker(self, data_dict):
        """
        Called when user clicks the 'Submit' button in the ToolBox (or triggers from a menu).
        If no button is selected, create a new picker button.
        If a button is selected, update the existing one.
        """
        if self.selected_picker_button is None:
            # Create a new picker button
            self._create_picker_button(data_dict)
        else:
            # Update the currently selected picker button
            self._update_picker_button(self.selected_picker_button, data_dict)

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

    def delete_selected_picker_button(self, btn=None):
        """
        Remove the currently selected button from the grid and from the UI,
        or remove the specific 'btn' if provided.
        """
        # If btn is not passed, use the selected_picker_button
        if btn is None:
            btn = self.selected_picker_button

        # If we still have no button, show a warning
        if not btn:
            QtWidgets.QMessageBox.warning(self, "Warning", "No button selected (or provided).")
            return

        # If btn is actually the currently selected button, deselect it
        if btn == self.selected_picker_button:
            self.selected_picker_button = None
            self.edit_box.update_picker_button_fields(None)

        # Remove from the parent
        btn.setParent(None)
        btn.deleteLater()

        print(f"Picker button '{btn.text()}' deleted successfully.")

    def on_picker_button_event(self, event_type, btn):
        """
        A central place for 'selected', 'deselect', 'moved', 'run_command', etc.
        This method can be triggered from tab_manager or grid_widget
        when a button_event is emitted.
        """
        if event_type == "selected":
            self.set_selected_picker_button(btn)
            print(f"[CharacterPicker] Received event '{event_type}' from button '{btn.text()}'")
        elif event_type == "deselect":
            self.set_selected_picker_button(None)
            print(f"[CharacterPicker] Received event '{event_type}'")
        elif event_type == "moved":
            # Maybe update some fields in the EditBox if this is the selected button
            if self.selected_picker_button == btn:
                self.edit_box.update_picker_button_fields(btn)
            print(f"[CharacterPicker] Received event '{event_type}' from button '{btn.text()}'")
        elif event_type == "run_command":
            # The user clicked the button in Animate Mode
            print(f"Executing command for {btn.text()}")
            # Possibly call btn.execute_command()
        else:
            print(f"Unknown picker event: {event_type} for button {btn.text() if btn else 'None'}")

    def _create_picker_button(self, data_dict):
        """
        Actually create and place a new picker button based on data_dict.
        """
        current_grid = self.tab_manager.get_current_grid_widget()
        if not current_grid:
            QtWidgets.QMessageBox.warning(self, "Error", "No valid grid on the current tab.")
            return

        # Actually create it
        new_btn = picker.create_picker_button(current_grid, data_dict)
        self.set_selected_picker_button(new_btn)

    def _update_picker_button(self, btn, data_dict):
        """
        Apply changes to an existing picker button 'btn' with data_dict.
        """
        btn.setText(data_dict["label"])
        gx, gy = data_dict["grid_pos"]
        w, h = data_dict["size_in_cells"]

        btn.grid_x, btn.grid_y = gx, gy
        btn.width_in_cells, btn.height_in_cells = w, h
        btn.place_in_grid()
        # If you have shape/color/command, set them here
        # e.g. btn.shape = merged_data["shape"]
        #      btn.color = merged_data["color"]
        #      btn.command = merged_data["command_string"]

        # Re-populate the EditBox to reflect the new data (optional)
        self.edit_box.update_picker_button_fields(btn)

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

        self._reconnect_grid_signals()

    def on_page_changed(self, index):
        """
        Called whenever the current QStackedWidget in TabManager changes pages.
        """
        current_tab = self.tab_manager.currentWidget()
        if not current_tab or not hasattr(current_tab, 'stacked_widget'):
            self.edit_box.set_page_name_field("")
            return

        # 1) Update page name in EditBox
        current_page = current_tab.stacked_widget.widget(index)
        if hasattr(current_page, "page_name"):
            self.edit_box.set_page_name_field(current_page.page_name)
        else:
            self.edit_box.set_page_name_field("")

        self._reconnect_grid_signals()

    def _reconnect_grid_signals(self):
        """
        Consolidate your connect/disconnect logic here,
        so both on_tab_changed and on_page_changed can call it.
        """
        new_grid = self.tab_manager.get_current_grid_widget()
        if self._connected_grid and self._connected_grid != new_grid:
            try:
                self._connected_grid.picker_event.disconnect(self.on_picker_button_event)
            except (TypeError, RuntimeError):
                pass
            self._connected_grid = None

        if new_grid and new_grid != self._connected_grid:
            new_grid.picker_event.connect(self.on_picker_button_event)
            self._connected_grid = new_grid

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


