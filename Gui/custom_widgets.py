# tabs.py
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QColor
import os


class FixedSizeTabBar(QtWidgets.QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)

    def tabSizeHint(self, index):
        """Override tab size to set fixed width and height."""
        return QtCore.QSize(110, 145)  # Set tab width to 100px, extra height for text

    def paintEvent(self, event):
        """Custom paint event to draw the tabs with minimal spacing and stacked icon/text."""
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)

            # Determine if it's the last tab
            last_tab = index == self.count() - 1

            # Define regions for icon and text
            if index == self.count() - 1:  # Last tab is "Add Character"
                # Center the icon vertically and horizontally for this tab
                icon_rect = QtCore.QRect(option.rect.x() + 25, option.rect.y() + 30, 55, 55)  # Center a 50x50 icon
            else:
                icon_rect = QtCore.QRect(option.rect.x(), option.rect.y(), 110, 115)  # Icon for other tabs 110x110

            text_rect = QtCore.QRect(option.rect.x(), option.rect.y() + 115, 110, 30)  # Text below the icon, 30px tall

            # Draw tab background
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, QColor("#646464"))  # Selected tab background
                painter.fillRect(text_rect, QColor("#f9aa26"))
                font = painter.font()
                font.setBold(True)  # Bold font for selected tab
                painter.setFont(font)
            else:
                if last_tab:
                    painter.fillRect(option.rect, QColor("#373737"))  # Default tab background
                else:
                    painter.fillRect(option.rect, QColor("#666666"))  # Default tab background

                painter.fillRect(text_rect, QColor("#373737"))

                font = painter.font()
                font.setBold(True)  # Bold font for selected tab
                painter.setFont(font)

            # Custom border for the "Add Character" tab
            if last_tab:  # Last tab is "Add Character"
                painter.setPen(QColor("#373737"))  # Top border
                painter.drawLine(option.rect.x(), option.rect.y(), option.rect.x() + option.rect.width(),
                                 option.rect.y())

                painter.setPen(QColor("#222222"))  # Left border
                painter.drawLine(option.rect.x(), option.rect.y(), option.rect.x(),
                                 option.rect.y() + option.rect.height())

                painter.setPen(QColor("#373737"))  # Bottom border
                painter.drawLine(option.rect.x(), option.rect.y() + option.rect.height(),
                                 option.rect.x() + option.rect.width(), option.rect.y() + option.rect.height())

                painter.setPen(QColor("#373737"))  # Right border
                painter.drawLine(option.rect.x() + option.rect.width(), option.rect.y(),
                                 option.rect.x() + option.rect.width(), option.rect.y() + option.rect.height())
            else:
                painter.setPen(QColor("#222222"))  # Top border
                painter.drawLine(option.rect.x(), option.rect.y(), option.rect.x() + option.rect.width(),
                                 option.rect.y())

                painter.setPen(QColor("#222222"))  # Left border
                painter.drawLine(option.rect.x(), option.rect.y(), option.rect.x(),
                                 option.rect.y() + option.rect.height())

                painter.setPen(QColor("#222222"))  # Bottom border
                painter.drawLine(option.rect.x(), option.rect.y() + option.rect.height(),
                                 option.rect.x() + option.rect.width(), option.rect.y() + option.rect.height())

                painter.setPen(QColor("#222222"))  # Right border
                painter.drawLine(option.rect.x() + option.rect.width(), option.rect.y(),
                                 option.rect.x() + option.rect.width(), option.rect.y() + option.rect.height())

            # Draw a border between icon and text
            separator_y = option.rect.y() + 115  # Y-coordinate at the top of the text_rect
            painter.drawLine(option.rect.x(), separator_y, option.rect.x() + 115, separator_y)

            # Draw icon and text
            if not option.icon.isNull():
                # Retrieve the pixmap from the QIcon
                pixmap = option.icon.pixmap(QtCore.QSize(110, 115))  # Desired size (width x height)

                # Draw the pixmap using QPainter's drawPixmap
                painter.drawPixmap(icon_rect, pixmap, pixmap.rect())

                # Apply dark overlay on top of the icon if not selected
                if not (option.state & QtWidgets.QStyle.State_Selected) and index != self.count() - 1:
                    painter.fillRect(icon_rect, QColor(0, 0, 0, 150))  # Semi-transparent black overlay on icon

            # Keep text aligned and consistent
            painter.setPen(QColor("white") if option.state & QtWidgets.QStyle.State_Selected else QColor("#A0A0A0"))
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, option.text)


class CollapsibleBox(QtWidgets.QWidget):
    toggled = QtCore.Signal(bool)  # Signal emitted when the box is toggled (open/close)

    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)
        self.is_open = False
        self.init_ui(title)

    def init_ui(self, title):
        # Create toggle button
        self.toggle_button = QtWidgets.QToolButton(text=title)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(self.is_open)
        self.toggle_button.clicked.connect(self.on_toggle)

        # Content container with a border
        self.content_widget = QtWidgets.QFrame()
        self.content_widget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)  # Add padding
        self.content_layout.setSpacing(10)  # Add spacing
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.setVisible(False)  # Initially collapsed

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_widget)

    def setContentLayout(self, layout):
        """Sets the content layout for the collapsible box."""
        # Clear existing layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.content_layout.addLayout(layout)

    def on_toggle(self):
        self.is_open = not self.is_open
        self.toggle_button.setArrowType(QtCore.Qt.DownArrow if self.is_open else QtCore.Qt.RightArrow)
        self.content_widget.setVisible(self.is_open)
        self.toggled.emit(self.is_open)
        self.content_widget.setVisible(self.is_open)
