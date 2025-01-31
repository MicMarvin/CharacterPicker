# picker.py
import logging
from PySide2 import QtCore, QtWidgets, QtGui
import math
import sys

logger = logging.getLogger(__name__)

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
        self._opacity = self.data_dict["opacity"]
        self._direction = self.data_dict["direction"]

        # Selection state
        self._selected = False

        # Initialize dragging flags
        self._dragging = False
        self._drag_start_mouse_pos = None
        self._initial_grid_pos = None

        # Initialize hover state
        self._hovered = False

        # Initialize drag threshold tracking
        self._drag_started = False
        self._mouse_press_pos = None

        # Enable hover events
        self.setAttribute(QtCore.Qt.WA_Hover, True)
        self.setMouseTracking(True)  # Optional

        # Apply initial color and opacity
        self.set_color(self._color)

        # Connect to grid panned signal
        self.grid_widget.grid_panned.connect(self.update_position)

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

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self.set_color(QtGui.QColor(value))

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.data_dict["opacity"] = value
        self.set_color(self._color)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        # Clamp the value between -90 and +90 degrees
        value = max(-90, min(90, value))
        self._direction = value
        self.data_dict["direction"] = self._direction
        self.update()  # Trigger repaint

    # ------------------- Style Management -------------------
    def set_color(self, color):
        """Set the button color and apply opacity if necessary."""
        if not isinstance(color, QtGui.QColor):
            color = QtGui.QColor(color)  # Ensure it's a QColor instance

        # Map the opacity value (1-10) to the range 10%-100%
        mapped_opacity = self._opacity * 10  # Assuming opacity range is 1-10

        alpha = int(255 * (mapped_opacity / 100.0))  # Convert to 0-255 scale
        color.setAlpha(alpha)

        self._color = color
        self.data_dict["color"] = color.name(QtGui.QColor.HexRgb)
        self.update()

    def set_unselected_style(self):
        """Revert to the default style when the button is deselected."""
        self._selected = False
        self.update()  # Trigger repaint

    def set_selected_style(self):
        """Set the style for when the button is selected."""
        self._selected = True
        self.update()  # Trigger repaint 

    # ------------------- Grid Placement -------------------

    def update_position(self):
        """Recalculate and update the widget's position based on grid panning."""
        self.place_in_grid()

    def place_in_grid(self):
        """Place the button in the grid based on grid_pos and size_in_cells."""
        grid_x, grid_y = self.grid_pos
        
        # Check if the position is available
        if not self.grid_widget.is_position_available((grid_x, grid_y), exclude_btn=self):
            logger.info(f"Position ({grid_x}, {grid_y}) is already occupied. Cannot move '{self.text()}'.")
            return  # Or choose to find the nearest available position

        self.grid_widget.ensure_point_in_bounds(grid_x, grid_y)
        px, py = self.grid_widget.grid_to_pixel(grid_x, grid_y)

        w, h = self.size_in_cells
        # Calculate the diagonal to accommodate rotation without clipping
        diagonal = math.ceil(math.sqrt(w**2 + h**2))
        padding_in_cells = 0  # No padding to minimize interactive area
        widget_size_in_cells = diagonal + 2 * padding_in_cells  # Minimal padding
        widget_size = widget_size_in_cells * self.grid_widget.cell_size

        # Position the widget's center at (px, py)
        top_left_x = px - widget_size / 2
        top_left_y = py - widget_size / 2
        self.setGeometry(int(top_left_x), int(top_left_y), int(widget_size), int(widget_size))

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
                # Enable dragging only in Edit Mode
                self._dragging = True

                # Store the initial grid position
                self._initial_grid_pos = self.grid_pos

                # Store the initial mouse position in grid coordinates
                mouse_widget_pos = self.grid_widget.mapFromGlobal(event.globalPos())
                self._initial_mouse_grid_pos = self.grid_widget.pixel_to_grid(
                    mouse_widget_pos.x(),
                    mouse_widget_pos.y()
                )

                # Store the mouse press position for drag threshold
                self._mouse_press_pos = event.pos()
                self._drag_started = False  # Reset drag started flag

                # Emit 'selected' event for selection logic
                shift_pressed = bool(event.modifiers() & QtCore.Qt.ShiftModifier)
                self.button_event.emit("selected", self, shift_pressed)
            else:
                # In Animate Mode, do not initiate dragging
                pass

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self.grid_widget.edit_mode:
            if not self._drag_started:
                # Calculate the distance moved since mouse press
                delta = event.pos() - self._mouse_press_pos
                distance = math.hypot(delta.x(), delta.y())
                if distance >= self.DRAG_THRESHOLD:
                    self._drag_started = True  # Initiate drag

            if self._drag_started:
                # Current mouse position relative to the GridWidget
                current_mouse_pos = self.grid_widget.mapFromGlobal(event.globalPos())

                # Convert pixel position to grid coordinates
                current_grid_x, current_grid_y = self.grid_widget.pixel_to_grid(
                    current_mouse_pos.x(),
                    current_mouse_pos.y()
                )

                # Calculate the delta from the initial mouse grid position
                delta_x = current_grid_x - self._initial_mouse_grid_pos[0]
                delta_y = current_grid_y - self._initial_mouse_grid_pos[1]

                # Update grid_pos based on the initial grid position plus delta
                new_grid_x = self._initial_grid_pos[0] + delta_x
                new_grid_y = self._initial_grid_pos[1] + delta_y

                # Snap to nearest grid position
                new_grid_x, new_grid_y = round(new_grid_x), round(new_grid_y)

                # Update grid_pos
                self.grid_pos = (new_grid_x, new_grid_y)

                # Emit 'moved' event
                shift_pressed = bool(event.modifiers() & QtCore.Qt.ShiftModifier)
                self.button_event.emit("moved", self, shift_pressed)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self._dragging and self.grid_widget.edit_mode:
                if self._drag_started:
                    # Dragging occurred, 'moved' event already emitted during drag
                    pass
                else:
                    # No dragging, interpret as a click
                    # Already handled 'selected' event on press
                    pass
                # Reset dragging flags
                self._dragging = False
                self._initial_mouse_grid_pos = None
                self._initial_grid_pos = None
                self._mouse_press_pos = None
                self._drag_started = False
            elif not self.grid_widget.edit_mode:
                # In Animate Mode, emit 'run_command' on click
                shift_pressed = bool(event.modifiers() & QtCore.Qt.ShiftModifier)
                self.button_event.emit("run_command", self, shift_pressed)

        super().mouseReleaseEvent(event)

    # ------------------- Custom Painting -------------------

    def paintEvent(self, event):
        """Override QPushButton's paint event for custom shapes with rotation."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Save the current painter state
        painter.save()

        # Apply rotation around the center
        center_x = self.width() / 2
        center_y = self.height() / 2
        painter.translate(center_x, center_y)
        painter.rotate(self.direction)
        painter.translate(-center_x, -center_y)

        # Determine colors based on selection state
        if self._dragging:
            brush_color = self._color.lighter(150)  # Lighter color to indicate dragging
            pen_color = QtGui.QColor("#f9aa26")  # Green border for dragging
            pen_width = 2
        elif self._selected:
            brush_color = self._color  # Selected background color
            pen_color = QtGui.QColor("#ffffff")  # Selected border color
            pen_width = 2  # Selected border width
        elif self._hovered:
            brush_color = self._color  # Hover background color
            pen_color = QtGui.QColor("#ffffff")  # Hover border color
            pen_width = 2  # Hover border width
        else:
            brush_color = self._color  # Unselected background color
            pen_color = QtGui.QColor("#000000")  # Unselected border color
            pen_width = 1  # Unselected border width

        # Set up the brush and pen with opacity included
        brush = QtGui.QBrush(brush_color)
        pen = QtGui.QPen(pen_color)
        pen.setWidth(pen_width)

        painter.setBrush(brush)
        painter.setPen(pen)

        # Determine the shape's dimensions based on size_in_cells
        w, h = self.size_in_cells
        width = w * self.grid_widget.cell_size
        height = h * self.grid_widget.cell_size

        # Calculate padding (none in this case)
        padding_in_cells = 0  # No padding to minimize interactive area
        padding = self.grid_widget.cell_size * padding_in_cells

        # Calculate available drawing area
        available_width = self.width() - 2 * padding
        available_height = self.height() - 2 * padding

        # No padding applied
        adjusted_width = width
        adjusted_height = height

        # Recalculate position to center the shape
        x = (self.width() - adjusted_width) / 2
        y = (self.height() - adjusted_height) / 2

        # Ensure minimum dimensions for visibility
        min_size = self.grid_widget.cell_size
        adjusted_width = max(adjusted_width, min_size)
        adjusted_height = max(adjusted_height, min_size)

        # Draw the appropriate shape
        shape = self.shape
        if shape == "rectangle":
            painter.drawRect(int(x), int(y), int(adjusted_width), int(adjusted_height))
        elif shape == "circle":
            painter.drawEllipse(int(x), int(y), int(adjusted_width), int(adjusted_height))
        elif shape == "triangle":
            points = [
                QtCore.QPoint(int(x + adjusted_width / 2), int(y)),
                QtCore.QPoint(int(x), int(y + adjusted_height)),
                QtCore.QPoint(int(x + adjusted_width), int(y + adjusted_height))
            ]
            painter.drawPolygon(QtGui.QPolygon(points))
        else:
            # Fallback to rectangle if unknown shape
            painter.drawRect(int(x), int(y), int(adjusted_width), int(adjusted_height))

        # Determine text color based on the background brightness
        brightness = brush_color.red() * 0.299 + brush_color.green() * 0.587 + brush_color.blue() * 0.114
        text_color = QtGui.QColor("#000000") if brightness > 186 else QtGui.QColor("#FFFFFF")

        painter.setPen(text_color)
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.data_dict["label"])

        # Restore the painter state
        painter.restore()

        painter.end()

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

        try:
            if mode == "Python":
                exec_globals = {
                    "sys": sys,
                    "QtWidgets": __import__("PySide2.QtWidgets").QtWidgets,
                    "__builtins__": __builtins__
                }
                exec(command, exec_globals)
                logger.info(f"Running Python command:\n{command}")

            elif mode == "MEL":
                import maya.mel as mel

                # Ensure the picker window is stored globally
                if "character_picker_main_window" not in sys.modules:
                    raise ValueError("Picker window not found in sys.modules.")

                picker_window = sys.modules["character_picker_main_window"]

                if not picker_window:
                    raise ValueError("Picker window reference is None.")

                picker_window_name = picker_window.objectName()

                if not picker_window_name:
                    raise ValueError("Picker window name is empty or undefined.")

                # Assign picker window name to a global MEL variable
                mel.eval(f'global string $pickerWindow = "{picker_window_name}";')
                mel.eval(command)
                logger.info(f"Running MEL command:\n{command}")

            elif mode == "Select":
                self._select_objects()

            else:
                logger.warning(f"No valid command mode specified for '{self.data_dict.get('label', 'Unnamed')}'.")

        except Exception as e:
            logger.error(f"Error executing {mode} command: {e}")

    def _select_objects(self):
        """Select (and track) objects for this button in Animate Mode."""
        import maya.cmds as cmds
        # Parse the user’s comma-separated list
        objects = [obj.strip() for obj in self.command_string.split(",") if obj.strip()]
       
        if not objects:
            logger.error(f"No objects to select for '{self._label}'")
            return

        # Perform the selection
        cmds.select(objects, add=True)  # or add=True if you want multi-selection

        # Store the objects we just selected, so we can deselect them later
        self._selected_objects = objects

        # Mark the button as "selected" visually
        self.set_selected_style()

        logger.info(f"Running Select command: {objects}")

    def deselect_objects(self):
        """Deselect the objects this button had selected, if any."""
        if hasattr(self, "_selected_objects"):
            import maya.cmds as cmds
            try:
                cmds.select(self._selected_objects, deselect=True)
            except Exception as e:
                logger.error(f"Error deselecting objects: {e}")
            self._selected_objects = []


def create_picker_button(grid_widget, data_dict):
    """
    Actually create and place a new PickerButton in the given GridWidget.
    """
    # Ensure color is properly formatted as a QColor object
    if isinstance(data_dict["color"], str):
        data_dict["color"] = QtGui.QColor(data_dict["color"])

    btn = PickerButton(data_dict=data_dict, grid_widget=grid_widget)

    # Set grid_pos and size_in_cells using the property setters
    gx, gy = data_dict["grid_pos"]
    w, h = data_dict["size_in_cells"]
    btn.grid_pos = (gx, gy)
    btn.size_in_cells = (w, h)

    # Set direction
    direction = data_dict.get("direction", 0)
    btn.direction = direction  # Setter ensures it's within -90 to +90

    # Place & show
    btn.place_in_grid()
    btn.show()

    # Connect the button's events to the grid's handler
    btn.button_event.connect(grid_widget.handle_picker_button_event)

    return btn

