from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import json


def maya_main_window():
    """Return Maya's main window widget."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class PickerPage(QtWidgets.QWidget):
    """A single page with a dynamic grid layout."""

    def __init__(self, rows=20, cols=10):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.cell_width = 40
        self.cell_height = 40
        self.buttons = []
        self.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def update_button_position(self, button, grid_x, grid_y):
        """Update the grid position of a button."""
        for i, (b, (old_x, old_y, width, height)) in enumerate(self.buttons):
            if b == button:
                self.buttons[i] = (button, (grid_x, grid_y, width, height))
                break

    def create_button(self, position):
        """Create a new button with a styled dialog."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add Button")

        layout = QtWidgets.QVBoxLayout(dialog)

        label_layout = QtWidgets.QHBoxLayout()
        label_layout.addWidget(QtWidgets.QLabel("Button Label:"))
        label_input = QtWidgets.QLineEdit()
        label_layout.addWidget(label_input)
        layout.addLayout(label_layout)

        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(QtWidgets.QLabel("Width (grid cells):"))
        width_input = QtWidgets.QSpinBox()
        width_input.setMinimum(1)
        width_input.setMaximum(self.cols)
        width_layout.addWidget(width_input)
        layout.addLayout(width_layout)

        height_layout = QtWidgets.QHBoxLayout()
        height_layout.addWidget(QtWidgets.QLabel("Height (grid cells):"))
        height_input = QtWidgets.QSpinBox()
        height_input.setMinimum(1)
        height_input.setMaximum(self.rows)
        height_layout.addWidget(height_input)
        layout.addLayout(height_layout)

        button_layout = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton("OK")
        cancel_button = QtWidgets.QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def accept():
            dialog.accept()

        def reject():
            dialog.reject()

        ok_button.clicked.connect(accept)
        cancel_button.clicked.connect(reject)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            text = label_input.text()
            width = width_input.value()
            height = height_input.value()

            if text:
                button = GridButton(text, parent=self)
                grid_x = round(position.x() / self.cell_width)
                grid_y = round(position.y() / self.cell_height)

                self.buttons.append((button, (grid_x, grid_y, width, height)))
                button.setFixedSize(width * self.cell_width, height * self.cell_height)
                button.move(grid_x * self.cell_width, grid_y * self.cell_height)
                button.show()

    def show_context_menu(self, position):
        """Show context menu for adding buttons or pages."""
        menu = QtWidgets.QMenu(self)
        create_button_action = menu.addAction("Add Button")
        add_page_action = menu.addAction("Add Page")

        action = menu.exec_(self.mapToGlobal(position))
        if action == create_button_action:
            self.create_button(position)
        elif action == add_page_action:
            main_window = self.window()
            if isinstance(main_window, CharacterPicker):
                main_window.add_page_to_current()

    def resizeEvent(self, event):
        """Recalculate cell dimensions and resize buttons."""
        self.cell_width = self.width() // self.cols
        self.cell_height = self.height() // self.rows
        for button, (grid_x, grid_y, grid_width, grid_height) in self.buttons:
            button.setFixedSize(grid_width * self.cell_width, grid_height * self.cell_height)
            button.move(grid_x * self.cell_width, grid_y * self.cell_height)
        self.update()

    def paintEvent(self, event):
        """Draw the grid on the page."""
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(200, 200, 200, 100))
        pen.setWidth(1)
        painter.setPen(pen)

        total_width = self.cell_width * self.cols
        total_height = self.cell_height * self.rows

        for col in range(self.cols + 1):
            x = col * self.cell_width
            painter.drawLine(x, 0, x, total_height)

        for row in range(self.rows + 1):
            y = row * self.cell_height
            painter.drawLine(0, y, total_width, y)

        painter.end()


