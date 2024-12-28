import sys
from PySide2 import QtCore, QtWidgets, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

import CharacterPicker.SRC.grid_widget as grid
import CharacterPicker.SRC.picker as picker
import CharacterPicker.Gui.custom_widgets as custom
import importlib
importlib.reload(picker)
importlib.reload(grid)


def maya_main_window():
    """Return Maya's main window widget (in Maya)."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class CharacterPicker(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CharacterPicker, self).__init__(parent or maya_main_window())
        self.setWindowTitle("Character Picker")
        self.resize(659, 1210)
        self.setMinimumSize(400, 800)  # Set a minimum size to avoid UI breaking

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # 1) The GridWidget
        self.grid_widget = grid.GridWidget(rows=200, cols=200)
        main_layout.addWidget(self.grid_widget, 1)

        # 2) The editBox at the bottom
        self.edit_box = QtWidgets.QGroupBox("Edit Settings")
        self.edit_box.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)

        main_layout.addWidget(self.edit_box, 0)

        edit_layout = QtWidgets.QVBoxLayout(self.edit_box)

        # main.py (partial, inside your CharacterPicker's __init__ after you create editBox)

        # STEP 1: Create a new group or frame for "Picker Button" fields
        picker_box = QtWidgets.QGroupBox("Picker Button")
        edit_layout.addWidget(picker_box)  # add to the same layout as your existing rows

        picker_form = QtWidgets.QFormLayout(picker_box)

        # 1) Label field
        self.picker_label_input = QtWidgets.QLineEdit()
        picker_form.addRow("Label:", self.picker_label_input)

        # 2) Grid X, Grid Y
        grid_pos_layout = QtWidgets.QHBoxLayout()
        self.picker_grid_x = QtWidgets.QSpinBox()
        self.picker_grid_x.setRange(-9999, 9999)  # some range you like
        self.picker_grid_x.setValue(0)  # default
        grid_pos_layout.addWidget(self.picker_grid_x)

        self.picker_grid_y = QtWidgets.QSpinBox()
        self.picker_grid_y.setRange(-9999, 9999)
        self.picker_grid_y.setValue(0)
        grid_pos_layout.addWidget(self.picker_grid_y)

        picker_form.addRow("Grid Pos (x, y):", grid_pos_layout)

        # 3) Width, Height
        size_layout = QtWidgets.QHBoxLayout()
        self.picker_width = QtWidgets.QSpinBox()
        self.picker_width.setRange(1, 50)
        self.picker_width.setValue(1)
        size_layout.addWidget(self.picker_width)

        self.picker_height = QtWidgets.QSpinBox()
        self.picker_height.setRange(1, 50)
        self.picker_height.setValue(1)
        size_layout.addWidget(self.picker_height)

        picker_form.addRow("Size (w, h):", size_layout)

        # 4) Parent Grid (read-only label)
        self.picker_parent_grid_label = QtWidgets.QLabel("(none)")
        picker_form.addRow("Parent Grid:", self.picker_parent_grid_label)

        # 5) Buttons for Add/Update and Delete
        btn_layout = QtWidgets.QHBoxLayout()
        self.picker_submit_btn = QtWidgets.QPushButton("Add")  # by default in "Add" mode
        self.picker_submit_btn.clicked.connect(self.on_picker_submit_clicked)
        btn_layout.addWidget(self.picker_submit_btn)

        self.picker_delete_btn = QtWidgets.QPushButton("Delete")
        self.picker_delete_btn.clicked.connect(self.on_picker_delete_clicked)
        self.picker_delete_btn.setEnabled(False)  # disabled unless a button is selected
        btn_layout.addWidget(self.picker_delete_btn)

        picker_form.addRow("", btn_layout)

        # Row 1: background controls
        bg_controls_layout = QtWidgets.QHBoxLayout()
        edit_layout.addLayout(bg_controls_layout)

        load_bg_btn = QtWidgets.QPushButton("Load Background")
        load_bg_btn.clicked.connect(self.on_load_background_clicked)
        bg_controls_layout.addWidget(load_bg_btn)

        # Nudge background by 1 cell each direction
        arrow_layout = QtWidgets.QGridLayout()
        bg_controls_layout.addLayout(arrow_layout)

        # Up arrow
        up_btn = QtWidgets.QPushButton("↑")
        up_btn.clicked.connect(self.nudge_bg_up)
        arrow_layout.addWidget(up_btn, 0, 1)

        # Left arrow
        left_btn = QtWidgets.QPushButton("←")
        left_btn.clicked.connect(self.nudge_bg_left)
        arrow_layout.addWidget(left_btn, 1, 0)

        # Right arrow
        right_btn = QtWidgets.QPushButton("→")
        right_btn.clicked.connect(self.nudge_bg_right)
        arrow_layout.addWidget(right_btn, 1, 2)

        # Down arrow
        down_btn = QtWidgets.QPushButton("↓")
        down_btn.clicked.connect(self.nudge_bg_down)
        arrow_layout.addWidget(down_btn, 2, 1)

        # Row 2: slider for background scale
        scale_layout = QtWidgets.QHBoxLayout()
        edit_layout.addLayout(scale_layout)
        scale_label = QtWidgets.QLabel("Background Scale:")
        scale_layout.addWidget(scale_label)

        self.bg_scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.bg_scale_slider.setRange(0, 100)
        self.bg_scale_slider.setValue(50)  # default = 50 => 1.0 scale
        self.bg_scale_slider.valueChanged.connect(self.on_bg_scale_changed)
        scale_layout.addWidget(self.bg_scale_slider)

        # Row 3: center/frame-all
        button_layout = QtWidgets.QHBoxLayout()
        edit_layout.addLayout(button_layout)

        center_btn = QtWidgets.QPushButton("Center on Zero")
        center_btn.clicked.connect(self.on_center_zero_clicked)
        button_layout.addWidget(center_btn)

        frame_all_btn = QtWidgets.QPushButton("Frame All")
        frame_all_btn.clicked.connect(self.on_frame_all_clicked)
        button_layout.addWidget(frame_all_btn)

        # Create a default 1x1 button
        picker.create_picker_button(
            label="DefaultButton",
            grid_pos=(0, 0),
            size_in_cells=(1, 1),
            parent_grid=self.grid_widget
        )

        self.selected_picker_button = None
        self.picker_parent_grid_label.setText("GridWidget")  # just a placeholder name

    # -------------------------------------------------------------------------
    # BG methods
    # -------------------------------------------------------------------------
    def on_load_background_clicked(self):
        # allow .svg in the filter
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Background Image",
            "",
            "Image Files (*.png *.jpg *.bmp *.tif *.tga *.jpeg *.svg)"
        )
        if image_path:
            self.grid_widget.set_background_image(image_path)

    def nudge_bg_left(self):
        self.grid_widget.nudge_bg_left()

    def nudge_bg_right(self):
        self.grid_widget.nudge_bg_right()

    def nudge_bg_up(self):
        self.grid_widget.nudge_bg_up()

    def nudge_bg_down(self):
        self.grid_widget.nudge_bg_down()

    def on_bg_scale_changed(self, value):
        """
        slider [0..100], 0 => 0.5, 50 => 1.0, 100 =>2.0
        We'll let the grid widget do the piecewise logic in set_bg_scale().
        """
        self.grid_widget.set_bg_scale(value)

    # -------------------------------------------------------------------------
    # Existing center/frame-all
    # -------------------------------------------------------------------------
    def on_center_zero_clicked(self):
        self.grid_widget.center_on_zero()

    def on_frame_all_clicked(self):
        self.grid_widget.frame_all()

    # -------------------------------------------------------------------------
    # Picker edit controls
    # -------------------------------------------------------------------------
    def on_picker_submit_clicked(self):
        """
        If no button is selected (self.selected_picker_button is None),
        we 'Add' a new button. Otherwise, we 'Update' the existing one.
        """
        label = self.picker_label_input.text()
        gx = self.picker_grid_x.value()
        gy = self.picker_grid_y.value()
        w = self.picker_width.value()
        h = self.picker_height.value()

        # Are we adding or updating?
        if self.selected_picker_button is None:
            # Add a new button
            new_btn = picker.create_picker_button(
                label=label,
                grid_pos=(gx, gy),
                size_in_cells=(w, h),
                parent_grid=self.grid_widget
            )
            # Optionally, select it after creation
            self.set_selected_picker_button(new_btn)
        else:
            # Update the selected button
            btn = self.selected_picker_button
            btn.setText(label)
            btn.grid_x = gx
            btn.grid_y = gy
            btn.width_in_cells = w
            btn.height_in_cells = h
            btn.place_in_grid()  # reposition

            # No need to re-parent, it's already in self.grid_widget
            # Keep it selected
            self.set_selected_picker_button(btn)

    def on_picker_delete_clicked(self):
        """
        Remove the currently selected picker button from the grid.
        """
        if not self.selected_picker_button:
            return
        btn = self.selected_picker_button
        # we can call a helper in picker.py or do it right here
        btn.setParent(None)  # removes from layout
        btn.deleteLater()

        self.set_selected_picker_button(None)  # clear selection

    def set_selected_picker_button(self, btn):
        """
        Select or deselect a picker button.
        """
        # Deselect previously selected button
        if self.selected_picker_button and self.selected_picker_button != btn:
            self.selected_picker_button.setStyleSheet("""
                QPushButton {
                    background-color: #607d8b;
                    color: #fff;
                    border: 1px solid #455a64;
                }
                QPushButton:hover {
                    background-color: #455a64;
                }
            """)

        self.selected_picker_button = btn

        if btn is None:
            # Deselect: clear fields and reset UI
            self.picker_label_input.setText("")
            self.picker_grid_x.setValue(0)
            self.picker_grid_y.setValue(0)
            self.picker_width.setValue(1)
            self.picker_height.setValue(1)

            self.picker_submit_btn.setText("Add")
            self.picker_delete_btn.setEnabled(False)
        else:
            # Select: populate fields with button's data
            self.picker_label_input.setText(btn.text())
            self.picker_grid_x.setValue(btn.grid_x)
            self.picker_grid_y.setValue(btn.grid_y)
            self.picker_width.setValue(btn.width_in_cells)
            self.picker_height.setValue(btn.height_in_cells)

            self.picker_submit_btn.setText("Update")
            self.picker_delete_btn.setEnabled(True)

            # Highlight the selected button
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f9aa26;
                    color: #000;
                    border: 2px solid #fff;
                }
                QPushButton:hover {
                    background-color: #f9aa26;
                }
            """)

    def on_picker_button_event(self, event_type, btn):
        """
        Handle all picker button events: 'selected', 'run_command', 'moved', 'deselect'.
        """
        print(f"[CharacterPicker] Handling event '{event_type}' from button '{btn.text() if btn else 'None'}'")
        if event_type == "selected":
            # Select the button and update UI fields
            self.set_selected_picker_button(btn)

        elif event_type == "run_command":
            # Execute the button's assigned command
            print(f"RUN command for '{btn.text()}' at ({btn.grid_x}, {btn.grid_y})")
            # Here you can integrate the actual command execution logic

        elif event_type == "moved":
            # If the moved button is the currently selected one, update the Grid Pos fields
            if self.selected_picker_button == btn:
                print(f"[CharacterPicker] Updating grid position for '{btn.text()}' to ({btn.grid_x}, {btn.grid_y})")
                self.picker_grid_x.setValue(btn.grid_x)
                self.picker_grid_y.setValue(btn.grid_y)

        elif event_type == "deselect":
            # Deselect any selected button
            self.set_selected_picker_button(None)

        else:
            print(f"[CharacterPicker] Unknown event_type={event_type} for button={btn.text() if btn else 'None'}")


def show_character_picker():
    """Show or re-show the CharacterPicker in Maya."""
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, CharacterPicker):
            widget.close()

    picker_window = CharacterPicker()
    picker_window.setWindowFlags(QtCore.Qt.Window)
    picker_window.show()


if __name__ == "__main__":
    show_character_picker()
