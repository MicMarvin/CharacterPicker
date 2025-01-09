from PySide2 import QtWidgets, QtCore, QtGui
import os
import CharacterPicker.Gui.custom_widgets as custom
import CharacterPicker.Utility.utils as utils
import CharacterPicker.Logic.grid_widget as grid
import CharacterPicker.Logic.picker as picker
import importlib

importlib.reload(custom)
importlib.reload(utils)
importlib.reload(grid)
importlib.reload(picker)


class PageButtonFrame(QtWidgets.QFrame):
    def __init__(self, icon_dir, context_menu, character_picker, parent=None):
        super().__init__(parent)
        self.icon_dir = icon_dir
        self.context_menu = context_menu  # Pass the shared context menu
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
        icon_path = os.path.join(self.icon_dir, "plus.svg")
        if os.path.exists(icon_path):
            self.add_page_button.setIcon(QtGui.QIcon(icon_path))
        else:
            print(f"Icon file not found: {icon_path}")

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
            print("CharacterPicker does not have 'handle_add_page' method.")


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

    def _on_stacked_widget_changed(self, index):
        """
        This internal method is called whenever the QStackedWidget changes pages.
        We simply emit our custom signal to notify the outside world (main_window).
        """
        self.currentPageChanged.emit(index)

    def add_character_tab(self, character_name=None):
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
            icon_path = os.path.join(self.icon_dir, "plus.svg")
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
                    print(f"Icon path does not exist: {image_path}")
                    icon = QtGui.QIcon()  # Default icon
                else:
                    icon = QtGui.QIcon(image_path)

                tab_index = self.indexOf(character_tab)
                if tab_index >= 0:
                    # Update the tab’s icon
                    self.setTabIcon(tab_index, icon)
                else:
                    print("Character tab not found in TabManager.")

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

            # Create the default "Main" page by calling add_page_to_current
            self.add_page_to_current("Body")

            # Set the background image for the first page
            default_image_path = os.path.join(self.icon_dir, "bodyBackground.svg")
            QtCore.QTimer.singleShot(0, lambda:self.set_current_page_background(default_image_path))

            self.update_page_button_styles()


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

    def add_page_to_current(self, page_name):
        """
        Add a new sub-page (GridWidget) to the current character tab.
        Create a new QPushButton in the page_button_layout to switch to it.
        """
        current_tab = self.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid character tab selected.")
            return

        if not page_name.strip():
            QtWidgets.QMessageBox.warning(self, "Warning", "Page name cannot be empty.")
            return

        # Create a new page (GridWidget)
        new_page = grid.GridWidget(rows=grid.GridWidget.DEFAULT_ROWS, cols=grid.GridWidget.DEFAULT_COLS)
        new_page.context_menu = self.context_menu

        # Assign an attribute page_name to this page so the EditBox can see it
        new_page.page_name = page_name

        current_tab.stacked_widget.addWidget(new_page)

        # Create a button to switch to this new page
        page_button = QtWidgets.QPushButton(page_name)
        page_button.clicked.connect(
            lambda checked=False, page=new_page:(
                current_tab.stacked_widget.setCurrentWidget(page),
                self.update_page_button_styles()
            )
        )

        # Add the new button to the dynamic buttons layout
        current_tab.page_button_frame.add_dynamic_button(page_button)

        # Store the reference in page_buttons dict
        current_tab.page_buttons[page_button] = new_page

        # Switch immediately to the new page
        current_tab.stacked_widget.setCurrentWidget(new_page)
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

