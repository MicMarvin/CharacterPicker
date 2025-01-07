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
    toggled = QtCore.Signal(bool, int)  # Emit open/close state and height change

    def __init__(self, title="", parent=None, use_custom_icons=False):
        super(CollapsibleBox, self).__init__(parent)
        self.is_open = False
        self.use_custom_icons = use_custom_icons  # Custom icons toggle
        self.init_ui(title)
        self.update_font_color()  # Ensure initial font color matches state

    def init_ui(self, title):
        # Toggle button
        self.toggle_button = QtWidgets.QToolButton()
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(self.is_open)
        self.toggle_button.setText(title)
        self.toggle_button.clicked.connect(self.on_toggle)

        # Set initial icon
        self.update_icon()

        # Content area
        self.content_widget = QtWidgets.QFrame()
        self.content_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.setVisible(False)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_widget)

    def setContentLayout(self, layout):
        """Set the layout for the content area."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.content_layout.addLayout(layout)

    def on_toggle(self):
        self.is_open = not self.is_open
        self.update_icon()

        # Calculate the height change
        if self.is_open:
            height_change = self.content_widget.sizeHint().height()
        else:
            height_change = -self.content_widget.sizeHint().height()

        # Update the content visibility
        self.content_widget.setVisible(self.is_open)

        # Update the font color
        self.update_font_color()

        # Emit the toggled signal with the height change
        self.toggled.emit(self.is_open, abs(height_change))

        # Prevent resizing sibling widgets
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.updateGeometry()

    def update_font_color(self):
        """Update the font color based on the open/closed state."""
        if self.use_custom_icons:
            open_color = "#f9aa26"  # White for open
            closed_color = "#a2a2a2"  # Grey for closed
            font_color = open_color if self.is_open else closed_color
            self.toggle_button.setStyleSheet(f"""
                QToolButton {{
                    color: {font_color};
                    border: none;
                }}
            """)

    def update_icon(self):
        """Update the icon based on the toggle state."""
        if self.use_custom_icons:
            self.toggle_button.setIcon(QtGui.QIcon(":checkboxOn.png" if self.is_open else ":checkboxOff.png"))
        else:
            self.toggle_button.setArrowType(QtCore.Qt.DownArrow if self.is_open else QtCore.Qt.RightArrow)

    def close_silently(self):
        """Close this collapsible section without emitting toggled."""
        if self.is_open:
            self.is_open = False
            self.toggle_button.setChecked(False)
            self.content_widget.setVisible(False)

        self.update_icon()
