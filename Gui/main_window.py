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
        self.setMinimumSize(500, 800)  # Set a minimum size to avoid UI breaking

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
        self.selected_picker_buttons = []

        # Manually force the UI to reflect the tab and page default name
        current_index = self.tab_manager.currentIndex()
        self.on_tab_changed(current_index)

        # Connect signals
        self.connect_signals()

        # Populate default values when the UI is first loaded
        #self.update_toolbox_display() 


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

        self.menu_bar.frame_action.triggered.connect(self.handle_frame_all)
        self.menu_bar.zoom_in_action.triggered.connect(self.handle_zoom_in)
        self.menu_bar.zoom_out_action.triggered.connect(self.handle_zoom_out)

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
        Called by menubar or context menu to add a button.
        We always deselect the current button, then either place a new one at the context 
        menu's grid position or use the Toolbox spinbox if grid_pos is None.
        """
        # 1) Force deselection
        self.clear_multi_select()

        # 2) Read & reset the context menu pos
        grid_pos = getattr(self.context_menu, "grid_pos", None)
        self.context_menu.grid_pos = None  # Reset for next time

        # 3) Call the Toolbox submission with optional override
        self.edit_box.handle_submit_clicked(external_grid_pos=grid_pos)

    def handle_frame_all(self):
        """Called when the menubar's 'Frame All' action is triggered."""
        current_grid = self.tab_manager.get_current_grid_widget()
        if not current_grid:
            print("No valid grid to frame.")
            return
        # Call the grid's frame_all method
        current_grid.frame_all()

    def handle_zoom_in(self):
        current_grid = self.tab_manager.get_current_grid_widget()
        if current_grid:
            current_grid.apply_zoom(+2)  # or +1 for smaller step

    def handle_zoom_out(self):
        current_grid = self.tab_manager.get_current_grid_widget()
        if current_grid:
            current_grid.apply_zoom(-2)

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
        If exactly one button is selected, update that one.
        If multiple are selected, you can decide how to handle:
        - Possibly just update the *last* one in self.selected_picker_buttons
        - Or do nothing / show a warning
        """
        num_selected = len(self.selected_picker_buttons)

        if num_selected == 0:
            # Create a new picker button
            self._create_picker_button(data_dict)
        elif num_selected == 1:
            # Update the single selected button
            btn = self.selected_picker_buttons[0]
            self._update_picker_button(btn, data_dict)
        else:
            # Multiple selected
            # 1) You can pick the last one:
            #    btn = self.selected_picker_buttons[-1]
            #    self._update_picker_button(btn, data_dict)
            # OR 2) do nothing:
            print("Multiple buttons selected, not sure which one to update. Doing nothing.")


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
        self.add_button_to_multi_select(new_btn, shift_pressed=False)

    def _update_picker_button(self, btn, data_dict):
        """
        Apply changes to an existing picker button 'btn' with data_dict.
        """
        # Update explicit attributes using property setters
        if "label" in data_dict:
            btn.setText(data_dict["label"])
            btn.data_dict["label"] = data_dict["label"]

        if "grid_pos" in data_dict:
            btn.grid_pos = data_dict["grid_pos"]

        if "size_in_cells" in data_dict:
            btn.size_in_cells = data_dict["size_in_cells"]

        if "shape" in data_dict:
            btn.shape = data_dict["shape"]

        if "color" in data_dict:
            btn.color = data_dict["color"]

        if "command_mode" in data_dict:
            btn.command_mode = data_dict["command_mode"]

        if "command_string" in data_dict:
            btn.command_string = data_dict["command_string"]

        # Trigger repaint to reflect new shape/color
        btn.update()

        # Optionally, update the EditBox fields
        self.edit_box.update_picker_button_fields(btn)

    def add_button_to_multi_select(self, btn, shift_pressed):
        """
        SHIFT + left-click => add to existing selection
        No SHIFT => single selection (clear others first).
        """
        # If SHIFT not pressed => clear old selection
        if not shift_pressed:
            self.clear_multi_select()  # We'll define this too

        # If button already in the list, do nothing or remove it (your preference).
        if btn in self.selected_picker_buttons:
            # Toggle off? or do nothing. Let's toggle off:
            self.selected_picker_buttons.remove(btn)
            btn.set_unselected_style()
            if btn.command_mode == "Select":
                btn.deselect_objects()
            print(f"{btn.text()} was toggled off.")
        else:
            self.selected_picker_buttons.append(btn)
            btn.set_selected_style()
            print(f"{btn.text()} toggled ON")

        self.update_toolbox_display()

    def remove_button_from_multi_select(self, btn):
        """
        Called when event_type == 'deselect' or the user re-clicks the same button, etc.
        """
        if btn in self.selected_picker_buttons:
            self.selected_picker_buttons.remove(btn)
            btn.set_unselected_style()
            if btn.command_mode == "Select":
                btn.deselect_objects()
            print(f"{btn.text()} forcibly removed from selection.")
        self.update_toolbox_display()

    def clear_multi_select(self):
        """
        Deselect all selected picker buttons.
        """
        for b in self.selected_picker_buttons[:]:
            b.set_unselected_style()
            if b.command_mode == "Select":
                b.deselect_objects()
        self.selected_picker_buttons.clear()
        self.update_toolbox_display()

    def update_toolbox_display(self):
        """
        If exactly one button is selected, show its data in the EditBox.
        If zero or multiple, show None (defaults).
        """
        num_selected = len(self.selected_picker_buttons)
        if num_selected == 1:
            btn = self.selected_picker_buttons[0]
            self.edit_box.update_picker_button_fields(btn)
        else:
            # Show defaults
            self.edit_box.update_picker_button_fields(None)

    def delete_selected_picker_button(self, btn=None, *args):
        """
        Remove the specified 'btn'. If no btn is given,
        we'll remove the *last* selected button if exactly one is selected.
        """
        # 1) If no btn is passed, see if we have a single or multiple
        if btn is None:
            if not self.selected_picker_buttons:
                QtWidgets.QMessageBox.warning(self, "Warning", "No button is currently selected.")
                return
            elif len(self.selected_picker_buttons) > 1:
                QtWidgets.QMessageBox.warning(self, "Warning", "Multiple buttons are selected. Specify which one to delete.")
                return
            else:
                # Exactly one
                btn = self.selected_picker_buttons[0]

        print(f"Attempting to delete picker button: {btn.text() if btn else 'None'}")

        if not btn:
            QtWidgets.QMessageBox.warning(self, "Warning", "No button selected (or provided).")
            return

        # 2) Remove from our multi-select list if present
        if btn in self.selected_picker_buttons:
            self.selected_picker_buttons.remove(btn)

        # Clear the Toolbox display if you want 
        self.update_toolbox_display()

        # 3) Remove the button from the UI
        btn.setParent(None)
        btn.deleteLater()

        print(f"Picker button '{btn.text()}' deleted successfully.")


    def on_picker_button_event(self, event_type, btn, shift_pressed=False):
        """
        A central place for 'selected', 'deselect', 'moved', 'run_command', etc.
        This method can be triggered from tab_manager or grid_widget
        when a button_event is emitted.
        """
        if event_type == "selected":
            if self.edit_mode:
                self.clear_multi_select()  # Force single selection in Edit Mode
                self.selected_picker_buttons.append(btn)
                btn.set_selected_style()
                self.update_toolbox_display()
            self.add_button_to_multi_select(btn, shift_pressed=False)
            print(f"[CharacterPicker] Received event '{event_type}' from button '{btn.text()}'")
        elif event_type == "deselect":
            # Toggle off if SHIFT not pressed, or forcibly remove from selection
            self.remove_button_from_multi_select(btn)
        elif event_type == "moved":
            # Maybe update some fields in the EditBox if this is the selected button
            if btn in self.selected_picker_buttons:
                self.update_toolbox_display()
            print(f"[CharacterPicker] Received event '{event_type}' from button '{btn.text()}'")
        elif event_type == "run_command":
            # The user clicked the button in Animate Mode          
            if btn.command_mode == "Select":
                # So we can track it for toggling later
                self.add_button_to_multi_select(btn, shift_pressed)           
            print(f"Executing command for {btn.text()}")
            btn.execute_command()  
        else:
            print(f"Unknown picker event: {event_type} for button {btn.text() if btn else 'None'}")

    def on_tab_changed(self, index):
        """
        Handle tab change to update EditBox accordingly.
        Deselect the current picker button,
        then set the EditBox fields to match the new tab/page.
        """
        # 1) Deselect any picker button
        self.clear_multi_select()

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
        Reconnects picker_event from the newly detected GridWidget
        while avoiding duplicate connections.
        """
        new_grid = self.tab_manager.get_current_grid_widget()

        # 1) If the new_grid is exactly the same widget instance, do nothing
        if new_grid is self._connected_grid:
            print("No change in grid. Skipping reconnection.")
            return

        # 2) If we had an old grid, disconnect it
        if self._connected_grid:
            try:
                self._connected_grid.picker_event.disconnect(self.on_picker_button_event)
            except (TypeError, RuntimeError):
                pass
            self._connected_grid = None

        # 3) Now if we have a valid new grid, connect it
        if new_grid:
            new_grid.picker_event.connect(self.on_picker_button_event)

        # 4) Update our reference
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