class GridButton(QtWidgets.QPushButton):
    """Custom button that can snap to grid."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.dragging = False
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.pos() - self.start_pos
            new_x = self.x() + delta.x()
            new_y = self.y() + delta.y()

            parent = self.parentWidget()
            if isinstance(parent, PickerPage):
                cell_width = parent.cell_width
                cell_height = parent.cell_height
                total_width = cell_width * parent.cols
                total_height = cell_height * parent.rows

                snapped_x = max(0, min(round(new_x / cell_width) * cell_width, total_width - self.width()))
                snapped_y = max(0, min(round(new_y / cell_height) * cell_height, total_height - self.height()))
                self.move(snapped_x, snapped_y)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            parent = self.parentWidget()
            if isinstance(parent, PickerPage):
                grid_x = round(self.x() / parent.cell_width)
                grid_y = round(self.y() / parent.cell_height)
                parent.update_button_position(self, grid_x, grid_y)


class CharacterPicker(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CharacterPicker, self).__init__(parent)
        self.setWindowTitle("Character Picker")
        self.resize(500, 800)

        self.create_menu_bar()
        self.tab_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.add_character_tab("New Character")

    def create_menu_bar(self):
        """Add a menu bar with options."""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New Character", self.new_character)
        file_menu.addAction("Save Character...", self.save_character)
        file_menu.addAction("Load Character...", lambda:self.load_character())
        file_menu.addAction("Close Current Tab", self.close_current_tab)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Add Page", self.add_page_to_current)
        edit_menu.addAction("Add Button", self.add_button_to_current)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self.show_about_dialog)

    def new_character(self):
        """Open a dialog to create a new character or load an existing one."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("New Character")

        # Main layout
        layout = QtWidgets.QVBoxLayout(dialog)

        # Radio Buttons
        option_group = QtWidgets.QGroupBox("Select an Option")
        option_layout = QtWidgets.QVBoxLayout(option_group)
        create_new_radio = QtWidgets.QRadioButton("Create New Character")
        load_existing_radio = QtWidgets.QRadioButton("Load Existing Character")
        create_new_radio.setChecked(True)

        option_layout.addWidget(create_new_radio)
        option_layout.addWidget(load_existing_radio)
        layout.addWidget(option_group)

        # Character Name Input
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Character Name:")
        name_input = QtWidgets.QLineEdit()
        name_widget = QtWidgets.QWidget()
        name_widget.setLayout(name_layout)
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)

        # File Path Input
        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_label = QtWidgets.QLabel("File Path:")
        file_path_input = QtWidgets.QLineEdit()
        browse_button = QtWidgets.QPushButton("Browse...")
        file_path_widget = QtWidgets.QWidget()
        file_path_widget.setLayout(file_path_layout)
        file_path_layout.addWidget(file_path_label)
        file_path_layout.addWidget(file_path_input)
        file_path_layout.addWidget(browse_button)
        file_path_widget.hide()  # Start hidden

        # Add both widgets to the main layout
        layout.addWidget(name_widget)
        layout.addWidget(file_path_widget)

        # OK and Cancel Buttons
        button_layout = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton("OK")
        cancel_button = QtWidgets.QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Behavior to toggle visibility
        def toggle_inputs():
            """Toggle visibility between character name and file path inputs."""
            is_new = create_new_radio.isChecked()
            name_widget.setVisible(is_new)
            file_path_widget.setVisible(not is_new)

        create_new_radio.toggled.connect(toggle_inputs)

        # Browse Button Behavior
        def browse_file():
            """Open a file dialog to select an existing character file."""
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select Character File", "", "JSON Files (*.json)"
            )
            if file_path:
                file_path_input.setText(file_path)

        browse_button.clicked.connect(browse_file)

        # OK Button Behavior
        def accept():
            """Handle the user's selection."""
            if create_new_radio.isChecked():
                # Create a new character
                character_name = name_input.text()
                if not character_name.strip():
                    QtWidgets.QMessageBox.warning(dialog, "Error", "Character name cannot be empty.")
                    return
                self.add_character_tab(character_name)
            else:
                # Load an existing character
                file_path = file_path_input.text()
                if not file_path.strip():
                    QtWidgets.QMessageBox.warning(dialog, "Error", "Please select a character file.")
                    return
                self.load_character(file_path)

            dialog.accept()

        ok_button.clicked.connect(accept)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec_()

    def load_character(self, file_path=None):
        """Open a file dialog to load a character from a JSON file."""
        if not file_path:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Load Character", "", "JSON Files (*.json)"
            )
            if not file_path:
                return  # User canceled the file dialog

        try:
            with open(file_path, "r") as f:
                character_data = json.load(f)

            # Remove the "New Character" tab if it exists
            for index in range(self.tab_widget.count()):
                if self.tab_widget.tabText(index) == "New Character":
                    self.tab_widget.removeTab(index)
                    break

            # Add the new character tab from the loaded data
            self.add_character_from_data(character_data)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load character: {e}")

    def add_character_from_data(self, character_data):
        """Add a character to the picker using data from a JSON file."""
        character_name = character_data.get("character", "Unnamed Character")

        # Create a new tab for this character
        character_tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(character_tab)

        # Add page buttons layout
        page_buttons_layout = QtWidgets.QHBoxLayout()
        tab_layout.addLayout(page_buttons_layout)

        # Add stacked widget for pages
        stacked_widget = QtWidgets.QStackedWidget()
        tab_layout.addWidget(stacked_widget)

        # Store references to the pages and buttons
        page_buttons = {}

        # Add pages and buttons from the character data
        for page_data in character_data.get("pages", []):
            page_name = page_data.get("page", "Unnamed Page")

            # Create a new page
            new_page = PickerPage()
            stacked_widget.addWidget(new_page)

            # Add the page button and connect it
            new_button = QtWidgets.QPushButton(page_name)
            new_button.clicked.connect(lambda checked=False, page=new_page:self.switch_to_page(character_tab, page))
            page_buttons[page_name] = new_page
            page_buttons_layout.addWidget(new_button)

            # Populate the page with buttons
            for button_data in page_data.get("buttons", []):
                button_label = button_data.get("button", "Unnamed Button")
                grid_x = button_data.get("grid_x", 0)
                grid_y = button_data.get("grid_y", 0)
                width = button_data.get("width", 1)
                height = button_data.get("height", 1)

                button = GridButton(button_label, parent=new_page)
                button.setFixedSize(width * new_page.cell_width, height * new_page.cell_height)
                button.move(grid_x * new_page.cell_width, grid_y * new_page.cell_height)
                button.show()
                new_page.buttons.append((button, (grid_x, grid_y, width, height)))

        # Attach data to the tab
        character_tab.page_buttons = page_buttons
        character_tab.stacked_widget = stacked_widget

        # Add the tab to the tab widget
        self.tab_widget.addTab(character_tab, character_name)

    def save_character(self):
        """Save the currently selected character to a JSON file."""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            QtWidgets.QMessageBox.warning(self, "Warning", "No character tab selected.")
            return

        # Use tab name as the default file name
        tab_name = self.tab_widget.tabText(self.tab_widget.currentIndex())
        default_file_name = tab_name.replace(" ", "_") + ".json"

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Character", default_file_name, "JSON Files (*.json)"
        )
        if not file_path:
            return  # User canceled

        # Save character data
        character_data = {"character":tab_name, "pages":[]}

        # Iterate through the pages and their buttons
        for page_name, page in current_tab.page_buttons.items():
            if isinstance(page, PickerPage):  # Ensure this is a valid PickerPage
                page_data = {"page":page_name, "buttons":[]}

                # Collect button details
                for button, (grid_x, grid_y, width, height) in page.buttons:
                    button_data = {
                        "button":button.text(),
                        "grid_x":grid_x,
                        "grid_y":grid_y,
                        "width":width,
                        "height":height,
                    }
                    page_data["buttons"].append(button_data)

                character_data["pages"].append(page_data)

        try:
            # Write character data to JSON file
            with open(file_path, "w") as f:
                json.dump(character_data, f, indent=4)

            # Update the tab name to match the saved file name
            new_name = file_path.split("/")[-1].replace("_", " ").replace(".json", "")
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), new_name)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save character: {e}")

    def add_character_tab(self, character_name):
        """Add a new character tab with a stacked widget."""
        character_tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(character_tab)

        # Add page buttons layout
        page_buttons_layout = QtWidgets.QHBoxLayout()
        tab_layout.addLayout(page_buttons_layout)

        # Add stacked widget for pages
        stacked_widget = QtWidgets.QStackedWidget()
        tab_layout.addWidget(stacked_widget)

        # Create the default "Main" page
        main_page = PickerPage()
        stacked_widget.addWidget(main_page)

        # Create the button for the "Main" page and add it
        main_button = QtWidgets.QPushButton("Main")
        main_button.clicked.connect(lambda checked=False, page=main_page:self.switch_to_page(character_tab, page))
        page_buttons_layout.addWidget(main_button)

        # Store references to the pages and buttons
        character_tab.page_buttons = {"Main":main_page}
        character_tab.stacked_widget = stacked_widget
        self.tab_widget.addTab(character_tab, character_name)

    def switch_to_page(self, current_tab, page):
        """Switch to the specified page in the stacked widget."""
        page_index = current_tab.stacked_widget.indexOf(page)
        current_tab.stacked_widget.setCurrentIndex(page_index)

    def close_current_tab(self):
        """Close the currently selected tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.removeTab(current_index)

    def add_page_to_current(self):
        """Add a new page to the current character tab."""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            page_name, ok = QtWidgets.QInputDialog.getText(self, "New Page", "Enter page name:")
            if ok and page_name:
                new_page = PickerPage()
                current_tab.stacked_widget.addWidget(new_page)

                new_button = QtWidgets.QPushButton(page_name)
                new_button.clicked.connect(lambda checked=False, page=new_page:self.switch_to_page(current_tab, page))
                current_tab.page_buttons[page_name] = new_page  # Link to PickerPage
                current_tab.layout().itemAt(0).layout().addWidget(new_button)

    def add_button_to_current(self):
        """Add a button to the current page."""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            current_page = current_tab.stacked_widget.currentWidget()
            if hasattr(current_page, 'create_button'):
                position = QtCore.QPoint(100, 100)  # Default position
                current_page.create_button(position)
            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "The current page does not support adding buttons.")

    def show_about_dialog(self):
        """Show the About dialog."""
        QtWidgets.QMessageBox.about(self, "About", "Character Picker Tool\nVersion 1.0\nCreated for Maya Animators.")


def show_character_picker():
    """Display the Character Picker tool inside Maya."""
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, CharacterPicker):
            widget.close()

    picker = CharacterPicker(parent=maya_main_window())
    picker.setWindowFlags(QtCore.Qt.Window)
    picker.show()


# Show the tool
show_character_picker()
