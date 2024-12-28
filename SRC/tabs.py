# tabs.py
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QColor, QIcon
import os
import random


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

            # Define regions for icon and text
            if index == self.count() - 1:  # Last tab is "Add Character"
                # Center the icon vertically and horizontally for this tab
                icon_rect = QtCore.QRect(option.rect.x() + 25, option.rect.y() + 30, 55, 55)  # Center a 50x50 icon
            else:
                icon_rect = QtCore.QRect(option.rect.x(), option.rect.y() + 5, 110, 110)  # Icon for other tabs 110x110

            text_rect = QtCore.QRect(option.rect.x(), option.rect.y() + 115, 110, 30)  # Text below the icon, 30px tall

            # Draw tab background
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, QColor("#646464"))  # Selected tab background
                painter.fillRect(text_rect, QColor("#f9aa26"))
                font = painter.font()
                font.setBold(True)  # Bold font for selected tab
                painter.setFont(font)
            else:
                painter.fillRect(option.rect, QColor("#373737"))  # Default tab background
                painter.fillRect(text_rect, QColor("#373737"))
                font = painter.font()
                font.setBold(True)  # Bold font for selected tab
                painter.setFont(font)

            # Custom border for the "Add Character" tab
            if index == self.count() - 1:  # Last tab is "Add Character"
                painter.setPen(QColor("#373737"))  # Top border
                painter.drawLine(option.rect.x(), option.rect.y(), option.rect.x() + option.rect.width(),
                                 option.rect.y())

                painter.setPen(QColor("#2D2D2D"))  # Left border
                painter.drawLine(option.rect.x(), option.rect.y(), option.rect.x(),
                                 option.rect.y() + option.rect.height())

                painter.setPen(QColor("#373737"))  # Bottom border
                painter.drawLine(option.rect.x(), option.rect.y() + option.rect.height(),
                                 option.rect.x() + option.rect.width(), option.rect.y() + option.rect.height())

                painter.setPen(QColor("#373737"))  # Right border
                painter.drawLine(option.rect.x() + option.rect.width(), option.rect.y(),
                                 option.rect.x() + option.rect.width(), option.rect.y() + option.rect.height())
            else:
                # Draw a black border around other tabs
                painter.setPen(QColor("#2D2D2D"))
                painter.drawRect(option.rect)

            # Draw a border between icon and text
            separator_y = option.rect.y() + 115  # Y-coordinate at the top of the text_rect
            painter.drawLine(option.rect.x(), separator_y, option.rect.x() + 110, separator_y)

            # Draw icon and text
            if not option.icon.isNull():
                option.icon.paint(painter, icon_rect, QtCore.Qt.AlignCenter)

            # Keep text aligned and consistent
            painter.setPen(QColor("white") if option.state & QtWidgets.QStyle.State_Selected else QColor("#A0A0A0"))
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, option.text)

    def setCloseButton(self):
        """Place the close button in the top-right corner."""
        for index in range(self.count()):
            close_button = self.tabButton(index, QtWidgets.QTabBar.RightSide)
            if close_button:
                close_button.setStyleSheet("""
                    QPushButton {
                        margin: 0;
                        padding: 0;
                        position: absolute;
                        top: 2px;
                        right: 2px;
                        image: url('close-icon.png');
                    }
                    QPushButton:hover {
                        image: url('close-icon-hover.png');
                    }
                """)


def get_random_icon(icon_dir):
    """Return a random icon path."""
    icons = ["unknownMan.svg", "unknownWoman.svg"]
    return os.path.join(icon_dir, random.choice(icons))
