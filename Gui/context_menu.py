# context_menu.py
from PySide2 import QtWidgets, QtCore


class ContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Reference to the main window

        # Define all possible actions
        self.change_background_action = QtWidgets.QAction("Change Background", self)
        self.change_picture_action = QtWidgets.QAction("Change Picture", self)
        self.add_button_action = QtWidgets.QAction("Add Button", self)
        self.delete_button_action = QtWidgets.QAction("Delete Button", self)
        self.add_tab_action = QtWidgets.QAction("Add Tab", self)
        self.rename_tab_action = QtWidgets.QAction("Rename Tab", self)
        self.close_tab_action = QtWidgets.QAction("Close Tab", self)
        self.add_page_action = QtWidgets.QAction("Add Page", self)
        self.rename_page_action = QtWidgets.QAction("Rename Page", self)
        self.remove_page_action = QtWidgets.QAction("Delete Page", self)
        self.current_mode_action = QtWidgets.QAction("Animate Mode", self)

        # Define separators
        self.separator1 = QtWidgets.QAction(self)
        self.separator1.setSeparator(True)
        self.separator2 = QtWidgets.QAction(self)
        self.separator2.setSeparator(True)

        # Add all actions to the menu initially (hidden by default)
        self.addAction(self.change_background_action)
        self.addAction(self.change_picture_action)
        self.addAction(self.separator2)
        self.addAction(self.add_button_action)
        self.addAction(self.delete_button_action)
        self.addAction(self.add_tab_action)
        self.addAction(self.rename_tab_action)
        self.addAction(self.close_tab_action)
        self.addAction(self.add_page_action)
        self.addAction(self.rename_page_action)
        self.addAction(self.remove_page_action)
        self.addAction(self.separator1)
        self.addAction(self.current_mode_action)


    def set_context_type(self, context_type):
        """
        Set the context type and update action visibility dynamically.
        :param context_type: The context type ('grid', 'tab_bar', 'page_buttons', 'tool_box').
        """
        # Hide all actions by default
        for action in self.actions():
            action.setVisible(False)

        # Enable relevant actions based on the context
        if context_type == 'grid':
            self.change_background_action.setVisible(True)
            self.change_background_action.setEnabled(self.parent_window.edit_mode)
            self.separator2.setVisible(True)
            self.add_button_action.setVisible(True)
            self.add_button_action.setEnabled(self.parent_window.edit_mode)
            self.delete_button_action.setVisible(True)
            self.delete_button_action.setEnabled(self.parent_window.edit_mode)
            self.separator1.setVisible(True)
            self.current_mode_action.setVisible(True)
        elif context_type == 'tab_bar':
            self.change_picture_action.setVisible(True)
            self.change_picture_action.setEnabled(self.parent_window.edit_mode)
            self.separator2.setVisible(True)
            self.add_tab_action.setVisible(True)
            self.add_tab_action.setEnabled(self.parent_window.edit_mode)
            self.rename_tab_action.setVisible(True)
            self.rename_tab_action.setEnabled(self.parent_window.edit_mode)
            self.close_tab_action.setVisible(True)
            self.close_tab_action.setEnabled(self.parent_window.edit_mode)
            self.separator1.setVisible(True)
            self.current_mode_action.setVisible(True)
        elif context_type == 'page_buttons':
            self.change_background_action.setVisible(True)
            self.change_background_action.setEnabled(self.parent_window.edit_mode)
            self.separator2.setVisible(True)
            self.add_page_action.setVisible(True)
            self.add_page_action.setEnabled(self.parent_window.edit_mode)
            self.rename_page_action.setVisible(True)
            self.rename_page_action.setEnabled(self.parent_window.edit_mode)
            self.remove_page_action.setVisible(True)
            self.remove_page_action.setEnabled(self.parent_window.edit_mode)
            self.separator1.setVisible(True)
            self.current_mode_action.setVisible(True)
        elif context_type == 'tool_box':
            self.current_mode_action.setVisible(True)
            self.current_mode_action.setEnabled(True)

        # Update current_mode_action text
        self.current_mode_action.setText(
            "Switch to Animate Mode" if self.parent_window.edit_mode else "Switch to Edit Mode"
        )


