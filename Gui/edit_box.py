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
        self.last_command_mode = "Python"  # Set default to avoid initial undefined behavior

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
    #  Mouse Events
    # ------------------------
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            # Show the context menu for the page button area
            self.context_menu.set_context_type('tool_box')
            self.context_menu.exec_(event.globalPos())
        else:
            super().mousePressEvent(event)

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
        """Adds the Picker Button section using a compact grid layout."""
        picker_box = custom.CollapsibleBox("Picker Button")
        parent_layout.addWidget(picker_box)

        picker_layout = QtWidgets.QGridLayout()  # Grid layout for compact arrangement

        # ---------- First Row: Form Layouts ----------

        # Left-side form layout: Label, Shape, Direction, Color
        left_form_layout = QtWidgets.QFormLayout()

        self.picker_label_input = QtWidgets.QLineEdit()
        self.picker_label_input.editingFinished.connect(self.update_picker_button_name)
        left_form_layout.addRow("Label:", self.picker_label_input)

        self.shape_combo_box = QtWidgets.QComboBox()
        self.shape_combo_box.addItems(["rectangle", "circle", "triangle"])
        left_form_layout.addRow("Shape:", self.shape_combo_box)

        color_opacity_layout = QtWidgets.QHBoxLayout()
        self.color_button = QtWidgets.QPushButton(" ")
        self.color_button.setFixedSize(25, 25)  # Fixed square size
        self.color_button.clicked.connect(self.open_color_dialog)
        
        # Get the default color and apply it
        default_color = self.get_default_picker_data()["color"]
        self.selected_color = default_color.name()  # Store default color

        # Set the color using QPalette instead of stylesheet
        palette = self.color_button.palette()
        palette.setColor(QtGui.QPalette.Button, default_color)
        self.color_button.setAutoFillBackground(True)
        self.color_button.setPalette(palette)
        self.color_button.update()

        color_opacity_layout.addWidget(self.color_button)

        default_opacity = self.get_default_picker_data()["opacity"]
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacity_slider.setRange(1, 10)
        self.opacity_slider.setSingleStep(1)
        self.opacity_slider.setValue(default_opacity)  # Use default from data_dict
        self.opacity_slider.valueChanged.connect(self.update_picker_opacity)
        color_opacity_layout.addWidget(self.opacity_slider)

        left_form_layout.addRow("Color:", color_opacity_layout)

        self.direction_dial = QtWidgets.QDial()
        self.direction_dial.setRange(0, 360)
        self.direction_dial.setNotchesVisible(True)
        self.direction_dial.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        left_form_layout.addRow("Orient:", self.direction_dial)

        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_form_layout)
        left_widget.setMinimumWidth(125)  # Set minimum width

        picker_layout.addWidget(left_widget, 0, 0)

        # Middle Spacer (to create separation)
        picker_layout.addItem(QtWidgets.QSpacerItem(5, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum), 0, 1)

        # Right-side form layout: Grid Pos, Size, Opacity, Mode, Command
        right_form_layout = QtWidgets.QFormLayout()

        grid_pos_layout = QtWidgets.QHBoxLayout()
        self.picker_grid_x = QtWidgets.QSpinBox()
        self.picker_grid_x.setRange(-9999, 9999)
        grid_pos_layout.addWidget(QtWidgets.QLabel(" (x)"))
        grid_pos_layout.addWidget(self.picker_grid_x)

        self.picker_grid_y = QtWidgets.QSpinBox()
        self.picker_grid_y.setRange(-9999, 9999)
        grid_pos_layout.addWidget(QtWidgets.QLabel("(y)"))
        grid_pos_layout.addWidget(self.picker_grid_y)
        right_form_layout.addRow("Grid:", grid_pos_layout)

        size_layout = QtWidgets.QHBoxLayout()
        self.picker_width = QtWidgets.QSpinBox()
        self.picker_width.setRange(1, 50)
        size_layout.addWidget(QtWidgets.QLabel(" width"))
        size_layout.addWidget(self.picker_width)

        self.picker_height = QtWidgets.QSpinBox()
        self.picker_height.setRange(1, 50)
        size_layout.addWidget(QtWidgets.QLabel("height"))
        size_layout.addWidget(self.picker_height)
        right_form_layout.addRow("Size:", size_layout)

        # Command Text Edit
        self.command_text_edit = QtWidgets.QPlainTextEdit()
        self.command_text_edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        right_form_layout.addRow("Exec:", self.command_text_edit)

        # Create radio buttons
        self.radio_python = QtWidgets.QRadioButton("Python")
        self.radio_mel = QtWidgets.QRadioButton("MEL")
        self.radio_select = QtWidgets.QRadioButton("Select")

        # Connect the toggled signals to the on_command_mode_changed method
        self.radio_python.toggled.connect(self.on_command_mode_changed)
        self.radio_mel.toggled.connect(self.on_command_mode_changed)
        self.radio_select.toggled.connect(self.on_command_mode_changed)

        # Group the radio buttons (optional for mutual exclusivity)
        self.command_mode_group = QtWidgets.QButtonGroup()
        self.command_mode_group.addButton(self.radio_python)
        self.command_mode_group.addButton(self.radio_mel)
        self.command_mode_group.addButton(self.radio_select)

        # Set default selection
        self.radio_python.setChecked(True)

        command_mode_layout = QtWidgets.QHBoxLayout()
        command_mode_layout.addWidget(self.radio_python)
        command_mode_layout.addWidget(self.radio_mel)
        command_mode_layout.addWidget(self.radio_select)
        right_form_layout.addRow("Mode:", command_mode_layout)

        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(right_form_layout)
        right_widget.setMinimumWidth(275)  # Set minimum width

        picker_layout.addWidget(right_widget, 0, 2)

        # ---------- Second Row: Buttons ----------

        button_layout = QtWidgets.QHBoxLayout()

        self.picker_submit_button = QtWidgets.QPushButton("Add/Update")
        self.picker_submit_button.clicked.connect(self.handle_submit_clicked)
        button_layout.addWidget(self.picker_submit_button)

        self.picker_delete_button = QtWidgets.QPushButton("Delete")
        self.picker_delete_button.clicked.connect(self.handle_delete_clicked)
        button_layout.addWidget(self.picker_delete_button)

        picker_layout.addLayout(button_layout, 1, 0, 1, 3)  # Span across three columns

        # Column stretch settings for better resizing behavior
        picker_layout.setColumnStretch(0, 3)
        picker_layout.setColumnStretch(1, 1)
        picker_layout.setColumnStretch(2, 4)

        picker_box.setContentLayout(picker_layout)
        return picker_box

    # ------------------------
    #  Picker Button Logic
    # ------------------------
    def get_default_picker_data(self, mode=None):
        if mode == "Python":
            default_command_string = (
                "QtWidgets.QMessageBox.information(sys.modules['character_picker_main_window'], 'Default Python Code', 'Hooray, it works!\\n\\nThe picker button ran this code.')"
            )
        elif mode == "MEL":
            default_command_string = (
                "confirmDialog -title \"Default MEL Code\" "
                "-message \"Hooray, it works!\\n\\nThe picker button ran this code.\" "
                "-button \"OK\" "
                "-parent $pickerWindow;"
            )
        elif mode == "Select":
            default_command_string = "Enter a comma separated list of controls to select."
        else:
            default_command_string = ""

        return {
            "label": " ",
            "grid_pos": (0, 0),
            "size_in_cells": (1, 1),
            "shape": "rectangle",
            "color": QtGui.QColor("#f9aa26"),
            "command_mode": mode,
            "command_string": default_command_string,
            "opacity": 9
        }
    
    def handle_submit_clicked(self, external_grid_pos=None):
        """
        Called when the user clicks the 'Submit' button in the Picker Button section
        OR when handle_menu_add_button() in the main_window passes an external grid position.
        Gathers form data into a dict, then calls main_window.submit_picker.
        """
        if self.radio_python.isChecked():
            command_mode = "Python"
        elif self.radio_mel.isChecked():
            command_mode = "MEL"
        elif self.radio_select.isChecked():
            command_mode = "Select"
        else:
            command_mode = None  # Handle unexpected case if needed

        data_dict = self.get_default_picker_data(mode=command_mode)
        
        # Label
        label = self.picker_label_input.text()
        data_dict["label"] = label

        # Grid Position (from spinboxes)
        gx = int(self.picker_grid_x.value())
        gy = int(self.picker_grid_y.value())
        data_dict["grid_pos"] = (gx, gy)

        # Size
        w = int(self.picker_width.value())
        h = int(self.picker_height.value())
        data_dict["size_in_cells"] = (w, h)

        # Shape
        shape = self.shape_combo_box.currentText()
        data_dict["shape"] = shape

        # Color
        data_dict["color"] = self.selected_color

        # Command Mode
        if self.radio_python.isChecked():
            command_mode = "Python"
        elif self.radio_mel.isChecked():
            command_mode = "MEL"
        elif self.radio_select.isChecked():
            command_mode = "Select"
        else:
            command_mode = None  # Handle unexpected case if needed

        data_dict["command_mode"] = command_mode

        # Command String
        command_string = self.command_text_edit.toPlainText().strip()
        data_dict["command_string"] = command_string

        # -----------------------------------------
        # OVERRIDE GRID POSITION IF PROVIDED EXTERNALLY
        # -----------------------------------------
        # --- Now do a robust check before overriding ---
        if isinstance(external_grid_pos, tuple):
            # external_grid_pos is a valid (gx, gy) coordinate
            data_dict["grid_pos"] = external_grid_pos
        else:
            if external_grid_pos is not None:
                # Print a warning if external_grid_pos is something other than None or tuple
                print(f"[WARNING] external_grid_pos is not a tuple (type: {type(external_grid_pos)}) => ignoring override")

        # Submit
        self.main_window.submit_picker(data_dict)

    def handle_delete_clicked(self):
        """Handle Delete button clicks."""
        # Emit a signal to delete the selected picker button
        self.main_window.delete_selected_picker_button

    def on_command_mode_changed(self, checked):
        """
        Update command text as soon as a radio button is toggled ON.
        If 'checked' is False, the radio is being turned OFF, so ignore it.
        """
        if not checked:
            return  # We only do work when a button is turned ON

        # Identify which radio triggered the signal
        button = self.sender()

        if button == self.radio_python:
            new_mode = "Python"
        elif button == self.radio_mel:
            new_mode = "MEL"
        elif button == self.radio_select:
            new_mode = "Select"
        else:
            return

        # 1) Retrieve old snippet
        old_data = self.get_default_picker_data(mode=self.last_command_mode)
        old_snippet = old_data["command_string"]

        # 2) Check what is currently in the text edit
        existing_text = self.command_text_edit.toPlainText().strip()

        # 3) If user hasn't typed anything new, set the default snippet
        if not existing_text or existing_text == old_snippet:
            new_data = self.get_default_picker_data(mode=new_mode)
            new_snippet = new_data["command_string"]
            self.command_text_edit.setPlainText(new_snippet)

        # 4) Update last_command_mode
        self.last_command_mode = new_mode

    def update_picker_button_fields(self, picker_button):
        """
        Update the EditBox fields based on the selected picker button or defaults.

        :param picker_button: The PickerButton instance or None.
        """
        if picker_button is None:
            # Populate with default values
            if self.radio_python.isChecked():
                command_mode = "Python"
            elif self.radio_mel.isChecked():
                command_mode = "MEL"
            elif self.radio_select.isChecked():
                command_mode = "Select"
            else:
                command_mode = None  # Handle unexpected case if needed

            data = self.get_default_picker_data(mode=command_mode)

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
            if data["command_mode"] == "Python":
                self.radio_python.setChecked(True)
            elif data["command_mode"] == "MEL":
                self.radio_mel.setChecked(True)
            elif data["command_mode"] == "Select":
                self.radio_select.setChecked(True)

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
            if data["command_mode"] == "Python":
                self.radio_python.setChecked(True)
            elif data["command_mode"] == "MEL":
                self.radio_mel.setChecked(True)
            elif data["command_mode"] == "Select":
                self.radio_select.setChecked(True)

            # Command String
            self.command_text_edit.setPlainText(data["command_string"])

            # Update buttons
            self.picker_submit_button.setText("Update")
            self.picker_delete_button.setEnabled(True)

    # ------------------------
    #  Picker Button Helpers
    # ------------------------
    def open_color_dialog(self):
        """Open a color dialog to select a color."""
        color = QtWidgets.QColorDialog.getColor(initial=QtGui.QColor(self.selected_color), parent=self, title="Select Button Color")
        if color.isValid():
            self.selected_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}")

    def update_picker_opacity(self):
        """Update opacity of the selected picker button based on the slider value."""
        opacity_value = self.opacity_slider.value()  # Gets values from 1-10

        main_window = self.window()
        if hasattr(main_window, "selected_picker_buttons") and main_window.selected_picker_buttons:
            for btn in main_window.selected_picker_buttons:
                btn.opacity = opacity_value  # Store raw slider value (1-10)
                btn.set_color(btn.color)  # Apply the mapped opacity inside set_color
                btn.data_dict["opacity"] = opacity_value  # Store raw value in data_dict

    def update_picker_button_name(self):
        """User finished editing the picker_label_input."""
        new_label = self.picker_label_input.text().strip()
        if not new_label:
            return
        # You need a reference to the *currently selected* picker button
        # Typically, your main_window or tab_manager has something like self.selected_picker_button
        main_window = self.window()
        if hasattr(main_window, "selected_picker_buttons") and main_window.selected_picker_buttons:
            btn = main_window.selected_picker_buttons[0]
            btn.setText(new_label)
