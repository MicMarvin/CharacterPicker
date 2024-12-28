from PySide2 import QtCore, QtWidgets, QtGui
from PySide2 import QtSvg  # For rendering .svg files
import CharacterPicker.Logic.picker as picker  # Adjust the import path as needed


class GridWidget(QtWidgets.QWidget):
    """
    A widget that draws a center-based grid with negative/positive coordinates.
    The background image can be placed at an offset (in grid coords),
    and has its own scale factor (bg_scale_factor) independent of cell_size.
    """
    # Shared configuration for all grid widgets
    DEFAULT_ROWS = 200
    DEFAULT_COLS = 200
    DEFAULT_CELL_SIZE = 40
    MIN_CELL_SIZE = 10
    MAX_CELL_SIZE = 100

    # Define a signal to emit picker button events
    picker_event = QtCore.Signal(str, object)  # (event_type, PickerButton)

    def __init__(self, rows=None, cols=None, parent=None):
        super().__init__(parent)

        # Use defaults if no specific values are provided
        self.rows = rows or GridWidget.DEFAULT_ROWS
        self.cols = cols or GridWidget.DEFAULT_COLS
        self.cell_size = GridWidget.DEFAULT_CELL_SIZE

        # Initialize min/max from rows/cols
        self.min_x = -(self.cols // 2)
        self.max_x = (self.cols // 2)
        self.min_y = -(self.rows // 2)
        self.max_y = (self.rows // 2)

        # Pan offset (in pixels) for the grid
        self.offset_x = 0.0
        self.offset_y = 0.0

        # Track panning with middle mouse
        self._dragging = False
        self._drag_start = QtCore.QPoint()

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        # Background-related
        self.bg_pixmap = None
        self.bg_offset_gx = 0.0
        self.bg_offset_gy = 0.0
        self.bg_scale_factor = 1.0

        # Reposition any picker buttons once the widget is shown & sized
        QtCore.QTimer.singleShot(0, self.reposition_all_buttons)

        self._edit_mode = True

    @property
    def edit_mode(self) -> bool:
        """Getter for edit_mode."""
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value: bool):
        """Setter for edit_mode."""
        if isinstance(value, bool):
            self._edit_mode = value
        else:
            raise ValueError("edit_mode must be a boolean value.")

    def set_background_image(self, image_path):
        """
        Load a background image from the given file path.
        If .svg, render to QPixmap. Otherwise, load as a normal QPixmap.
        Then scale it once to fit the widget for an initial size.
        Reset bg_offset_gx/gy=0, bg_scale_factor=1.0 so it starts centered.
        """
        if not image_path:
            self.bg_pixmap = None
            self.update()
            return

        if image_path.lower().endswith(".svg"):
            svg_renderer = QtSvg.QSvgRenderer(image_path)
            if not svg_renderer.isValid():
                print(f"Failed to load SVG: {image_path}")
                self.bg_pixmap = None
                self.update()
                return

            render_size = self.size()
            if render_size.width() < 10 or render_size.height() < 10:
                render_size = QtCore.QSize(512, 512)

            temp_image = QtGui.QImage(render_size, QtGui.QImage.Format_ARGB32)
            temp_image.fill(QtCore.Qt.transparent)

            painter = QtGui.QPainter(temp_image)
            svg_renderer.render(painter)
            painter.end()

            self.bg_pixmap = QtGui.QPixmap.fromImage(temp_image)
        else:
            # Raster image
            pixmap = QtGui.QPixmap(image_path)
            if not pixmap.isNull():
                self.bg_pixmap = pixmap.scaled(
                    self.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
            else:
                self.bg_pixmap = None

        # Reset BG offsets + scale
        self.bg_offset_gx = 0.0
        self.bg_offset_gy = 0.0
        self.bg_scale_factor = 1.0

        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        # Draw background first
        if self.bg_pixmap:
            self.draw_background(painter)

        # Now draw the grid lines
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0

        pen = QtGui.QPen(QtGui.QColor(200, 200, 200, 180))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw vertical lines
        for gx in range(self.min_x, self.max_x + 1):
            line_x = center_x + self.offset_x + gx * self.cell_size
            if line_x < 0:
                continue
            if line_x > self.width():
                continue

            top_y = center_y + self.offset_y - (self.max_y * self.cell_size)
            bot_y = center_y + self.offset_y - (self.min_y * self.cell_size)
            line_y1 = max(0, top_y)
            line_y2 = min(self.height(), bot_y)

            if line_y2 >= line_y1:
                painter.drawLine(QtCore.QPointF(line_x, line_y1),
                                 QtCore.QPointF(line_x, line_y2))

        # Draw horizontal lines
        for gy in range(self.min_y, self.max_y + 1):
            line_y = center_y + self.offset_y - gy * self.cell_size
            if line_y < 0:
                continue
            if line_y > self.height():
                continue

            left_x = center_x + self.offset_x + self.min_x * self.cell_size
            right_x = center_x + self.offset_x + self.max_x * self.cell_size
            line_x1 = max(0, left_x)
            line_x2 = min(self.width(), right_x)

            if line_x2 >= line_x1:
                painter.drawLine(QtCore.QPointF(line_x1, line_y),
                                 QtCore.QPointF(line_x2, line_y))

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._dragging = True
            self._drag_start = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            delta = event.pos() - self._drag_start
            self._drag_start = event.pos()

            self.offset_x += delta.x()
            self.offset_y += delta.y()

            self.reposition_all_buttons()
            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        step = 2
        if delta > 0:
            self.cell_size += step
        else:
            self.cell_size -= step

        if self.cell_size < GridWidget.MIN_CELL_SIZE:
            self.cell_size = GridWidget.MIN_CELL_SIZE
        elif self.cell_size > GridWidget.MAX_CELL_SIZE:
            self.cell_size = GridWidget.MAX_CELL_SIZE

        self.reposition_all_buttons()
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reposition_all_buttons()

    def ensure_point_in_bounds(self, gx, gy, margin=2):
        if gx < self.min_x:
            self.min_x = gx - margin
        elif gx > self.max_x:
            self.max_x = gx + margin

        if gy < self.min_y:
            self.min_y = gy - margin
        elif gy > self.max_y:
            self.max_y = gy + margin

        self.update()

    def reposition_all_buttons(self):
        for child in self.findChildren(QtWidgets.QPushButton):
            if hasattr(child, "place_in_grid"):
                child.place_in_grid()

    def center_on_zero(self):
        px, py = self.grid_to_pixel(0, 0)
        desired_cx = self.width() / 2.0
        desired_cy = self.height() / 2.0
        shift_x = desired_cx - px
        shift_y = desired_cy - py

        self.offset_x += shift_x
        self.offset_y += shift_y

        self.reposition_all_buttons()
        self.update()

    def frame_all(self):
        buttons = []
        for child in self.findChildren(QtWidgets.QPushButton):
            if hasattr(child, "grid_x") and hasattr(child, "grid_y"):
                buttons.append(child)
        if not buttons:
            return

        min_gx = min(b.grid_x for b in buttons)
        max_gx = max(b.grid_x + (b.width_in_cells - 1) for b in buttons)
        min_gy = min(b.grid_y for b in buttons)
        max_gy = max(b.grid_y + (b.height_in_cells - 1) for b in buttons)

        grid_bbox_width = (max_gx - min_gx + 1)
        grid_bbox_height = (max_gy - min_gy + 1)

        if grid_bbox_width <= 0 or grid_bbox_height <= 0:
            return

        margin_px = 20
        avail_w = self.width() - margin_px
        avail_h = self.height() - margin_px
        if avail_w <= 0 or avail_h <= 0:
            return

        desired_cell_size_w = avail_w / grid_bbox_width
        desired_cell_size_h = avail_h / grid_bbox_height
        new_cell_size = min(desired_cell_size_w, desired_cell_size_h)

        new_cell_size = max(self.min_cell_size, min(new_cell_size, self.max_cell_size))
        self.cell_size = new_cell_size

        mid_gx = (min_gx + max_gx + 1) / 2.0
        mid_gy = (min_gy + max_gy + 1) / 2.0

        px_mid, py_mid = self.grid_to_pixel(mid_gx, mid_gy)
        desired_cx = self.width() / 2.0
        desired_cy = self.height() / 2.0
        shift_x = desired_cx - px_mid
        shift_y = desired_cy - py_mid

        self.offset_x += shift_x
        self.offset_y += shift_y

        self.reposition_all_buttons()
        self.update()

    def grid_to_pixel(self, gx, gy):
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        px = center_x + self.offset_x + (gx * self.cell_size)
        py = center_y + self.offset_y - (gy * self.cell_size)
        return (px, py)

    def pixel_to_grid(self, px, py):
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        gx = (px - center_x - self.offset_x) / self.cell_size
        gy = -(py - center_y - self.offset_y) / self.cell_size
        return (gx, gy)

    def handle_picker_button_event(self, event_type, btn):
        """
        Handle different types of button events and forward them.
        """
        if btn:
            btn_label = btn.text()
        else:
            btn_label = 'None'

        print(f"[GridWidget] Received event '{event_type}' from button '{btn_label}'")
        # Emit the event upwards
        self.picker_event.emit(event_type, btn)
