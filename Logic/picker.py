# picker.py
from PySide2 import QtCore, QtWidgets, QtGui
import math


class PickerButton(QtWidgets.QPushButton):
    """
    A button that knows its grid-based size and position.
    Unified event handling using button_event signal.
    """
    button_event = QtCore.Signal(str, object)  # (event_type, self)

    # Define a drag threshold (in pixels)
    DRAG_THRESHOLD = 15

    def __init__(self, label, grid_widget):
        super().__init__(label, grid_widget)
        self.grid_widget = grid_widget

        # Set default style
        self.set_default_style()

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(self.default_style())

    def default_style(self):
        return """
            QPushButton {
                border: 1px solid #2d2d2d;
                background-color: #373737;
                color: #A6A6A6;
                font-size: 14px;
            }
            QPushButton:hover {
                border: 2px solid #f9aa26;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """

    def set_selected_style(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #f9aa26;
                color: #000;
                border: 2px solid #fff;
            }
            QPushButton:hover {
                background-color: #f9aa26;
            }
        """)

    def set_default_style(self):
        self.setStyleSheet(self.default_style())

    def place_in_grid(self):
        self.grid_widget.ensure_point_in_bounds(self.grid_x, self.grid_y)
        px, py = self.grid_widget.grid_to_pixel(self.grid_x, self.grid_y)
        w = self.width_in_cells * self.grid_widget.cell_size
        h = self.height_in_cells * self.grid_widget.cell_size
        self.setGeometry(int(px), int(py), int(w), int(h))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.grid_widget.edit_mode:
            self.button_event.emit("selected", self)

            self._dragging = False  # Reset dragging flag
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.grid_widget.edit_mode and self._drag_start_pos:
            # Calculate the distance moved from the initial press
            delta = event.pos() - self._drag_start_pos
            distance = math.hypot(delta.x(), delta.y())

            if not self._dragging and distance >= self.DRAG_THRESHOLD:
                self._dragging = True  # Start dragging

            if self._dragging:
                # Perform dragging logic
                new_pos = self.mapToParent(event.pos() - self._drag_start_pos)
                self.move(new_pos)

                # Update grid position based on new pixel position
                gx, gy = self.grid_widget.pixel_to_grid(new_pos.x(), new_pos.y())
                gx, gy = round(gx), round(gy)

                self.grid_x = gx
                self.grid_y = gy
                self.place_in_grid()

                # Emit “moved” event
                self.button_event.emit("moved", self)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.grid_widget.edit_mode:
            if self._dragging:
                # Emit 'moved' event after drag release
                print(f"[PickerButton] Emitting 'moved' for '{self.text()}' to ({self.grid_x}, {self.grid_y})")
                self.button_event.emit("moved", self)
            else:
                # Emit 'selected' event
                print(f"[PickerButton] Emitting 'selected' for '{self.text()}'")
                self.button_event.emit("selected", self)

            # Reset dragging flags
            self._dragging = False
            self._drag_start_pos = None

        super().mouseReleaseEvent(event)


def create_picker_button(grid_widget, data_dict):
    """
    Actually create and place a new PickerButton in the given GridWidget.
    """
    label = data_dict["label"]
    gx, gy = data_dict["grid_pos"]
    w, h = data_dict["size_in_cells"]

    btn = PickerButton(label, grid_widget)
    btn.grid_x = gx
    btn.grid_y = gy
    btn.width_in_cells, btn.height_in_cells = w, h

    # Additional data? e.g. shape, color, command, etc.
    # btn.shape = data_dict.get("shape", "rectangle")
    # btn.color = data_dict.get("color", "#ffffff")

    # Place & show
    btn.place_in_grid()
    btn.show()

    # Connect the button's events to the grid or tab_manager
    btn.button_event.connect(grid_widget.handle_picker_button_event)

    return btn

