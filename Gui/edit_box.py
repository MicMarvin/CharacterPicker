# edit_box.py
from PySide2 import QtWidgets, QtCore, QtGui
import CharacterPicker.Gui.custom_widgets as custom
import os
import importlib

importlib.reload(custom)


class EditBox(QtWidgets.QGroupBox):
    picker_added = QtCore.Signal(dict)  # {'label', 'grid_pos', 'size_in_cells'}
    picker_updated = QtCore.Signal(dict)  # {'label', 'grid_pos', 'size_in_cells'}
    add_button_signal = QtCore.Signal()  # No additional data

    def __init__(self, icon_dir, parent=None):
        super(EditBox, self).__init__("Edit Mode", parent)
        self.icon_dir = icon_dir
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        # Page Settings Section
        self.add_page_settings(layout)

        # Picker Button Section
        self.add_picker_button_controls(layout)

        # Buttons for adding/removing characters at the bottom
        self.add_character_controls(layout)

        # Buttons for adding/removing pages at the bottom
        self.add_page_controls(layout)

        # Toggle for Edit/Animate Mode
        self.add_mode_toggle(layout)

    def add_page_settings(self, parent_layout):
        """Adds the Page Settings section."""
        page_settings_box = custom.CollapsibleBox("Page Settings")
        parent_layout.addWidget(page_settings_box)

        # Create a horizontal layout to organize fields and controls
        page_settings_layout = QtWidgets.QHBoxLayout()

        # Add stretch between left and right sections
        page_settings_layout.addStretch()

        # Left side: Name, Background, and Scale Factor
        left_layout = QtWidgets.QFormLayout()

        # Page Name Input
        self.page_name_input = QtWidgets.QLineEdit()
        self.page_name_input.setPlaceholderText("Enter page name")
        self.page_name_input.textChanged.connect(self.update_page_name)
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

        page_settings_layout.addLayout(left_layout)

        # Add stretch between left and right sections
        page_settings_layout.addStretch()

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

        page_settings_layout.addLayout(nudge_layout)

        # Add stretch between left and right sections
        page_settings_layout.addStretch()

        page_settings_box.setContentLayout(page_settings_layout)

    def add_picker_button_controls(self, parent_layout):
        """Adds the Picker Button section using CollapsibleBox."""
        picker_box = custom.CollapsibleBox("Picker Button")
        parent_layout.addWidget(picker_box)

        picker_layout = QtWidgets.QFormLayout()

        # Label Input
        self.picker_label_input = QtWidgets.QLineEdit()
        picker_layout.addRow("Label:", self.picker_label_input)

        # Grid Position
        grid_pos_layout = QtWidgets.QHBoxLayout()
        self.picker_grid_x = QtWidgets.QDoubleSpinBox()
        self.picker_grid_x.setRange(-9999, 9999)
        self.picker_grid_x.setValue(0)
        grid_pos_layout.addWidget(self.picker_grid_x)

        self.picker_grid_y = QtWidgets.QDoubleSpinBox()
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

        # Add and Delete Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.picker_submit_button = QtWidgets.QPushButton("Add")
        button_layout.addWidget(self.picker_submit_button)

        self.picker_delete_button = QtWidgets.QPushButton("Delete")
        button_layout.addWidget(self.picker_delete_button)
        picker_layout.addRow(button_layout)

        picker_box.setContentLayout(picker_layout)

    def add_character_controls(self, parent_layout):
        """Adds controls for adding/removing characters."""
        button_layout = QtWidgets.QHBoxLayout()

        self.add_character_button = QtWidgets.QPushButton("Add New Character")
        button_layout.addWidget(self.add_character_button)

        self.remove_character_button = QtWidgets.QPushButton("Remove Current Character")
        button_layout.addWidget(self.remove_character_button)

        parent_layout.addLayout(button_layout)

    def add_page_controls(self, parent_layout):
        """Adds controls for adding/removing pages."""
        button_layout = QtWidgets.QHBoxLayout()

        self.add_page_button = QtWidgets.QPushButton("Add Page")
        button_layout.addWidget(self.add_page_button)

        self.remove_page_button = QtWidgets.QPushButton("Delete Page")
        button_layout.addWidget(self.remove_page_button)

        parent_layout.addLayout(button_layout)

    def on_bg_scale_changed(self, value):
        """Update the background scale factor based on the slider value."""
        current_tab = self.parent().tab_manager.currentWidget()
        if current_tab:
            current_page = current_tab.stacked_widget.currentWidget()
            if hasattr(current_page, "set_bg_scale"):
                current_page.set_bg_scale(value)

    def set_background_image(self):
        """Set a new background image."""
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Background Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.svg)"
        )
        if image_path:
            self.bg_label.setText(f"{os.path.basename(image_path)}")
            self.parent().tab_manager.currentWidget().stacked_widget.currentWidget().set_background_image(image_path)

    def nudge_bg_left(self):
        self.parent().tab_manager.currentWidget().stacked_widget.currentWidget().nudge_bg_left()

    def nudge_bg_right(self):
        self.parent().tab_manager.currentWidget().stacked_widget.currentWidget().nudge_bg_right()

    def nudge_bg_up(self):
        self.parent().tab_manager.currentWidget().stacked_widget.currentWidget().nudge_bg_up()

    def nudge_bg_down(self):
        self.parent().tab_manager.currentWidget().stacked_widget.currentWidget().nudge_bg_down()

    def update_page_name(self, name):
        """Update the page name."""
        current_tab = self.parent().tab_manager.currentWidget()
        if current_tab:
            current_tab.stacked_widget.currentWidget().page_name = name

    def add_mode_toggle(self, parent_layout):
        """Adds a toggle button to switch between Edit and Animate Modes."""
        self.mode_toggle_btn = QtWidgets.QPushButton("Switch to Animate Mode")
        self.mode_toggle_btn.setCheckable(True)
        parent_layout.addWidget(self.mode_toggle_btn)

    def emit_add_button_signal(self):
        """Emit the add_button_signal to add a button to the current sub-page."""
        self.add_button_signal.emit()

    def submit_picker(self):
        """Handle Add or Update button clicks."""
        label = self.picker_label_input.text()
        gx = self.picker_grid_x.value()
        gy = self.picker_grid_y.value()
        w = self.picker_width.value()
        h = self.picker_height.value()

        if self.picker_submit_button.text() == "Add":
            # Emit a signal to add a new picker button
            self.picker_added.emit({
                "label":label,
                "grid_pos":(int(gx), int(gy)),
                "size_in_cells":(w, h)
            })
        elif self.picker_submit_button.text() == "Update":
            # Emit a signal to update the selected picker button
            self.picker_updated.emit({
                "label":label,
                "grid_pos":(int(gx), int(gy)),
                "size_in_cells":(w, h)
            })

    def delete_picker(self):
        """Handle Delete button clicks."""
        # Emit a signal to delete the selected picker button
        self.parent().delete_selected_picker_button()

    def set_selected_picker_button(self, picker_button):
        """Update the EditBox fields based on the selected picker button."""
        if picker_button is None:
            # Deselect: clear fields and reset UI
            self.picker_label_input.setText("")
            self.picker_grid_x.setValue(0)
            self.picker_grid_y.setValue(0)
            self.picker_width.setValue(1)
            self.picker_height.setValue(1)

            self.picker_submit_button.setText("Add")
            self.picker_delete_button.setEnabled(False)
        else:
            # Select: populate fields with button's data
            self.picker_label_input.setText(picker_button.text())
            self.picker_grid_x.setValue(picker_button.grid_x)
            self.picker_grid_y.setValue(picker_button.grid_y)
            self.picker_width.setValue(picker_button.width_in_cells)
            self.picker_height.setValue(picker_button.height_in_cells)

            self.picker_submit_button.setText("Update")
            self.picker_delete_button.setEnabled(True)
