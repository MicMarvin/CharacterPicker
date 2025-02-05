import logging
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2 import QtSvg  # For rendering .svg files
import CharacterPicker.Logic.picker as picker  # Adjust the import path as needed

logger = logging.getLogger(__name__)

class GridWidget(QtWidgets.QWidget):
    """
    A widget that draws a center-based grid with negative/positive coordinates.
    The background image can be placed at an offset (in grid coords),
    and has its own scale factor (bg_size_in_cells) independent of cell_size.
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
    
    def __init__(self, rows=None, cols=None, parent=None, context_menu=None):
        super().__init__(parent)

        self.context_menu = context_menu

        # Use defaults if no specific values are provided
        self.rows = rows or GridWidget.DEFAULT_ROWS
        self.cols = cols or GridWidget.DEFAULT_COLS
        self.cell_size = GridWidget.DEFAULT_CELL_SIZE

        # Add a flag to allow one-time automatic adjustment.
        self.auto_adjust = True

        self.loaded = False   # Indicates this page was loaded from saved data

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

        # Initialize background attributes
        self.frozen_bg_pixmap = None
        self.bg_pixmap = None  
        self.background_image = ""  # Path to the background image
        self.bg_size_in_cells = [int(self.width()/self.cell_size), int(self.height()/self.cell_size)]
        self.bg_offset_gx = 0.0
        self.bg_offset_gy = 0.0

        # Reposition any picker buttons once the widget is shown & sized
        QtCore.QTimer.singleShot(0, self.reposition_all_buttons)

        self.framed = False   # Will be set to True when the page has been explicitly framed.

        # Initialize rubber band for marquee selection
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.rubberBand.hide()
        self.rubberBandOrigin = QtCore.QPoint()

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

    def load_background_image(self):
        """
        Loads the background image from self.background_image
        without altering its size, so that later scaling is driven
        solely by bg_size_in_cells and cell_size.
        """
        if not self.background_image:
            self.bg_pixmap = None
            self.update()
            return

        image_path = self.background_image
        if image_path.lower().endswith(".svg"):
            svg_renderer = QtSvg.QSvgRenderer(image_path)
            if not svg_renderer.isValid():
                logger.error(f"Failed to load SVG: {image_path}")
                self.bg_pixmap = None
                self.update()
                return
            default_size = svg_renderer.defaultSize()
            w = default_size.width()
            h = default_size.height()
            if w < 1 or h < 1:
                w, h = 512, 512
                logger.warning(f"SVG '{image_path}' has invalid size. Using fallback size 512x512.")
            # Do not scale here; load intrinsic size.
            temp_image = QtGui.QImage(w, h, QtGui.QImage.Format_ARGB32)
            temp_image.fill(QtCore.Qt.transparent)
            svg_painter = QtGui.QPainter(temp_image)
            svg_renderer.render(svg_painter)
            svg_painter.end()
            self.bg_pixmap = QtGui.QPixmap.fromImage(temp_image)
            logger.info(f"SVG background image loaded (intrinsic size): {image_path}")
        else:
            pixmap = QtGui.QPixmap(image_path)
            if not pixmap.isNull():
                # Load without scaling.
                self.bg_pixmap = pixmap
                logger.info(f"Raster background image loaded (intrinsic size): {image_path}")
            else:
                logger.error(f"Failed to load raster image: {image_path}")
                self.bg_pixmap = None
        self.update()

    def set_background_image(self, image_path, apply_scaling=True):
        if not image_path:
            self.bg_pixmap = None
            self.background_image = ""
            self.update()
            return

        self.background_image = image_path
        # Load the image intrinsically.
        self.load_background_image()
        if apply_scaling:
            # For a new page, set bg_size_in_cells to fill the widget:
            self.bg_size_in_cells = [int(self.width()/self.cell_size), int(self.height()/self.cell_size)]
            # Scale the image accordingly.
            self.scale_background_image()
            
    def scale_background_image(self):
        """
        Scale the loaded background image (self.bg_pixmap, assumed to be at intrinsic size)
        to the desired target size computed from self.cell_size and self.bg_size_in_cells.
        The target dimensions (in pixels) are:
            target_width = cell_size * bg_size_in_cells[0]
            target_height = cell_size * bg_size_in_cells[1]
        """
        if self.bg_pixmap is None:
            return
        target_width = self.cell_size * self.bg_size_in_cells[0]
        target_height = self.cell_size * self.bg_size_in_cells[1]
        # Scale while preserving aspect ratio:
        scaled = self.bg_pixmap.scaled(target_width, target_height,
                                    QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.SmoothTransformation)
        self._cached_scaled_bg = scaled
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        # Draw background first
        if self.bg_pixmap:
            self.draw_background(painter)

        if self.edit_mode:
            self.draw_grid_lines(painter)

        painter.end()

    def draw_background(self, painter):
        painter.save()
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        painter.translate(center_x + self.offset_x, center_y + self.offset_y)
        offset_px_x = self.bg_offset_gx * self.cell_size
        offset_px_y = -(self.bg_offset_gy * self.cell_size)
        painter.translate(offset_px_x, offset_px_y)
        # Compute target size in pixels:
        target_width = self.cell_size * self.bg_size_in_cells[0]
        target_height = self.cell_size * self.bg_size_in_cells[1]
        if self.bg_pixmap:
            # Scale the pixmap on the fly to the target size.
            scaled = self.bg_pixmap.scaled(target_width, target_height,
                                        QtCore.Qt.KeepAspectRatio,
                                        QtCore.Qt.SmoothTransformation)
            pix_w = scaled.width()
            pix_h = scaled.height()
            painter.drawPixmap(-pix_w/2, -pix_h/2, scaled)
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

    @property
    def adjusted_cell_size(self):
        if self.auto_adjust:
            # In edit mode we let cell_size be as is.
            if self.edit_mode:
                return self.cell_size
            # Otherwise, if a reference width is stored, adjust:
            if hasattr(self, "ref_width") and self.ref_width and self.ref_width > 0:
                scale = self.width() / self.ref_width
                return self.cell_size * scale
            return self.cell_size
        else:
            return self.cell_size

    @property
    def adjusted_bg_scale_factor(self):
        if self.auto_adjust:
            if self.edit_mode:
                return self.bg_size_in_cells
            if hasattr(self, "ref_width") and self.ref_width and self.ref_width > 0:
                scale = self.width() / self.ref_width
                return self.bg_size_in_cells * scale
            return self.bg_size_in_cells
        else:
            return self.bg_size_in_cells

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

        self.bg_size_in_cells = scale
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reposition_all_buttons()

    def adjust_to_current_size(self):
        """
        Adjust the stored cell_size and bg_size_in_cells based on the current widget dimensions.
        This method computes a factor from the current width versus the saved reference width,
        applies that factor to cell_size and bg_size_in_cells, updates the reference dimensions,
        and then disables further automatic adjustment.
        """
        if hasattr(self, "ref_width") and self.ref_width and self.ref_width > 0:
            factor = self.width() / self.ref_width
            self.cell_size *= factor
            self.bg_size_in_cells *= factor
        # Update reference dimensions to current size.
        self.ref_width = self.width()
        self.ref_height = self.height()
        # Lock in the values.
        self.auto_adjust = False


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
        """
        1) Gather the bounding box from all picker buttons
        2) Also gather bounding box from the background's current size_in_cells
        (plus offset).
        3) Fit that union of bounding boxes into the window by computing a new
        cell_size. Keep bg_size_in_cells as is. Recenter self.offset_x/y.
        """

        # ----------------------------------------------------------
        # (A) Gather bounding box from picker buttons
        # ----------------------------------------------------------
        buttons_found = False
        min_gx = None
        max_gx = None
        min_gy = None
        max_gy = None

        for child in self.findChildren(picker.PickerButton):
            gx, gy = child.grid_pos
            w_cells, h_cells = child.size_in_cells
            b_minx = gx
            b_maxx = gx + w_cells - 1
            b_miny = gy
            b_maxy = gy + h_cells - 1

            if not buttons_found:
                min_gx, max_gx, min_gy, max_gy = b_minx, b_maxx, b_miny, b_maxy
                buttons_found = True
            else:
                min_gx = min(min_gx, b_minx)
                max_gx = max(max_gx, b_maxx)
                min_gy = min(min_gy, b_miny)
                max_gy = max(max_gy, b_maxy)

        if not buttons_found:
            # If no buttons, define a trivial bounding box so we can still handle the background
            min_gx, max_gx, min_gy, max_gy = 0, 0, 0, 0

        # ----------------------------------------------------------
        # (B) Merge bounding box from the background itself
        # The background is drawn at (bg_offset_gx,bg_offset_gy) with
        # a size of bg_size_in_cells (width, height) in grid coords,
        # centered on that offset.
        # So the half-width = bg_size_in_cells[0]/2, half-height = ...
        # We'll unify that with the existing bounding box.
        # ----------------------------------------------------------
        bg_w_cells = self.bg_size_in_cells[0]
        bg_h_cells = self.bg_size_in_cells[1]

        # The background center is at (bg_offset_gx, bg_offset_gy)
        # so the corners are offset +/- half-size
        bg_min_x = self.bg_offset_gx - (bg_w_cells / 2.0)
        bg_max_x = self.bg_offset_gx + (bg_w_cells / 2.0)
        bg_min_y = self.bg_offset_gy - (bg_h_cells / 2.0)
        bg_max_y = self.bg_offset_gy + (bg_h_cells / 2.0)

        # Merge this with the min/max from the buttons
        if not buttons_found:
            # If there were no buttons at all, or min_gx.. were undefined, just use bg directly
            min_gx, max_gx = bg_min_x, bg_max_x
            min_gy, max_gy = bg_min_y, bg_max_y
        else:
            min_gx = min(min_gx, bg_min_x)
            max_gx = max(max_gx, bg_max_x)
            min_gy = min(min_gy, bg_min_y)
            max_gy = max(max_gy, bg_max_y)

        # If the final bounding box is degenerate (0 or negative size), expand it trivially
        if min_gx == max_gx:
            max_gx = min_gx + 1
        if min_gy == max_gy:
            max_gy = min_gy + 1

        # ----------------------------------------------------------
        # (C) Convert that bounding box to pixel space
        # We'll see how big it is in grid coords
        # (like "grid_bbox_w" = max_gx-min_gx), etc.
        # Then we figure out a cell_size that fits inside the window.
        # ----------------------------------------------------------
        margin_px = 20
        avail_w = self.width() - margin_px
        avail_h = self.height() - margin_px
        if avail_w <= 0 or avail_h <= 0:
            return

        grid_bbox_w = (max_gx - min_gx)
        grid_bbox_h = (max_gy - min_gy)

        # Desired cell size is the ratio of "available px" / "bbox in grid coords"
        desired_cell_size_w = avail_w / grid_bbox_w
        desired_cell_size_h = avail_h / grid_bbox_h
        new_cell_size = min(desired_cell_size_w, desired_cell_size_h)

        # Clip cell size to your min/max
        new_cell_size = max(self.MIN_CELL_SIZE, min(new_cell_size, self.MAX_CELL_SIZE))

        # We'll scale from the old cell_size -> new cell_size
        # But we do *not* update bg_size_in_cells => we preserve user-chosen dimension
        old_cell_size = self.cell_size
        self.cell_size = new_cell_size

        # ----------------------------------------------------------
        # (D) Re-center offset so that the bounding box is in view
        # We'll pick the midpoint of the bounding box and shift it to the widget center.
        # ----------------------------------------------------------
        mid_gx = (min_gx + max_gx) / 2.0
        mid_gy = (min_gy + max_gy) / 2.0

        # Convert that grid center to pixel coords with the new cell_size
        px_mid, py_mid = self.grid_to_pixel(mid_gx, mid_gy)
        desired_cx = self.width() / 2.0
        desired_cy = self.height() / 2.0
        shift_x = desired_cx - px_mid
        shift_y = desired_cy - py_mid

        # Adjust offsets
        self.offset_x += shift_x
        self.offset_y += shift_y

        # ----------------------------------------------------------
        # (E) Reposition buttons so they reflect the new cell_size
        # (and your new offsets)
        # ----------------------------------------------------------
        self.reposition_all_buttons()
        self.update()

    def apply_zoom(self, increment):
        """
        Zoom the grid by 'increment' in cell_size.
        We do NOT change bg_size_in_cells anymore. This keeps
        the background and buttons in sync in animate mode.
        """
        new_cell_size = self.cell_size + increment
        if new_cell_size < self.MIN_CELL_SIZE:
            new_cell_size = self.MIN_CELL_SIZE
        elif new_cell_size > self.MAX_CELL_SIZE:
            new_cell_size = self.MAX_CELL_SIZE

        self.cell_size = new_cell_size

        # Move/resize any buttons in this grid
        self.reposition_all_buttons()

        self.update()


    def grid_to_pixel(self, grid_x, grid_y):
        """Convert grid coordinates to pixel coordinates, accounting for panning and Y-axis inversion."""
        cs = self.adjusted_cell_size
        pixel_x = (grid_x * cs) + (self.width() / 2) + self.offset_x
        pixel_y = (self.height() / 2) - (grid_y * cs) + self.offset_y
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

        logger.info(f"[GridWidget] Received event '{event_type}' from button '{btn_label}', shift={shift_pressed}")
        # Forward the event upwards with the shift boolean
        self.picker_event.emit(event_type, btn, shift_pressed)

    # ------------------------
    #  Mouse Events
    # ------------------------
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            child = self.childAt(event.pos())
            # If click is NOT on a picker button, start marquee selection.
            if not child or not isinstance(child, picker.PickerButton):
                self.rubberBandOrigin = event.pos()
                self.rubberBand.setGeometry(QtCore.QRect(self.rubberBandOrigin, QtCore.QSize()))
                self.rubberBand.show()
                # Clear any previous multi-selection (assume the top-level window has this method)
                top_level = self.window()
                if hasattr(top_level, "clear_multi_select"):
                    top_level.clear_multi_select()
                event.accept()
                return  # Do not process further for this event.
            else:
                # If a picker button is clicked, continue with normal processing.
                super().mousePressEvent(event)
        elif event.button() == QtCore.Qt.MiddleButton:
            self._dragging = True
            self._drag_start = event.pos()
            event.accept()
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
                gx, gy = self.pixel_to_grid(event.pos().x(), event.pos().y())
                self.context_menu.grid_pos = (round(gx), round(gy))
            self.context_menu.exec_(event.globalPos())
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.rubberBand.isVisible():
            rect = QtCore.QRect(self.rubberBandOrigin, event.pos()).normalized()
            self.rubberBand.setGeometry(rect)
            event.accept()
            return
        if self._dragging:
            delta = event.pos() - self._drag_start
            self._drag_start = event.pos()
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.reposition_all_buttons()
            self.update()
            self.grid_panned.emit()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.rubberBand.isVisible():
            selection_rect = self.rubberBand.geometry()
            self.rubberBand.hide()
            # Iterate over all picker buttons in this grid.
            for btn in self.findChildren(picker.PickerButton):
                # btn.geometry() is already in the coordinate system of the grid widget.
                if selection_rect.intersects(btn.geometry()):
                    # In animate mode, only select if command_mode is "Select"
                    if not self.edit_mode and btn.command_mode != "Select":
                        continue
                    # Add the button to the multi-selection.
                    top_level = self.window()
                    if hasattr(top_level, "add_button_to_multi_select"):
                        top_level.add_button_to_multi_select(btn, shift_pressed=True)
                    # We iterate over all selected picker buttons and call their execute_command() method
                    if not self.edit_mode:
                        top_level = self.window()
                        for btn in top_level.selected_picker_buttons:
                            btn.execute_command()
            event.accept()
            return
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
