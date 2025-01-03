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


class TabManager(QtWidgets.QTabWidget):
    """
    Manages the tabs within the Character Picker tool.
    Handles creation, deletion, and navigation of character tabs.
    """
    # Define a signal to handle picker button events
    picker_event = QtCore.Signal(str, object)  # (event_type, PickerButton)
    # Define a signal to handle page change events
    currentPageChanged = QtCore.Signal(int)  # (the new page index)

    def __init__(self, icon_dir, parent=None, context_menu=None):
        super(TabManager, self).__init__(parent)
        self.icon_dir = icon_dir
        self.context_menu = context_menu
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
            page_button_frame = QtWidgets.QFrame()
            page_button_frame.setStyleSheet("""
                QFrame {
                    border: none;
                    border-bottom: 1px solid #2d2d2d;
                }
            """)
            page_button_layout = QtWidgets.QHBoxLayout(page_button_frame)
            page_button_layout.setContentsMargins(10, 10, 10, 10)

            # Store a reference to the layout on the tab object
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
            self.add_page_to_current("Main")

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

    def add_picker_button(self, picker_data):
        """Add a picker button based on the provided picker_data."""
        current_tab = self.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid character tab selected.")
            return

        current_page = current_tab.stacked_widget.currentWidget()
        if isinstance(current_page, grid.GridWidget):
            label = picker_data.get("label", "NewButton")
            grid_pos = picker_data.get("grid_pos", (0, 0))
            size_in_cells = picker_data.get("size_in_cells", (1, 1))

            # Create the PickerButton instance
            picker_button = picker.create_picker_button(
                label=label,
                grid_pos=grid_pos,
                size_in_cells=size_in_cells,
                parent_grid=current_page
            )
            picker_button.button_event.connect(self.on_picker_event)

            # Add to the grid
            current_page.add_picker_button(picker_button)
            self.parent().update_picker_button_fields(picker_button)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Current page is not a valid GridWidget.")

    def add_button_to_current(self):
        """Add a button to the current sub-page with default picker_data."""
        default_picker_data = {
            "label":"NewButton",
            "grid_pos":(0, 0),
            "size_in_cells":(1, 1)
        }
        self.add_picker_button(default_picker_data)

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

        # Add the new button to the page_button_layout
        current_tab.page_button_layout.addWidget(page_button)

        # Store the reference in page_buttons dict
        current_tab.page_buttons[page_button] = new_page

        # Switch immediately to the new page
        current_tab.stacked_widget.setCurrentWidget(new_page)
        self.update_page_button_styles()

