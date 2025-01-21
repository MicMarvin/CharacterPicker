# picker.py
from PySide2 import QtCore, QtWidgets, QtGui
import math


class PickerButton(QtWidgets.QPushButton):
    """
    A button that knows its grid-based size and position.
    Unified event handling using button_event signal.
    """
    button_event = QtCore.Signal(str, object, bool)  # (event_type, self, shift_pressed)

    # Define a drag threshold (in pixels)
    DRAG_THRESHOLD = 15

    def __init__(self, data_dict=None, grid_widget=None):
        if data_dict is None:
            raise ValueError("data_dict must be provided to initialize PickerButton.")
        label = data_dict.get("label", " ")
        super().__init__(label, grid_widget)
        self.grid_widget = grid_widget
        self.data_dict = data_dict

        # Initialize explicit attributes with private variables
        self._label = self.data_dict["label"]
        self._shape = self.data_dict["shape"]
        self._color = self.data_dict["color"]
        self._command_mode = self.data_dict["command_mode"]
        self._command_string = self.data_dict["command_string"]
        self._grid_pos = self.data_dict["grid_pos"]
        self._size_in_cells = self.data_dict["size_in_cells"]
        
        # Selection state
        self._selected = False

        # Initialize dragging flags
        self._dragging = False
        self._drag_start_pos = None

        # Initialize hover state
        self._hovered = False

        # Enable hover events
        self.setAttribute(QtCore.Qt.WA_Hover, True)
        self.setMouseTracking(True)  # Optional
    
    # ------------------- Property Setters and Getters -------------------

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value
        self.data_dict["shape"] = value
        self.update()  # Trigger repaint

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.data_dict["color"] = value
        self.update()

    @property
    def command_mode(self):
        return self._command_mode

    @command_mode.setter
    def command_mode(self, value):
        self._command_mode = value
        self.data_dict["command_mode"] = value

    @property
    def command_string(self):
        return self._command_string

    @command_string.setter
    def command_string(self, value):
        self._command_string = value
        self.data_dict["command_string"] = value

    @property
    def grid_pos(self):
        return self._grid_pos

    @grid_pos.setter
    def grid_pos(self, value):
        self._grid_pos = value
        self.data_dict["grid_pos"] = value
        self.place_in_grid()

    @property
    def size_in_cells(self):
        return self._size_in_cells

    @size_in_cells.setter
    def size_in_cells(self, value):
        self._size_in_cells = value
        self.data_dict["size_in_cells"] = value
        self.place_in_grid()

    # ------------------- Style Management -------------------

    def set_unselected_style(self):
        """Revert to the default style when the button is deselected."""
        self._selected = False
        self.update()  # Trigger repaint

    def set_selected_style(self):
        """Set the style for when the button is selected."""
        self._selected = True
        self.update()  # Trigger repaint 

    # ------------------- Grid Placement -------------------

    def place_in_grid(self):
        """Place the button in the grid based on grid_pos and size_in_cells."""
        grid_x, grid_y = self.grid_pos
        self.grid_widget.ensure_point_in_bounds(grid_x, grid_y)
        px, py = self.grid_widget.grid_to_pixel(grid_x, grid_y)
        w = self.size_in_cells[0] * self.grid_widget.cell_size
        h = self.size_in_cells[1] * self.grid_widget.cell_size
        self.setGeometry(int(px), int(py), int(w), int(h))

    # ------------------- Hover Event Handlers -------------------

    def enterEvent(self, event):
        """Handle the mouse entering the widget area."""
        self._hovered = True
        self.update()  # Trigger repaint to reflect hover state
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle the mouse leaving the widget area."""
        self._hovered = False
        self.update()  # Trigger repaint to revert hover state
        super().leaveEvent(event)

    # ------------------- Event Handling -------------------

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.grid_widget.edit_mode:
                # EDIT MODE BEHAVIOR (move, select)
                shift_pressed = bool(event.modifiers() & QtCore.Qt.ShiftModifier)
                self.button_event.emit("selected", self, shift_pressed)
                self._dragging = False  # Reset dragging flag
                self._drag_start_pos = event.pos()
            else:
                pass
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.grid_widget.edit_mode and self._drag_start_pos:
            
            shift_pressed = bool(event.modifiers() & QtCore.Qt.ShiftModifier)
            
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

                self.grid_pos = (gx, gy)
                self.place_in_grid()

                # Emit “moved” event
                self.button_event.emit("moved", self, shift_pressed)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            shift_pressed = bool(event.modifiers() & QtCore.Qt.ShiftModifier)
            if self.grid_widget.edit_mode:
                # EDIT MODE BEHAVIOR (move, select)
                if self._dragging:
                    # Emit 'moved' event after drag release
                    print(f"[PickerButton] Emitting 'moved' for '{self.text()}' to ({self.grid_pos[0]}, {self.grid_pos[1]})")
                    self.button_event.emit("moved", self, shift_pressed)
                else:
                    # Emit 'selected' event
                    print(f"[PickerButton] Emitting 'selected' for '{self.text()}'")
                    self.button_event.emit("selected", self, shift_pressed)
            else:
                # ANIMATE MODE BEHAVIOR (run_command)
                if self._selected and self.command_mode == "select":
                    if shift_pressed:
                        # If it’s already selected and SHIFT is NOT pressed => “deselect”
                        self.button_event.emit("deselect", self, shift_pressed)
                    else:
                        self.button_event.emit("run_command", self, shift_pressed)
                else:
                    # Otherwise, run the command (select objects or code)
                    self.button_event.emit("run_command", self, shift_pressed)

        # Reset dragging flags
        self._dragging = False
        self._drag_start_pos = None

        super().mouseReleaseEvent(event)

    # ------------------- Custom Painting -------------------

    def paintEvent(self, event):
        """Override QPushButton's paint event for custom shapes"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Determine colors based on selection state
        if self._selected:
            brush_color = self.color # Selected background color
            pen_color = "#ffffff"    # Selected border color
            pen_width = 2            # Selected border width
        elif self._hovered:
            # Define hover styles
            brush_color = self.color # Hover background color
            pen_color = "#ffffff"    # Hover border color
            pen_width = 2            # Hover border width
        else:
            brush_color = self.color # Unselected background color
            pen_color = "#000000"    # Unselected border color
            pen_width = 1            # Unselected border width

        # Set up the brush and pen
        brush = QtGui.QBrush(QtGui.QColor(brush_color))
        pen = QtGui.QPen(QtGui.QColor(pen_color))
        pen.setWidth(pen_width)

        painter.setBrush(brush)
        painter.setPen(pen)

        # Draw the appropriate shape
        shape = self.shape
        if shape == "rectangle":
            painter.drawRect(2, 2, self.width()-4, self.height()-4)
        elif shape == "circle":
            painter.drawEllipse(2, 2, self.width()-4, self.height()-4)
        elif shape == "triangle":
            points = [
                QtCore.QPoint(self.width()/2, 2),
                QtCore.QPoint(2, self.height()-2),
                QtCore.QPoint(self.width()-2, self.height()-2)
            ]
            painter.drawPolygon(QtGui.QPolygon(points))
        else:
            # Fallback to rectangle if unknown shape
            painter.drawRect(2, 2, self.width()-4, self.height()-4)

        # Draw the button text
        # Adjust text color based on background for visibility
        bg_color = QtGui.QColor(self.color)
        brightness = bg_color.red() * 0.299 + bg_color.green() * 0.587 + bg_color.blue() * 0.114
        text_color = "#000000" if brightness > 186 else "#FFFFFF"

        painter.setPen(QtGui.QColor(text_color))
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.data_dict["label"])

    def _lighten_color(self, color, factor=0.2):
        """
        Lighten the given color by the specified factor.

        :param color: Hex color string (e.g., "#A6A6A6")
        :param factor: Float representing the lightening factor (0 < factor < 1)
        :return: Hex color string of the lightened color
        """
        color = QtGui.QColor(color)
        r = min(int(color.red() + (255 - color.red()) * factor), 255)
        g = min(int(color.green() + (255 - color.green()) * factor), 255)
        b = min(int(color.blue() + (255 - color.blue()) * factor), 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # ------------------- Command Execution -------------------

    def execute_command(self):
        """Execute the stored command based on command_mode."""
        mode = self.command_mode
        command = self.command_string
        if mode == "python":
            try:
                exec(command, {}, {})
                print(f"Running Python command: {command}")
            except Exception as e:
                print(f"Error executing Python command: {e}")
        elif mode == "select":
            self._select_objects()
        else:
            print(f"No valid command mode specified for '{self.data_dict['label']}'.")

    def _select_objects(self):
        """Select (and track) objects for this button in Animate Mode."""
        import maya.cmds as cmds
        # Parse the user’s comma-separated list
        objects = [obj.strip() for obj in self.command_string.split(",") if obj.strip()]
       
        if not objects:
            print(f"No objects to select for '{self._label}'")
            return

        # Perform the selection
        cmds.select(objects, add=True)  # or add=True if you want multi-selection

        # Store the objects we just selected, so we can deselect them later
        self._selected_objects = objects

        # Mark the button as "selected" visually
        self.set_selected_style()

        print(f"Running Select command: {objects}")

    def deselect_objects(self):
        """Deselect the objects this button had selected, if any."""
        if hasattr(self, "_selected_objects"):
            import maya.cmds as cmds
            try:
                cmds.select(self._selected_objects, deselect=True)
            except Exception as e:
                print(f"Error deselecting objects: {e}")
            self._selected_objects = []


def create_picker_button(grid_widget, data_dict):
    """
    Actually create and place a new PickerButton in the given GridWidget.
    """
    btn = PickerButton(data_dict=data_dict, grid_widget=grid_widget)
    
    # Set grid_pos and size_in_cells using the property setters
    gx, gy = data_dict["grid_pos"]
    w, h = data_dict["size_in_cells"]
    btn.grid_pos = (gx, gy)
    btn.size_in_cells = (w, h)
    
    # Place & show
    btn.place_in_grid()
    btn.show()

    # Connect the button's events to the grid or tab_manager
    btn.button_event.connect(grid_widget.handle_picker_button_event)

    return btn

