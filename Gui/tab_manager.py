from PySide2 import QtWidgets, QtCore, QtGui
import os
import CharacterPicker.Gui.custom_widgets as custom
import CharacterPicker.Utility.utils as utils
import CharacterPicker.Logic.grid_widget as grid
import CharacterPicker.Logic.picker as picker


class TabManager(QtWidgets.QTabWidget):
    """
    Manages the tabs within the Character Picker tool.
    Handles creation, deletion, and navigation of character tabs.
    """
    # Define a signal to handle picker button events
    picker_event = QtCore.Signal(str, object)  # (event_type, PickerButton)

    def __init__(self, icon_dir, parent=None):
        super(TabManager, self).__init__(parent)
        self.icon_dir = icon_dir
        self.setTabBar(custom.FixedSizeTabBar())
        self.init_tabs()

    def init_tabs(self):
        self.add_character_tab("Character 1")
        self.add_character_tab()  # Add the "Add Character Tab"

    def add_character_tab(self, character_name=None):
        if character_name is None:  # Add the "Add Character Tab"
            add_tab_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(add_tab_widget)
            label = QtWidgets.QLabel("To begin, add a character")
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label)

            icon_path = os.path.join(self.icon_dir, "plus.svg")
            icon = QtGui.QIcon(icon_path)
            self.setIconSize(QtCore.QSize(50, 50))
            self.addTab(add_tab_widget, icon, "NEW")
            self.tabBar().tabBarClicked.connect(self.on_tab_bar_clicked)
        else:
            character_tab = QtWidgets.QWidget()
            main_layout = QtWidgets.QVBoxLayout(character_tab)
            main_layout.setSpacing(0)  # Remove spacing between sections
            main_layout.setContentsMargins(0, 0, 0, 0)

            # Page button section with a bottom border only
            page_button_frame = QtWidgets.QFrame()
            page_button_frame.setStyleSheet("""
                QFrame {
                    border: none;
                    border-bottom: 1px solid #2D2D2D;
                }
            """)
            page_button_layout = QtWidgets.QHBoxLayout(page_button_frame)
            page_button_layout.setContentsMargins(10, 10, 10, 10)

            # Add a button for the main page
            main_button = QtWidgets.QPushButton("Main")
            page_button_layout.addWidget(main_button)

            # Store a reference to the page_button_frame
            character_tab.page_button_frame = page_button_frame

            # Add the page button frame to the main layout
            main_layout.addWidget(page_button_frame)

            # Grid section
            stacked_widget = QtWidgets.QStackedWidget()
            main_layout.addWidget(stacked_widget)

            # Create the main grid page
            main_page = grid.GridWidget(rows=grid.GridWidget.DEFAULT_ROWS, cols=grid.GridWidget.DEFAULT_COLS)
            stacked_widget.addWidget(main_page)

            # Connect the main button to switch to the main page
            main_button.clicked.connect(lambda:stacked_widget.setCurrentWidget(main_page))

            # Store references for saving/loading
            character_tab.stacked_widget = stacked_widget
            character_tab.page_buttons = {main_button:main_page}

            # Add the tab to the TabManager
            random_icon_path = utils.get_random_icon()
            tab_icon = QtGui.QIcon(random_icon_path)
            self.insertTab(self.count() - 1, character_tab, tab_icon, character_name)
            self.setCurrentIndex(self.count() - 2)

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
            self.parent().set_selected_picker_button(picker_button)
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
            self.parent().set_selected_picker_button(picker_button)
        elif event_type == "moved":
            # Handle moved event if needed
            pass
        elif event_type == "deselect":
            self.parent().set_selected_picker_button(None)

    def add_page_to_current(self, page_name):
        """Add a new sub-page to the current character tab."""
        current_tab = self.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid character tab selected.")
            return

        if not page_name.strip():
            QtWidgets.QMessageBox.warning(self, "Warning", "Page name cannot be empty.")
            return

        # Access the stacked widget
        stacked_widget = current_tab.stacked_widget
        new_page = grid.GridWidget(rows=grid.GridWidget.DEFAULT_ROWS, cols=grid.GridWidget.DEFAULT_COLS)
        stacked_widget.addWidget(new_page)

        # Create the page button
        page_button = QtWidgets.QPushButton(page_name)
        page_button.clicked.connect(
            lambda checked=False, page=new_page:(
                stacked_widget.setCurrentWidget(page), self.update_page_button_styles()
            )
        )

        # Use the explicit reference to page_button_frame
        if hasattr(current_tab, "page_button_frame"):
            page_button_frame = current_tab.page_button_frame
            page_button_layout = page_button_frame.layout()
            if page_button_layout:
                page_button_layout.addWidget(page_button)
            else:
                print("Error: page_button_frame layout is missing!")
                return
        else:
            print("Error: current_tab does not have page_button_frame!")
            return

        # Update references and styles
        current_tab.page_buttons[page_button] = new_page
        stacked_widget.setCurrentWidget(new_page)
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
            self.parent().set_selected_picker_button(picker_button)
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
            self.parent().set_selected_picker_button(picker_button)
        elif event_type == "moved":
            # Handle moved event if needed
            pass
        elif event_type == "deselect":
            self.parent().set_selected_picker_button(None)

    def add_page_to_current(self, page_name):
        """Add a new sub-page to the current character tab."""
        current_tab = self.currentWidget()
        if not current_tab or not hasattr(current_tab, "stacked_widget"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No valid character tab selected.")
            return

        if not page_name.strip():
            QtWidgets.QMessageBox.warning(self, "Warning", "Page name cannot be empty.")
            return

        stacked_widget = current_tab.stacked_widget
        new_page = grid.GridWidget(rows=grid.GridWidget.DEFAULT_ROWS, cols=grid.GridWidget.DEFAULT_COLS)
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
