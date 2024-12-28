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
        self.grid_x = 0
        self.grid_y = 0
        self.width_in_cells = 1
        self.height_in_cells = 1

        self._dragging = False
        self._drag_start_pos = None

        # Remove the clicked connection if it exists
        # self.clicked.disconnect()  # Ensure no residual connections

        # Set default style
        self.set_default_style()

    def set_default_style(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #607d8b;
                color: #fff;
                border: 1px solid #455a64;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)

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

    def place_in_grid(self):
        self.grid_widget.ensure_point_in_bounds(self.grid_x, self.grid_y)
        px, py = self.grid_widget.grid_to_pixel(self.grid_x, self.grid_y)
        w = self.width_in_cells * self.grid_widget.cell_size
        h = self.height_in_cells * self.grid_widget.cell_size
        self.setGeometry(int(px), int(py), int(w), int(h))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.grid_widget.edit_mode:
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


def create_picker_button(label, grid_pos, size_in_cells, parent_grid):
    btn = PickerButton(label, parent_grid)
    btn.grid_x, btn.grid_y = grid_pos
    btn.width_in_cells, btn.height_in_cells = size_in_cells
    btn.place_in_grid()
    btn.show()

    # Connect to the grid's handle_picker_button_event
    btn.button_event.connect(parent_grid.handle_picker_button_event)
    return btn
