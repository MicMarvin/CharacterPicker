from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIcon, QColor
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import os
import random

ICON = os.environ["RIGGING_TOOL_ROOT"] + "/CharacterPicker/Icons/"


def maya_main_window():
    """Return Maya's main window widget."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def get_random_icon():
    """Randomly select either 'unknownMan.svg' or 'unknownWoman.svg' and return the full path."""
    icons = ["unknownMan.svg", "unknownWoman.svg"]
    return os.path.join(ICON, random.choice(icons))


class FixedSizeTabBar(QtWidgets.QTabBar):
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
            else:
                painter.fillRect(option.rect, QColor("#373737"))  # Default tab background
                painter.fillRect(text_rect, QColor("#373737"))

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


class TabInterfaceExample(QtWidgets.QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        self.setWindowTitle("Tab Interface Example")
        self.resize(600, 800)

        # Main layout
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        # Create a QTabWidget with a custom TabBar
        self.tab_widget = QtWidgets.QTabWidget()
        tab_bar = FixedSizeTabBar()
        self.tab_widget.setTabBar(tab_bar)  # Use the fixed-size tab bar

        main_layout.addWidget(self.tab_widget)

        # Add sample tabs
        self.add_tab("new character", "Welcome to Tab 1", get_random_icon())

        # Add the 'Add New Tab' tab
        self.add_character_tab()

        # Add dynamic tab buttons
        button_layout = QtWidgets.QHBoxLayout()

        add_tab_button = QtWidgets.QPushButton("Add New Tab")
        add_tab_button.clicked.connect(self.add_new_tab)
        button_layout.addWidget(add_tab_button)

        remove_tab_button = QtWidgets.QPushButton("Remove Current Tab")
        remove_tab_button.clicked.connect(self.remove_current_tab)
        button_layout.addWidget(remove_tab_button)

        main_layout.addLayout(button_layout)

    def add_tab(self, tab_name, content, icon_path=None):
        """Add a new tab with an optional icon that fills the tab."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        label = QtWidgets.QLabel(content)
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # Set the icon to fill the tab
        if icon_path:
            icon = QIcon(icon_path)
            self.tab_widget.setIconSize(QtCore.QSize(110, 110))  # Icon size to match tab width
            self.tab_widget.addTab(tab, icon, tab_name)
        else:
            self.tab_widget.addTab(tab, tab_name)

    def add_new_tab(self):
        """Dynamically add a new tab with placeholder content."""
        tab_count = self.tab_widget.count()  # Count includes the 'Add New Tab' button tab
        tab_name = f"Tab {tab_count}"
        content = f"This is dynamically added {tab_name}"

        # Remove the 'Add New Tab' tab before adding a new one
        self.tab_widget.removeTab(self.tab_widget.count() - 1)
        self.add_tab(tab_name, content, get_random_icon())

        # Re-add the 'Add New Tab' tab
        self.add_character_tab()

        # Select the newly added tab
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 2)

    def add_character_tab(self):
        """Add a special tab that functions as a button to add new tabs."""
        add_tab_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(add_tab_widget)
        label = QtWidgets.QLabel("NEW")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        icon_path = os.path.join(ICON, "plus.svg")
        icon = QIcon(icon_path)
        self.tab_widget.setIconSize(QtCore.QSize(50, 50))  # Icon size to match tab width
        self.tab_widget.addTab(add_tab_widget, QIcon(icon), "NEW")

        # Connect tabBarClicked signal to custom click handler
        self.tab_widget.tabBar().tabBarClicked.connect(self.on_tab_bar_clicked)

    def on_tab_bar_clicked(self, index):
        """Handle clicks on the 'Add Character' tab."""
        if index == self.tab_widget.count() - 1:  # Check if 'Add Character' tab was clicked
            self.add_new_tab()

    def remove_current_tab(self):
        """Remove the currently selected tab, except the 'Add New Tab' tab."""
        current_index = self.tab_widget.currentIndex()

        # Prevent removing the 'Add New Tab' tab
        if current_index != -1 and current_index != self.tab_widget.count() - 1:
            self.tab_widget.removeTab(current_index)


def show_tab_interface():
    """Display the Tab Interface tool inside Maya's main window."""
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, TabInterfaceExample):
            widget.close()

    tab_interface = TabInterfaceExample()
    tab_interface.setWindowFlags(QtCore.Qt.Window)
    tab_interface.show()


# Show the tool
show_tab_interface()
