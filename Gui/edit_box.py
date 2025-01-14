# edit_box.py
from PySide2 import QtWidgets, QtCore, QtGui
import CharacterPicker.Gui.custom_widgets as custom
import os
import importlib

importlib.reload(custom)


class EditBox(QtWidgets.QGroupBox):
    def __init__(self, icon_dir, main_window=None, tab_manager=None, context_menu=None):
        super().__init__(main_window)
        self.icon_dir = icon_dir
        self.main_window = main_window
        self.tab_manager = tab_manager  # Store a reference to the tab_manager
        self.context_menu = context_menu  # Pass the shared context menu
        self.currently_open_section = None  # Track which CollapsibleBox is open

        # Main layout for the content
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Add sections to the ToolBox
        self.character_settings = self.add_character_settings(layout)
        self.page_settings = self.add_page_settings(layout)
        self.picker_button_controls = self.add_picker_button_controls(layout)

        # Connect toggled signals
        self.character_settings.toggled.connect(self.handle_section_toggle)
        self.page_settings.toggled.connect(self.handle_section_toggle)
        self.picker_button_controls.toggled.connect(self.handle_section_toggle)

        self.setStyleSheet("""
            QGroupBox {
                border: 0px solid #2d2d2d;  /* Black border */
                border-radius: 0px;         /* Rounded corners (optional) */
                background-color: #373737;  /* Grey background (adjust if needed) */
                margin-top: 0px;           /* Space for the title */
            }
        """)

    def handle_section_toggle(self, is_open):
        sender = self.sender()  # The CollapsibleBox that just got toggled
        main_window = self.window()

        # If the user is opening this 'sender' subsection
        if is_open:
            new_height = sender.content_widget.sizeHint().height()
            if self.currently_open_section and self.currently_open_section != sender:
                old_height = self.currently_open_section.content_widget.sizeHint().height()
                self.currently_open_section.close_silently()  # no signal
            else:
                old_height = 0

            delta = new_height - old_height
            main_window.resize(main_window.width(), main_window.height() + delta)
            self.currently_open_section = sender

        else:
            # closing the section that *was* open
            if self.currently_open_section == sender:
                old_height = sender.content_widget.sizeHint().height()
                main_window.resize(main_window.width(), main_window.height() - old_height)
                self.currently_open_section = None

    def set_character_name_field(self, name):
        """Sets the character_name_input field to the given name."""
        self.character_name_input.setText(name or "")

    def set_page_name_field(self, name):
        """Sets the page_name_input field to the given name."""
        self.page_name_input.setText(name or "")

    def set_picker_label_field(self, label):
        """Sets the picker_label_input field to the given label."""
        self.picker_label_input.setText(label or "")

    def set_character_pic_button_enabled(self, enabled: bool):
        """Enable or disable the 'Set Character Picture' button."""
        self.character_pic_button.setEnabled(enabled)

    # ------------------------
    #  Character Settings
    # ------------------------
    def add_character_settings(self, parent_layout):
        """
        Creates a CollapsibleBox labeled "Character Settings" containing:
         - Row 1: A QLineEdit for character name, plus "Add New Character" and "Remove Current Character" buttons.
         - Row 2: "Add Page" and "Delete Page" buttons.
        """
        char_settings_box = custom.CollapsibleBox("Character Settings")
        parent_layout.addWidget(char_settings_box)

        # Main layout for everything inside this CollapsibleBox
        char_settings_layout = QtWidgets.QHBoxLayout()

        # Character Inputs
        character_inputs_layout = QtWidgets.QGridLayout()

        # Label for character pic file
        self.character_pic_label = QtWidgets.QLabel("Profile Picture:")
        self.character_pic_filename = QtWidgets.QLabel("None")

        # Input box for character name
        self.character_name_label = QtWidgets.QLabel("Character Name:")
        self.character_name_input = QtWidgets.QLineEdit()
        self.character_name_input.setPlaceholderText("Character Name")
        self.character_name_input.editingFinished.connect(self.update_character_name)

        # Button for adding character pic
        character_pic_size = QtCore.QSize(24, 24)  # Small square size for buttons
        self.character_pic_button = QtWidgets.QPushButton()
        self.character_pic_button.setIcon(QtGui.QIcon(":/file.svg"))  # Maya built-in icon
        self.character_pic_button.setFixedSize(character_pic_size)
        self.character_pic_button.setToolTip("Set Character Picture")
        self.character_pic_button.clicked.connect(self.set_character_pic)

        self.add_character_button = QtWidgets.QPushButton("Add Character")
        self.remove_character_button = QtWidgets.QPushButton("Delete Character")
        self.save_character_button = QtWidgets.QPushButton("Save Character")
        self.load_character_button = QtWidgets.QPushButton("Load Character")

        character_inputs_layout.addWidget(self.character_pic_label, 0, 0, alignment=QtCore.Qt.AlignRight)
        character_inputs_layout.addWidget(self.character_pic_filename, 0, 1)
        character_inputs_layout.addWidget(self.character_pic_button, 0, 2, 1, 2)
        character_inputs_layout.addWidget(self.character_name_label, 1, 0, alignment=QtCore.Qt.AlignRight)
        character_inputs_layout.addWidget(self.character_name_input, 1, 1)
        character_inputs_layout.addWidget(self.add_character_button, 1, 2)
        character_inputs_layout.addWidget(self.remove_character_button, 1, 3)
        character_inputs_layout.addWidget(self.save_character_button, 2, 0, 1, 2)
        character_inputs_layout.addWidget(self.load_character_button, 2, 2, 1, 2)

        # Set Fixed Width for Column 1
        character_inputs_layout.setColumnMinimumWidth(1, 200)

        # Set Column Stretch
        character_inputs_layout.setColumnStretch(0, 0)  # Column 1 stretches
        character_inputs_layout.setColumnStretch(1, 1)
        character_inputs_layout.setColumnStretch(2, 1)
        character_inputs_layout.setColumnStretch(3, 1)

        # Add a stretch before and after the form if desired
        char_settings_layout.addStretch()
        char_settings_layout.addLayout(character_inputs_layout)
        char_settings_layout.addStretch()

        # Set the CollapsibleBox content
        char_settings_box.setContentLayout(char_settings_layout)
        return char_settings_box

    def update_character_name(self):
        """User finished editing the character_name_input."""
        new_name = self.character_name_input.text().strip()
        if not new_name:
            # Decide what to do if empty is disallowed
            return
        current_index = self.tab_manager.currentIndex()
        if current_index >= 0:
            self.tab_manager.setTabText(current_index, new_name)

    def set_character_pic(self):
        """Set a new character picture."""
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Character Picture", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.svg)"
        )
        if image_path:
            self.character_pic_filename.setText(f"{os.path.basename(image_path)}")
            current_tab = self.tab_manager.currentWidget()
            if current_tab:
                current_tab.set_tab_icon(image_path)

    # ------------------------
    #  Page Settings
    # ------------------------
    def add_page_settings(self, parent_layout):
        """Adds the Page Settings section."""
        page_settings_box = custom.CollapsibleBox("Page Settings")
        parent_layout.addWidget(page_settings_box)

        # 1) Create a vertical layout that will hold everything
        page_settings_container = QtWidgets.QVBoxLayout()

        # 2) The "top row" layout remains an HBox, same as before
        top_row_layout = QtWidgets.QHBoxLayout()

        # Left side: Name, Background, and Scale Factor
        left_layout = QtWidgets.QFormLayout()

        # Page Name Input
        self.page_name_input = QtWidgets.QLineEdit()
        self.page_name_input.setPlaceholderText("Enter page name")
        self.page_name_input.editingFinished.connect(self.update_page_name)
        left_layout.addRow("Page Name:", self.page_name_input)

        # Current Background Label
        self.bg_label = QtWidgets.QLabel("None")
        left_layout.addRow("Background:", self.bg_label)

        # Scale Factor Slider
        self.bg_scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.bg_scale_slider.setRange(0, 100)
        self.bg_scale_slider.setValue(50)  # Default = 50 => 1.0 scale
        self.bg_scale_slider.valueChanged.connect(self.on_bg_scale_changed)
        left_layout.addRow("Scale Factor:", self.bg_scale_slider)

        # Add a stretch before and after the form if desired
        top_row_layout.addStretch()
        top_row_layout.addLayout(left_layout)

        # Right side: Nudge Background Controls
        nudge_layout = QtWidgets.QGridLayout()
        button_size = QtCore.QSize(24, 24)  # Small square size for buttons

        up_button = QtWidgets.QPushButton("↑")
        up_button.setFixedSize(button_size)
        up_button.clicked.connect(self.nudge_bg_up)
        nudge_layout.addWidget(up_button, 0, 1)

        left_button = QtWidgets.QPushButton("←")
        left_button.setFixedSize(button_size)
        left_button.clicked.connect(self.nudge_bg_left)
        nudge_layout.addWidget(left_button, 1, 0)

        self.browse_bg_button = QtWidgets.QPushButton()
        self.browse_bg_button.setIcon(QtGui.QIcon(":/file.svg"))  # Maya built-in icon
        self.browse_bg_button.setFixedSize(button_size)
        self.browse_bg_button.setToolTip("Set Background")
        self.browse_bg_button.clicked.connect(self.set_background_image)
        nudge_layout.addWidget(self.browse_bg_button, 1, 1)

        right_button = QtWidgets.QPushButton("→")
        right_button.setFixedSize(button_size)
        right_button.clicked.connect(self.nudge_bg_right)
        nudge_layout.addWidget(right_button, 1, 2)

        down_button = QtWidgets.QPushButton("↓")
        down_button.setFixedSize(button_size)
        down_button.clicked.connect(self.nudge_bg_down)
        nudge_layout.addWidget(down_button, 2, 1)

        # Add the nudge_layout as part of the top_row_layout if desired
        top_row_layout.addLayout(nudge_layout)
        # Possibly another stretch at the end
        top_row_layout.addStretch()

        # 3) Add the top row (HBox) to the container (VBox)
        page_settings_container.addLayout(top_row_layout)

        # 4) Now create a new horizontal layout for the two new buttons
        bottom_button_layout = QtWidgets.QHBoxLayout()
        self.add_page_button = QtWidgets.QPushButton("Add Page")
        bottom_button_layout.addWidget(self.add_page_button)

        self.remove_page_button = QtWidgets.QPushButton("Delete Page")
        bottom_button_layout.addWidget(self.remove_page_button)

        # Make them stretch across the box if you like:
        # bottom_button_layout.setStretch(0, 1)
        # bottom_button_layout.setStretch(1, 1)

        # Add that horizontal layout to our vertical container
        page_settings_container.addLayout(bottom_button_layout)

        # 5) Finally, assign this vertical container as the content of the CollapsibleBox
        page_settings_box.setContentLayout(page_settings_container)
        return page_settings_box

    def update_page_name(self):
        """User finished editing the page_name_input."""
        new_name = self.page_name_input.text().strip()
        if not new_name:
            return
        current_tab = self.tab_manager.currentWidget()
        if current_tab and hasattr(current_tab, "stacked_widget"):
            current_page = current_tab.stacked_widget.currentWidget()

            # 1) Update the page object's "page_name"
            if hasattr(current_page, "page_name"):
                current_page.page_name = new_name

            # 2) Find the button referencing this page and rename it
            if hasattr(current_tab, "page_buttons"):
                for page_button, page_obj in current_tab.page_buttons.items():
                    if page_obj == current_page:
                        page_button.setText(new_name)
                        break

    def on_bg_scale_changed(self, value):
        """Update the background scale factor based on the slider value."""
        current_tab = self.tab_manager.currentWidget()
        if current_tab:
            current_page = current_tab.stacked_widget.currentWidget()
            if hasattr(current_page, "set_bg_scale"):
                current_page.set_bg_scale(value)

    def set_background_image(self, image_path=None):
        """
        Delegate setting the background to CharacterPicker.
        """
        self.tab_manager.set_current_page_background(image_path)

    def nudge_bg_left(self):
        current_tab = self.tab_manager.currentWidget()
        if current_tab:
            current_tab.stacked_widget.currentWidget().nudge_bg_left()

    def nudge_bg_right(self):
        current_tab = self.tab_manager.currentWidget()
        if current_tab:
            current_tab.stacked_widget.currentWidget().nudge_bg_right()

    def nudge_bg_up(self):
        current_tab = self.tab_manager.currentWidget()
        if current_tab:
            current_tab.stacked_widget.currentWidget().nudge_bg_up()

    def nudge_bg_down(self):
        current_tab = self.tab_manager.currentWidget()
        if current_tab:
            current_tab.stacked_widget.currentWidget().nudge_bg_down()

    # ------------------------
    #  Picker Button Section
    # ------------------------
    def add_picker_button_controls(self, parent_layout):
        """Adds the Picker Button section using CollapsibleBox."""
        picker_box = custom.CollapsibleBox("Picker Button")
        parent_layout.addWidget(picker_box)

        picker_layout = QtWidgets.QFormLayout()

        # Label Input
        self.picker_label_input = QtWidgets.QLineEdit()
        self.picker_label_input.editingFinished.connect(self.update_picker_button_name)
        picker_layout.addRow("Label:", self.picker_label_input)

        # Grid Position
        grid_pos_layout = QtWidgets.QHBoxLayout()
        self.picker_grid_x = QtWidgets.QSpinBox()
        self.picker_grid_x.setRange(-9999, 9999)
        self.picker_grid_x.setValue(0)
        grid_pos_layout.addWidget(self.picker_grid_x)

        self.picker_grid_y = QtWidgets.QSpinBox()
        self.picker_grid_y.setRange(-9999, 9999)
        self.picker_grid_y.setValue(0)
        grid_pos_layout.addWidget(self.picker_grid_y)
        picker_layout.addRow("Grid Pos (x, y):", grid_pos_layout)

        # Size Controls
        size_layout = QtWidgets.QHBoxLayout()
        self.picker_width = QtWidgets.QSpinBox()
        self.picker_width.setRange(1, 50)
        size_layout.addWidget(self.picker_width)

        self.picker_height = QtWidgets.QSpinBox()
        self.picker_height.setRange(1, 50)
        size_layout.addWidget(self.picker_height)
        picker_layout.addRow("Size (w, h):", size_layout)

        # Shape Selection
        self.shape_combo_box = QtWidgets.QComboBox()
        self.shape_combo_box.addItems(["rectangle", "circle", "triangle"])
        picker_layout.addRow("Shape:", self.shape_combo_box)

        # Color Picker
        self.color_button = QtWidgets.QPushButton()
        self.color_button.setText("Select Color")
        self.color_button.clicked.connect(self.open_color_dialog)
        self.selected_color = "#A6A6A6"  # Default color
        self.color_button.setStyleSheet(f"background-color: {self.selected_color}")
        picker_layout.addRow("Color:", self.color_button)

        # Command Mode
        self.command_mode_combo_box = QtWidgets.QComboBox()
        self.command_mode_combo_box.addItems(["none", "python", "select"])
        picker_layout.addRow("Command Mode:", self.command_mode_combo_box)

        # Command String
        self.command_text_edit = QtWidgets.QPlainTextEdit()
        self.command_text_edit.setPlaceholderText("Enter Python code or object names (comma-separated)")
        picker_layout.addRow("Command:", self.command_text_edit)

        # Add and Delete Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.picker_submit_button = QtWidgets.QPushButton("Add")
        self.picker_submit_button.clicked.connect(self.handle_submit_clicked)
        button_layout.addWidget(self.picker_submit_button)

        self.picker_delete_button = QtWidgets.QPushButton("Delete")
        self.picker_delete_button.clicked.connect(self.handle_delete_clicked)
        button_layout.addWidget(self.picker_delete_button)
        picker_layout.addRow(button_layout)

        picker_box.setContentLayout(picker_layout)
        return picker_box

    def update_picker_button_name(self):
        """User finished editing the picker_label_input."""
        new_label = self.picker_label_input.text().strip()
        if not new_label:
            return
        # You need a reference to the *currently selected* picker button
        # Typically, your main_window or tab_manager has something like self.selected_picker_button
        main_window = self.window()
        if hasattr(main_window, "selected_picker_button") and main_window.selected_picker_button:
            main_window.selected_picker_button.setText(new_label)

    # ------------------------
    #  Picker Button Logic
    # ------------------------
    def open_color_dialog(self):
        """Open a color dialog to select a color."""
        color = QtWidgets.QColorDialog.getColor(initial=QtGui.QColor(self.selected_color), parent=self, title="Select Button Color")
        if color.isValid():
            self.selected_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}")

    def get_default_picker_data(self):
        return {
            "label": " ",
            "grid_pos": (0, 0),
            "size_in_cells": (1, 1),
            "shape": "rectangle",
            "color": "#A6A6A6",
            "command_mode": "select",
            "command_string": ""
        }
    
    def handle_submit_clicked(self):
        """
        Called when the user clicks the 'Submit' button in the Picker Button section.
        Gathers form data into a dict, calls main_window.submit_picker.
        """
        data_dict = self.get_default_picker_data()

        label = self.picker_label_input.text()
        data_dict["label"] = label

        gx = int(self.picker_grid_x.value())
        gy = int(self.picker_grid_y.value())
        data_dict["grid_pos"] = (gx, gy)

        w = int(self.picker_width.value())
        h = int(self.picker_height.value())
        data_dict["size_in_cells"] = (w, h)

        # Shape Selection
        shape = self.shape_combo_box.currentText()
        data_dict["shape"] = shape

        # Color Selection
        data_dict["color"] = self.selected_color

        # Command Mode and String
        command_mode = self.command_mode_combo_box.currentText()
        data_dict["command_mode"] = command_mode

        command_string = self.command_text_edit.toPlainText().strip()
        data_dict["command_string"] = command_string

        self.main_window.submit_picker(data_dict)

    def handle_delete_clicked(self):
        """Handle Delete button clicks."""
        # Emit a signal to delete the selected picker button
        self.main_window.delete_selected_picker_button()

    def update_picker_button_fields(self, picker_button):
        """
        Update the EditBox fields based on the selected picker button or defaults.

        :param picker_button: The PickerButton instance or None.
        """
        if picker_button is None:
            # Populate with default values
            data = self.get_default_picker_data()

            self.picker_label_input.setText(data["label"])
            self.picker_grid_x.setValue(data["grid_pos"][0])
            self.picker_grid_y.setValue(data["grid_pos"][1])
            self.picker_width.setValue(data["size_in_cells"][0])
            self.picker_height.setValue(data["size_in_cells"][1])

            # Shape
            index = self.shape_combo_box.findText(data["shape"])
            if index != -1:
                self.shape_combo_box.setCurrentIndex(index)

            # Color
            self.selected_color = data["color"]
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}")

            # Command Mode
            index = self.command_mode_combo_box.findText(data["command_mode"])
            if index != -1:
                self.command_mode_combo_box.setCurrentIndex(index)

            # Command String
            self.command_text_edit.setPlainText(data["command_string"])

            # Update buttons
            self.picker_submit_button.setText("Add")
            self.picker_delete_button.setEnabled(False)
        else:
            # Populate with picker_button's data
            data = picker_button.data_dict

            self.picker_label_input.setText(data["label"])
            self.picker_grid_x.setValue(data["grid_pos"][0])
            self.picker_grid_y.setValue(data["grid_pos"][1])
            self.picker_width.setValue(data["size_in_cells"][0])
            self.picker_height.setValue(data["size_in_cells"][1])

            # Shape
            index = self.shape_combo_box.findText(data["shape"])
            if index != -1:
                self.shape_combo_box.setCurrentIndex(index)

            # Color
            self.selected_color = data["color"]
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}")

            # Command Mode
            index = self.command_mode_combo_box.findText(data["command_mode"])
            if index != -1:
                self.command_mode_combo_box.setCurrentIndex(index)

            # Command String
            self.command_text_edit.setPlainText(data["command_string"])

            # Update buttons
            self.picker_submit_button.setText("Update")
            self.picker_delete_button.setEnabled(True)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            # Show the context menu for the page button area
            self.context_menu.set_context_type('tool_box')
            self.context_menu.exec_(event.globalPos())
        else:
            super().mousePressEvent(event)