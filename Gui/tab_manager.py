from PySide2 import QtWidgets, QtCore, QtGui
import os
import logging
import CharacterPicker.Gui.custom_widgets as custom
import CharacterPicker.Utility.utils as utils
import CharacterPicker.Logic.grid_widget as grid
import CharacterPicker.Logic.picker as picker
import importlib

importlib.reload(custom)
importlib.reload(utils)
importlib.reload(grid)
importlib.reload(picker)

logger = logging.getLogger(__name__)

class PageButtonFrame(QtWidgets.QFrame):
    def __init__(self, icon_dir, context_menu, character_picker, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.icon_dir = icon_dir
        self.context_menu = context_menu
        self.character_picker = character_picker

        # Main horizontal layout
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Layout for dynamic page buttons (left)
        self.dynamic_buttons_layout = QtWidgets.QHBoxLayout()
        self.dynamic_buttons_layout.setSpacing(5)  # Adjust spacing as needed
        self.main_layout.addLayout(self.dynamic_buttons_layout)

        # Permanent button on the right
        self.add_page_button = QtWidgets.QPushButton()
        self.add_page_button.setFixedSize(25, 25)  # Set fixed size
        self.add_page_button.setToolTip("Add Page")
        self.add_page_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
        """)

        # Set the icon for the button
        icon_path = self.icon_dir / "plus.svg"  # Keep it as a Path object
        if icon_path.exists():  # Check existence using Path
            self.add_page_button.setIcon(QtGui.QIcon(str(icon_path)))  # Convert to string when needed
        else:
           logger.error(f"Icon file not found: {icon_path}")

        self.add_page_button.clicked.connect(self.handle_add_page_clicked)
        self.main_layout.addWidget(self.add_page_button)

    def add_dynamic_button(self, button: QtWidgets.QPushButton):
        """Add a new dynamic button to the layout."""
        self.dynamic_buttons_layout.addWidget(button)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            # Show the context menu for the page button area
            self.context_menu.set_context_type('page_buttons')
            self.context_menu.exec_(event.globalPos())
        else:
            super().mousePressEvent(event)

    def handle_add_page_clicked(self):
        """Call the TabManager's add_page_to_current method."""
        if hasattr(self.character_picker, 'handle_add_page'):
            self.character_picker.handle_add_page()
        else:
            logger.error(f"CharacterPicker does not have 'handle_add_page' method.")


class TabManager(QtWidgets.QTabWidget):
    """
    Manages the tabs within the Character Picker tool.
    Handles creation, deletion, and navigation of character tabs.
    """
    # Define a signal to handle picker button events
    picker_event = QtCore.Signal(str, object)  # (event_type, PickerButton)
    # Define a signal to handle page change events
    currentPageChanged = QtCore.Signal(int)  # (the new page index)

    def __init__(self, icon_dir, character_picker=None, context_menu=None):
        super(TabManager, self).__init__(character_picker)
        self.icon_dir = icon_dir
        self.context_menu = context_menu
        self.character_picker = character_picker
        self.setTabBar(custom.FixedSizeTabBar())
        self.init_tabs()

        self.currentChanged.connect(self.update_page_button_styles)

    def init_tabs(self):
        self.add_character_tab("Character 1")
        self.add_character_tab()  # Add the "Add Character Tab"

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            # Check if the click occurred on the tab bar
            if self.tabBar().rect().contains(event.pos()):
                self.context_menu.set_context_type('tab_bar')
                self.context_menu.exec_(event.globalPos())
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
    
    def _on_stacked_widget_changed(self, index):
        """
        This internal method is called whenever the QStackedWidget changes pages.
        We simply emit our custom signal to notify the outside world (main_window).
        """
        self.currentPageChanged.emit(index)

    def add_character_tab(self, character_name=None, character_pic_path=""):
        """
        Create and add a new character tab to the TabManager.
        If character_name is None, adds the "NEW" placeholder tab.
        Otherwise, creates a fully functional tab, then calls add_page_to_current("Main")
        so that 'Main' is created the same way as other pages.
        """
        if character_name is None:
            # Existing code for the "NEW" tab
            add_tab_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(add_tab_widget)
            label = QtWidgets.QLabel("To begin, add a character")
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label)

            # Use the plus.svg icon
            icon_path = str(self.icon_dir / "plus.svg")
            icon = QtGui.QIcon(icon_path)
            self.setIconSize(QtCore.QSize(50, 50))

            # Insert the "NEW" tab at the end
            self.addTab(add_tab_widget, icon, "NEW")
            self.tabBar().tabBarClicked.connect(self.on_tab_bar_clicked)

        else:
            # Create a regular character tab
            character_tab = QtWidgets.QWidget()

            # Store any custom attributes on this character_tab
            character_tab.character_pic_path = None  # Holds the path for the character picture

            def set_tab_icon(image_path=None):
                """
                Update the tab icon for THIS character tab
                and store the path so we can retrieve it later.
                Return the QIcon created so the caller can insertTab with it.
                """
                if not image_path:
                    image_path = utils.get_random_icon()

                if not os.path.exists(image_path):
                    logger.warning(f"Icon path does not exist: {image_path}")
                    icon = QtGui.QIcon()  # Default icon
                else:
                    icon = QtGui.QIcon(image_path)

                tab_index = self.indexOf(character_tab)
                if tab_index >= 0:
                    # Update the tab’s icon
                    self.setTabIcon(tab_index, icon)
                else:
                    logger.error(f"Character tab not found in TabManager.")

                character_tab.character_pic_path = image_path

                return icon

            # Attach this method to the character_tab instance
            character_tab.set_tab_icon = set_tab_icon

            # Set up layouts and widgets within the character_tab
            main_layout = QtWidgets.QVBoxLayout(character_tab)
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)

            # Create a frame to hold the page buttons
            page_button_frame = PageButtonFrame(self.icon_dir, self.context_menu, self.character_picker, self)
            page_button_frame.setStyleSheet("""
                QFrame {
                    border: none;
                    border-bottom: 1px solid #2d2d2d;
                }
            """)

            # Create the layout for the page buttons and add it to the frame
            page_button_layout = QtWidgets.QHBoxLayout(page_button_frame)
            page_button_layout.setContentsMargins(10, 10, 10, 10)
            page_button_layout.setSpacing(5)  # Adjust spacing as needed

            # Assign the frame and layout to the character_tab
            character_tab.page_button_frame = page_button_frame
            character_tab.page_button_layout = page_button_layout

            # Add the frame containing the page buttons to the main layout
            main_layout.addWidget(page_button_frame)

            # Create a QStackedWidget for the pages
            stacked_widget = QtWidgets.QStackedWidget()
            main_layout.addWidget(stacked_widget)
            character_tab.stacked_widget = stacked_widget

            stacked_widget.currentChanged.connect(self._on_stacked_widget_changed)

            # Initialize an empty dict for page buttons
            character_tab.page_buttons = {}

            # Insert the new character tab just before the "NEW" tab
            # Use a temporary icon initially (can be empty or a default icon)
            temp_icon = QtGui.QIcon()
            self.insertTab(self.count() - 1, character_tab, temp_icon, character_name)
            self.setCurrentIndex(self.count() - 2)

            # Now that the tab is inserted, set the actual icon
            # Store original icon
            tab_index = self.indexOf(character_tab)
            original_icon = character_tab.set_tab_icon()  # image_path=None to get a random icon
            self.setTabIcon(tab_index, original_icon)

            # Set the background image for the first page
            default_image_path = str(self.icon_dir / "bodyBackground.svg")
            self.add_page_to_current("Body", default_image_path)

            self.update_page_button_styles()

            return self.indexOf(character_tab)

    def on_tab_bar_clicked(self, index):
        if index == self.count() - 1:
            self.add_character_tab(f"Character {self.count()}")

    def update_page_button_styles(self):
        current_tab = self.currentWidget()
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

    def get_current_grid_widget(self):
        """
        Return the GridWidget of the currently selected tab/page, or None if invalid.
        """
        current_tab = self.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            return None

        current_page = current_tab.stacked_widget.currentWidget()
        if isinstance(current_page, grid.GridWidget):
            return current_page
        return None

    def on_picker_event(self, event_type, picker_button):
        """Handle picker button events."""
        if event_type == "selected":
            self.parent().update_picker_button_fields(picker_button)
        elif event_type == "moved":
            # Handle moved event if needed
            pass
        elif event_type == "deselect":
            self.parent().update_picker_button_fields(None)

    def add_page_to_current(self, page_name, background_image="", bg_scale_factor=1.0, bg_offset=(0.0, 0.0)):
        """
        Add a new sub-page (GridWidget) to the current character tab with optional background settings.
        """
        current_tab = self.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            QtWidgets.QMessageBox.warning(self.character_picker, "Warning", "No valid character tab selected.")
            return

        if not page_name.strip():
            QtWidgets.QMessageBox.warning(self, "Warning", "Page name cannot be empty.")
            return

        # Create a new GridWidget (page)
        new_page = grid.GridWidget(rows=grid.GridWidget.DEFAULT_ROWS, cols=grid.GridWidget.DEFAULT_COLS, parent=current_tab, context_menu=self.context_menu)
        new_page.page_name = page_name
        new_page.background_image = background_image  # Store background image path

        # Set background image, scale, and offset if provided
        if background_image:
            QtCore.QTimer.singleShot(0, lambda:new_page.set_background_image(background_image))
        new_page.bg_scale_factor = bg_scale_factor
        new_page.bg_offset_gx, new_page.bg_offset_gy = bg_offset

        # Add the page to the stacked_widget
        current_tab.stacked_widget.addWidget(new_page)

        # Create a navigation button for the new page
        page_button = QtWidgets.QPushButton(page_name)
        page_button.setFixedHeight(40)  # Adjust as needed
        # Set font to bold
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(12)  # Adjust font size as needed
        page_button.setFont(font)
        page_button.clicked.connect(lambda *args, page=new_page: self.switch_to_page(page))

        # Add the button to the dynamic_buttons_layout
        current_tab.page_button_frame.add_dynamic_button(page_button)

        # Store the reference in page_buttons dict
        current_tab.page_buttons[page_button] = new_page

        # Switch to the new page
        current_tab.stacked_widget.setCurrentWidget(new_page)
        self.update_page_button_styles()

        # Using logger instead of print
        logger.info(f"Page '{page_name}' added successfully.")


    def switch_to_page(self, page_widget):
        """
        Switch the current view to the specified page_widget.
        """
        current_tab = self.currentWidget()
        if not current_tab:
            return
        current_tab.stacked_widget.setCurrentWidget(page_widget)
        self.update_page_button_styles()

    def set_current_page_background(self, image_path=None):
        """
        Set the background image for the current page's GridWidget.
        If no image_path is provided, prompt the user to select one.
        """
        if not image_path:
            image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select Background Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.svg)"
            )
            if not image_path:  # User canceled or no file selected
                return

        current_tab = self.currentWidget()
        if current_tab and hasattr(current_tab, "stacked_widget"):
            current_page = current_tab.stacked_widget.currentWidget()
            if current_page and isinstance(current_page, grid.GridWidget):
                current_page.set_background_image(image_path)
            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "Current page does not support background images.")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid page is selected.")

    def gather_current_character_data(self):
        """
        Gathers all data from the currently selected character tab.
        Returns a dictionary matching the JSON structure.
        """
        current_index = self.currentIndex()
        if current_index == -1:
            QtWidgets.QMessageBox.warning(self, "Warning", "No character tab is currently selected.")
            return None

        # Prevent saving the "NEW" tab
        if current_index == self.count() - 1:
            QtWidgets.QMessageBox.warning(self, "Warning", "Cannot save the 'NEW' tab.")
            return None

        current_tab = self.widget(current_index)
        character_name = self.tabText(current_index)
        character_pic_filename = getattr(current_tab, "character_pic_path", "")

        pages_dict = {}
        stacked_widget = getattr(current_tab, "stacked_widget", None)
        if not stacked_widget:
            QtWidgets.QMessageBox.warning(self, "Warning", "Current tab does not contain any pages.")
            return None

        for page_index in range(stacked_widget.count()):
            page_widget = stacked_widget.widget(page_index)
            page_name = getattr(page_widget, "page_name", f"Page {page_index + 1}")
            background_image = getattr(page_widget, "background_image", "")
            bg_scale_factor = getattr(page_widget, "bg_scale_factor", 1.0)
            bg_offset_gx = getattr(page_widget, "bg_offset_gx", 0.0)
            bg_offset_gy = getattr(page_widget, "bg_offset_gy", 0.0)

            # **Include the current grid cell size (zoom level)**
            cell_size = getattr(page_widget, "cell_size", 40)
            logger.info(f"Cell size for page '{page_name}': {cell_size}")   

            buttons_data = []
            for btn in page_widget.findChildren(picker.PickerButton):
                btn_data = {
                    "label": btn.data_dict.get("label", ""),
                    "grid_pos": list(btn.grid_pos),
                    "size_in_cells": list(btn.size_in_cells),
                    "shape": btn.shape,
                    "color": btn.color.name(QtGui.QColor.HexRgb),
                    "command_mode": btn.command_mode,
                    "command_string": btn.command_string,
                    "opacity": btn.opacity,
                    "direction": btn.direction
                }
                buttons_data.append(btn_data)

            pages_dict[page_name] = {
                "page_name": page_name,
                "background_image": background_image,
                "bg_scale_factor": bg_scale_factor,
                "bg_offset_gx": bg_offset_gx,
                "bg_offset_gy": bg_offset_gy,
                "cell_size": cell_size,
                "buttons": buttons_data
            }

        character_data = {
            "character_name": character_name,
            "character_pic_filename": character_pic_filename,
            "pages": list(pages_dict.values())
        }

        return character_data

    def _gather_buttons_from_grid(self, page_obj):
        """
        Extracts data from all picker buttons within the given page's GridWidget.
        Returns a list of button dictionaries.
        """
        button_list = []
        for btn in page_obj.grid_widget.findChildren(picker.PickerButton):
            btn_data = btn.data_dict.copy()
            btn_data["color"] = btn.color.name()  # Ensure color is stored as hex string
            button_list.append(btn_data)
        return button_list

    def load_character_into_tab(self, character_dict):
        character_name = character_dict.get("character_name", "Unnamed Character")
        character_pic_filename = character_dict.get("character_pic_filename", "")

        # Create a new character tab using your existing routine.
        new_tab_index = self.add_character_tab(character_name, character_pic_filename)
        new_tab = self.widget(new_tab_index)
        new_tab.character_pic_path = character_pic_filename

        # Update the tab icon to use the saved profile picture.
        try:
            new_tab.set_tab_icon(character_pic_filename)
        except Exception as e:
            logger.error(f"Error setting tab icon: {e}")  

        # **** Remove all existing pages and clear navigation buttons ****
        while new_tab.stacked_widget.count() > 0:
            widget = new_tab.stacked_widget.widget(0)
            new_tab.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        # Also clear the navigation buttons from the page button frame:
        layout = new_tab.page_button_frame.dynamic_buttons_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear the page_buttons dictionary
        new_tab.page_buttons = {}

        # Iterate over saved pages
        for page_info in character_dict.get("pages", []):
            page_name = page_info.get("page_name", "Unnamed Page")
            background_image = page_info.get("background_image", "")
            bg_scale_factor = page_info.get("bg_scale_factor", 1.0)
            bg_offset = (page_info.get("bg_offset_gx", 0), page_info.get("bg_offset_gy", 0))
            saved_cell_size = page_info.get("cell_size", 40)  # Retrieve saved cell size

            # Create a new page using GridWidget.
            new_page = grid.GridWidget(
                rows=grid.GridWidget.DEFAULT_ROWS,
                cols=grid.GridWidget.DEFAULT_COLS,
                parent=new_tab,
                context_menu=self.context_menu
            )
            new_page.page_name = page_name
            new_page.background_image = background_image
            new_page.bg_scale_factor = bg_scale_factor
            new_page.bg_offset_gx, new_page.bg_offset_gy = bg_offset

            # Restore the saved grid cell size (zoom level)
            new_page.cell_size = saved_cell_size

            # Use a timer to set the background image so that the correct value is captured.
            if background_image:
                QtCore.QTimer.singleShot(
                    0, lambda bg=background_image, page=new_page: page.set_background_image(bg)
                )

            # Add the new page to the stacked widget.
            new_tab.stacked_widget.addWidget(new_page)

            # Create a navigation button for this page.
            page_button = QtWidgets.QPushButton(page_name)
            page_button.setFixedHeight(40)
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(12)
            page_button.setFont(font)
            page_button.clicked.connect(lambda *args, page=new_page: self.switch_to_page(page))
            new_tab.page_button_frame.add_dynamic_button(page_button)
            new_tab.page_buttons[page_button] = new_page

            # Recreate picker buttons on this page.
            for btn_info in page_info.get("buttons", []):
                picker.create_picker_button(new_page, btn_info)

        # Set the current page to the first one.
        if new_tab.stacked_widget.count() > 0:
            new_tab.stacked_widget.setCurrentIndex(0)

        self.update_page_button_styles()

        current_tab = self.currentWidget()
        for i in range(current_tab.stacked_widget.count()):
            page = current_tab.stacked_widget.widget(i)
            # Force the page to match the current tab’s size (or another appropriate size)
            page.resize(current_tab.size())
            page.reposition_all_buttons()
            page.update()

        logger.info(f"Character '{character_name}' loaded successfully.")  
