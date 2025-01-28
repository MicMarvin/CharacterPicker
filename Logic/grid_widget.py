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
    picker_event = QtCore.Signal(str, object, bool)  # (event_type, PickerButton, shift_pressed)

    # Define a signal to emit when the grid is panned
    grid_panned = QtCore.Signal()
    
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

    @property
    def edit_mode(self):
        """
        Returns True if the top-level CharacterPicker is in edit mode,
        or False otherwise.
        """
        # window() gives us the top-level widget containing this GridWidget
        top_level = self.window()
        # If the top-level widget (CharacterPicker) has an 'edit_mode' attribute,
        # return it; otherwise default to False.
        if hasattr(top_level, "edit_mode"):
            return top_level.edit_mode
        return False

    def set_background_image(self, image_path):
        """
        Load a background image from the given file path.
        If .svg, scale once to fit the widget (KeepAspectRatio) at load time.
        If raster, do the same with pixmap.scaled(...).
        Then store it in self.bg_pixmap.
        """
        if not image_path:
            self.bg_pixmap = None
            self.update()
            return

        def scale_and_set_image():
            if self.width() > 0 and self.height() > 0:
                if image_path.lower().endswith(".svg"):
                    svg_renderer = QtSvg.QSvgRenderer(image_path)
                    if not svg_renderer.isValid():
                        print(f"Failed to load SVG: {image_path}")
                        self.bg_pixmap = None
                        self.update()
                        return

                    # 1) Get the intrinsic default size from the SVG
                    default_size = svg_renderer.defaultSize()
                    w = default_size.width()
                    h = default_size.height()

                    # If the SVG doesn't report a default size, use a fallback
                    if w < 1 or h < 1:
                        w, h = 512, 512

                    # 2) Compare with the widget's size to find the best ratio
                    widget_w = self.width()
                    widget_h = self.height()
                    ratio = min(widget_w / w, widget_h / h)

                    # 3) The target size to keep aspect ratio
                    target_w = max(int(w * ratio), 1)
                    target_h = max(int(h * ratio), 1)

                    # Create a QImage of that target size
                    temp_image = QtGui.QImage(target_w, target_h, QtGui.QImage.Format_ARGB32)
                    temp_image.fill(QtCore.Qt.transparent)

                    # Render the SVG at that size
                    svg_painter = QtGui.QPainter(temp_image)
                    svg_renderer.render(svg_painter)
                    svg_painter.end()

                    # Convert to QPixmap
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
                        print(f"Failed to load raster image: {image_path}")
                        self.bg_pixmap = None

                # Reset BG offsets + scale
                self.bg_offset_gx = 0.0
                self.bg_offset_gy = 0.0
                self.bg_scale_factor = 1.0

                self.update()
            else:
                # Widget size not stable; retry scaling
                print(f"Widget size not stable for {image_path}, retrying...")
                QtCore.QTimer.singleShot(0, scale_and_set_image)

        scale_and_set_image()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        # Draw background first
        if self.bg_pixmap:
            self.draw_background(painter)

        if self.edit_mode:
            self.draw_grid_lines(painter)

        painter.end()

    def draw_background(self, painter):
        """
        We interpret (bg_offset_gx, bg_offset_gy) in grid coords,
        then apply bg_scale_factor. The image center aligns with grid (0,0)
        plus any offset we specify. It does not scale with cell_size.
        """
        painter.save()

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        # Translate to the grid's (0,0) in pixel space
        painter.translate(center_x + self.offset_x, center_y + self.offset_y)

        # Convert bg_offset_gx/gy from grid coords to px (just 1 cell => cell_size px)
        offset_px_x = self.bg_offset_gx * self.cell_size
        offset_px_y = -(self.bg_offset_gy * self.cell_size)  # negative for y-up
        painter.translate(offset_px_x, offset_px_y)

        # Then scale by bg_scale_factor
        painter.scale(self.bg_scale_factor, self.bg_scale_factor)

        pix_w = self.bg_pixmap.width()
        pix_h = self.bg_pixmap.height()

        # Draw with the image center at (0,0)
        painter.drawPixmap(-pix_w / 2, -pix_h / 2, self.bg_pixmap)

        painter.restore()

    def draw_grid_lines(self, painter):
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

    # Nudge by 0.5 cell
    def nudge_bg_left(self):
        self.bg_offset_gx -= 0.25  # CHANGED from 1 to 0.25
        self.update()

    def nudge_bg_right(self):
        self.bg_offset_gx += 0.25
        self.update()

    def nudge_bg_up(self):
        self.bg_offset_gy += 0.25
        self.update()

    def nudge_bg_down(self):
        self.bg_offset_gy -= 0.25
        self.update()

    def set_bg_scale(self, slider_value):
        """
        Adjust the scale factor for the background image.
        slider_value in [0..100], 0 => min_scale, 50 => default_scale, 100 => max_scale.
        """
        min_scale = 0.1
        default_scale = 1.0
        max_scale = 10.0

        if slider_value <= 50:
            scale = min_scale + (default_scale - min_scale) * (slider_value / 50.0)
        else:
            scale = default_scale + (max_scale - default_scale) * ((slider_value - 50) / 50.0)

        self.bg_scale_factor = scale
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reposition_all_buttons()

    def is_position_available(self, new_grid_pos, exclude_btn=None):
        """
        Check if the new_grid_pos is available (no other button occupies it).
        :param new_grid_pos: Tuple (gx, gy)
        :param exclude_btn: PickerButton to exclude from the check (useful when moving the button itself)
        :return: True if available, False otherwise
        """
        for child in self.findChildren(picker.PickerButton):
            if child == exclude_btn:
                continue
            if child.grid_pos == new_grid_pos:
                return False
        return True

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
        for child in self.findChildren(picker.PickerButton):
            child.place_in_grid()

    def frame_all(self):
        # 1) Gather bounding box from all PickerButtons
        buttons_found = False
        min_gx = None
        max_gx = None
        min_gy = None
        max_gy = None

        for child in self.findChildren(QtWidgets.QPushButton):
            # Instead of checking grid_x, grid_y, check if child is a PickerButton
            if isinstance(child, picker.PickerButton):
                gx, gy = child.grid_pos              # e.g. (grid_x, grid_y)
                w_cells, h_cells = child.size_in_cells  # e.g. (width_in_cells, height_in_cells)

                # bounding box in grid coords for this button
                b_minx = gx
                b_maxx = gx + (w_cells - 1)
                b_miny = gy
                b_maxy = gy + (h_cells - 1)

                # merge
                if min_gx is None or b_minx < min_gx:
                    min_gx = b_minx
                if max_gx is None or b_maxx > max_gx:
                    max_gx = b_maxx
                if min_gy is None or b_miny < min_gy:
                    min_gy = b_miny
                if max_gy is None or b_maxy > max_gy:
                    max_gy = b_maxy

                buttons_found = True

        if not buttons_found:
            # no buttons => define a trivial bounding box so we can still handle the background
            min_gx, max_gx, min_gy, max_gy = 0, 1, 0, 1

        # 2) Merge with background bounding box if we have a bg_pixmap
        #    (same logic as before)
        if self.bg_pixmap:
            pixmap_w = self.bg_pixmap.width()
            pixmap_h = self.bg_pixmap.height()
            factor = self.bg_scale_factor
            cs = self.cell_size

            current_bg_w_pixels = pixmap_w * factor
            current_bg_h_pixels = pixmap_h * factor

            bg_w_grid = current_bg_w_pixels / cs
            bg_h_grid = current_bg_h_pixels / cs

            bg_min_x = self.bg_offset_gx - (bg_w_grid / 2.0)
            bg_max_x = self.bg_offset_gx + (bg_w_grid / 2.0)
            bg_min_y = self.bg_offset_gy - (bg_h_grid / 2.0)
            bg_max_y = self.bg_offset_gy + (bg_h_grid / 2.0)

            if bg_min_x < min_gx:
                min_gx = bg_min_x
            if bg_max_x > max_gx:
                max_gx = bg_max_x
            if bg_min_y < min_gy:
                min_gy = bg_min_y
            if bg_max_y > max_gy:
                max_gy = bg_max_y

        # 3) Now compute the bounding box size and do the scaling/centering
        grid_bbox_w = (max_gx - min_gx)
        grid_bbox_h = (max_gy - min_gy)
        if grid_bbox_w <= 0 or grid_bbox_h <= 0:
            return

        margin_px = 20
        avail_w = self.width() - margin_px
        avail_h = self.height() - margin_px
        if avail_w <= 0 or avail_h <= 0:
            return

        desired_cell_size_w = avail_w / grid_bbox_w
        desired_cell_size_h = avail_h / grid_bbox_h
        new_cell_size = min(desired_cell_size_w, desired_cell_size_h)
        new_cell_size = max(self.MIN_CELL_SIZE, min(new_cell_size, self.MAX_CELL_SIZE))

        old_cell_size = self.cell_size
        if old_cell_size > 0:
            ratio = new_cell_size / old_cell_size
            self.bg_scale_factor *= ratio
        self.cell_size = new_cell_size

        mid_gx = (min_gx + max_gx) / 2.0
        mid_gy = (min_gy + max_gy) / 2.0

        px_mid, py_mid = self.grid_to_pixel(mid_gx, mid_gy)
        desired_cx = self.width() / 2.0
        desired_cy = self.height() / 2.0
        shift_x = desired_cx - px_mid
        shift_y = desired_cy - py_mid

        self.offset_x += shift_x
        self.offset_y += shift_y

        self.reposition_all_buttons()
        self.update()

    def apply_zoom(self, increment):
        """
        Zoom the grid by 'increment' in cell_size.
        If in animate mode, also scale the background by the same ratio.
        """
        old_cell_size = self.cell_size

        new_cell_size = self.cell_size + increment
        if new_cell_size < self.MIN_CELL_SIZE:
            new_cell_size = self.MIN_CELL_SIZE
        elif new_cell_size > self.MAX_CELL_SIZE:
            new_cell_size = self.MAX_CELL_SIZE

        # If we are in animate mode, scale the background ratio
        if not self.edit_mode and old_cell_size > 0:
            ratio = new_cell_size / float(old_cell_size)
            self.bg_scale_factor *= ratio

        self.cell_size = new_cell_size
        self.reposition_all_buttons()
        self.update()

    def grid_to_pixel(self, grid_x, grid_y):
        """Convert grid coordinates to pixel coordinates, accounting for panning and Y-axis inversion."""
        # Apply panning offset
        pixel_x = (grid_x * self.cell_size) + (self.width() / 2) + self.offset_x
        # Invert Y-axis: positive Y upwards
        pixel_y = (self.height() / 2) - (grid_y * self.cell_size) + self.offset_y
        return (pixel_x, pixel_y)

    def pixel_to_grid(self, pixel_x, pixel_y):
        """Convert pixel coordinates to grid coordinates, accounting for panning and Y-axis inversion."""
        # Adjust for panning offset
        adjusted_x = pixel_x - (self.width() / 2) - self.offset_x
        adjusted_y = (self.height() / 2) - pixel_y - self.offset_y  # Invert Y-axis
        grid_x = adjusted_x / self.cell_size
        grid_y = adjusted_y / self.cell_size
        return (grid_x, grid_y)

    def handle_picker_button_event(self, event_type, btn, shift_pressed=False):
        """
        Handle different types of button events and forward them: 'selected', 'run_command', 'moved', 'deselect'.
        """
        if btn:
            btn_label = btn.text()
        else:
            btn_label = 'None'

        print(f"[GridWidget] Received event '{event_type}' from button '{btn_label}', shift={shift_pressed}")
        # Forward the event upwards with the shift boolean
        self.picker_event.emit(event_type, btn, shift_pressed)

    # ------------------------
    #  Mouse Events
    # ------------------------
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._dragging = True
            self._drag_start = event.pos()
            event.accept()

        elif event.button() == QtCore.Qt.LeftButton:
            # Check if user clicked on a child (e.g. a PickerButton)
            child = self.childAt(event.pos())
            # If child is None or not a PickerButton, deselect
            if not child or not isinstance(child, picker.PickerButton):
                # Clear selection for all buttons
                top_level = self.window()
                if hasattr(top_level, "clear_multi_select"):
                    top_level.clear_multi_select()  
        elif event.button() == QtCore.Qt.RightButton:
            child = self.childAt(event.pos())
            selected_button = child if isinstance(child, picker.PickerButton) else None

            if selected_button:
                self.context_menu.selected_button = selected_button
                self.context_menu.set_context_type('button')
                self.context_menu.grid_pos = None
            else:
                self.context_menu.selected_button = None
                self.context_menu.set_context_type('grid')

                # Get the grid coordinates of the right-clicked spot
                gx, gy = self.pixel_to_grid(event.pos().x(), event.pos().y())
                # Store that grid position in the context menu
                self.context_menu.grid_pos = (round(gx), round(gy))

            self.context_menu.exec_(event.globalPos())
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

            # Emit grid_panned signal
            self.grid_panned.emit()

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
        """
        Zoom in/out with mouse wheel. 
        'delta' is typically 120 per wheel step in many systems,
        so we pick a step=2 or step=1 to get a nice ratio.
        """
        delta = event.angleDelta().y()
        step = 2  # or 1 if you want smaller increments

        if delta > 0:
            self.apply_zoom(step)
        else:
            self.apply_zoom(-step)
        event.accept()
