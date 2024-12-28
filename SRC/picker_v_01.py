from PySide2 import QtWidgets, QtCore, QtGui


class GridContainer(QtWidgets.QWidget):
    """A container widget that paints the grid lines and holds the buttons."""

    def __init__(self, rows, cols, cell_size=40, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.setMinimumSize(1, 1)  # Just a small initial size

    def set_cell_size(self, cell_size):
        self.cell_size = cell_size
        # Update the fixed size based on new cell size
        self.setFixedSize(round(self.cols * self.cell_size), round(self.rows * self.cell_size))
        self.update()

    def paintEvent(self, event):
        """Draw gridlines to visually represent cells."""
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(200, 200, 200, 100))
        pen.setWidth(1)
        painter.setPen(pen)

        # Draw vertical lines
        for col in range(self.cols + 1):
            x = round(col * self.cell_size)
            painter.drawLine(x, 0, x, round(self.rows * self.cell_size))

        # Draw horizontal lines
        for row in range(self.rows + 1):
            y = round(row * self.cell_size)
            painter.drawLine(0, y, round(self.cols * self.cell_size), y)

        painter.end()


class PickerPage(QtWidgets.QWidget):
    """Page with a dynamic grid layout and proportional scaling."""

    def __init__(self, rows=20, cols=10, parent=None):
        super().__init__(parent)
        # Ensure rows and cols are never zero
        self.rows = max(rows, 1)
        self.cols = max(cols, 1)
        self.cell_size = 40  # Initial cell size (square)

        # Main layout to manage spacing and centering
        self.outer_layout = QtWidgets.QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)

        # Horizontal layout for centering the grid
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.outer_layout.addStretch()
        self.outer_layout.addLayout(self.horizontal_layout)
        self.outer_layout.addStretch()

        # The actual grid container that draws lines and holds buttons
        self.grid_container = GridContainer(self.rows, self.cols, self.cell_size, self)
        self.horizontal_layout.addStretch()
        self.horizontal_layout.addWidget(self.grid_container)
        self.horizontal_layout.addStretch()

        # Store buttons and their grid data
        self.buttons = []

    def resizeEvent(self, event):
        available_width = self.width()
        available_height = self.height()

        # Safeguard against division by zero
        if available_width == 0:
            available_width = 1
        if available_height == 0:
            available_height = 1

        # Ensure rows and cols are never zero
        if self.rows <= 0:
            self.rows = 1
        if self.cols <= 0:
            self.cols = 1

        # Maintain a 2:1 aspect ratio for the grid
        if (available_width / available_height) < (self.cols / self.rows):
            self.cell_size = available_width / self.cols
        else:
            self.cell_size = available_height / self.rows

        # Ensure cell_size is not zero
        if self.cell_size == 0:
            self.cell_size = 1

        # Update grid container size
        self.grid_container.set_cell_size(self.cell_size)

        # Resize and reposition buttons
        for button, (grid_x, grid_y, width, height) in self.buttons:
            button.setFixedSize(round(width * self.cell_size), round(height * self.cell_size))
            button.move(round(grid_x * self.cell_size), round(grid_y * self.cell_size))

        self.update()

    def add_button(self, label, grid_x, grid_y, width, height):
        """Add a button to the grid."""
        button = GridButton(label, self.grid_container)
        button.setFixedSize(width * self.cell_size, height * self.cell_size)
        button.move(grid_x * self.cell_size, grid_y * self.cell_size)
        button.show()
        self.buttons.append((button, (grid_x, grid_y, width, height)))

    def update_button_position(self, button, grid_x, grid_y):
        """Update the grid position of a button."""
        for i, (b, (old_x, old_y, width, height)) in enumerate(self.buttons):
            if b == button:
                self.buttons[i] = (button, (grid_x, grid_y, width, height))
                break

    def create_button(self, position):
        """Create a new button with a dialog."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add Button")

        layout = QtWidgets.QVBoxLayout(dialog)

        # Button label input
        label_layout = QtWidgets.QHBoxLayout()
        label_layout.addWidget(QtWidgets.QLabel("Button Label:"))
        label_input = QtWidgets.QLineEdit()
        label_layout.addWidget(label_input)
        layout.addLayout(label_layout)

        # Width input
        width_layout = QtWidgets.QHBoxLayout()
        width_layout.addWidget(QtWidgets.QLabel("Width (grid cells):"))
        width_input = QtWidgets.QSpinBox()
        width_input.setMinimum(1)
        width_input.setMaximum(self.cols)
        width_layout.addWidget(width_input)
        layout.addLayout(width_layout)

        # Height input
        height_layout = QtWidgets.QHBoxLayout()
        height_layout.addWidget(QtWidgets.QLabel("Height (grid cells):"))
        height_input = QtWidgets.QSpinBox()
        height_input.setMinimum(1)
        height_input.setMaximum(self.rows)
        height_layout.addWidget(height_input)
        layout.addLayout(height_layout)

        # Dialog buttons
        button_layout = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton("OK")
        cancel_button = QtWidgets.QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            label = label_input.text()
            width = width_input.value()
            height = height_input.value()

            if label:
                grid_x = int(position.x() // self.cell_size)
                grid_y = int(position.y() // self.cell_size)
                self.add_button(label, grid_x, grid_y, width, height)

    def show_context_menu(self, position):
        """Show context menu."""
        menu = QtWidgets.QMenu(self)
        create_button_action = menu.addAction("Add Button")
        add_page_action = menu.addAction("Add Page")

        action = menu.exec_(self.mapToGlobal(position))
        if action == create_button_action:
            self.create_button(position)
        elif action == add_page_action:
            main_window = self.window()
            if isinstance(main_window, QtWidgets.QMainWindow):
                main_window.add_page_to_current()


class GridButton(QtWidgets.QPushButton):
    """Custom button for grid layouts."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.dragging = False
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.pos() - self.start_pos
            new_x = self.x() + delta.x()
            new_y = self.y() + delta.y()

            parent = self.parentWidget()
            if isinstance(parent, GridContainer):
                cell_size = parent.cell_size
                # Limit snapping within the grid_container boundaries
                snapped_x = max(0, min(round(new_x / cell_size) * round(cell_size),
                                       parent.width() - self.width()))
                snapped_y = max(0, min(round(new_y / cell_size) * round(cell_size),
                                       parent.height() - self.height()))
                self.move(snapped_x, snapped_y)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            # Update button's grid position
            page = self.parentWidget().parentWidget()
            if isinstance(page, PickerPage):
                cell_size = page.cell_size
                grid_x = self.x() // cell_size
                grid_y = self.y() // cell_size
                page.update_button_position(self, grid_x, grid_y)
