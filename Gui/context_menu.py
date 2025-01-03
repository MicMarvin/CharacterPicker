# context_menu.py
from PySide2 import QtWidgets, QtCore


class ContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Store a reference to the main window for actions

        # Explicitly create and add actions
        self.add_button_action = QtWidgets.QAction("Add Button", self)
        self.addAction(self.add_button_action)

        self.delete_button_action = QtWidgets.QAction("Delete Button", self)
        self.addAction(self.delete_button_action)

        # Separator for future options
        self.addSeparator()

        # Connect actions to methods
        self.add_button_action.triggered.connect(self.add_button)
        self.delete_button_action.triggered.connect(self.delete_button)

    def show_context_menu(self, global_position, selected_button=None):
        """
        Show context menu based on the current selection.
        :param global_position: Global position of the right-click event.
        :param selected_button: The currently selected picker button, if any.
        """
        # Update the enabled state of actions
        self.delete_button_action.setEnabled(selected_button is not None)

        # Show the menu at the provided global position
        self.exec_(global_position)

    def add_button(self):
        """Logic to invoke the 'Add Button' workflow."""
        if hasattr(self.parent_window, 'edit_box'):
            self.parent_window.edit_box.submit_picker()  # Trigger the add button logic in the ToolBox

    def delete_button(self):
        """Logic to delete the selected button."""
        if hasattr(self.parent_window, 'delete_selected_picker_button'):
            self.parent_window.delete_selected_picker_button()
