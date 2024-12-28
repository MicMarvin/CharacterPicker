# context_menu.py
from PySide2 import QtWidgets


class ContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(ContextMenu, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.addAction("Add Button", self.add_button)
        self.addAction("Delete Button", self.delete_button)

    def add_button(self):
        # Logic to add a button
        pass

    def delete_button(self):
        # Logic to delete a button
        pass

    def show_context_menu(self, position):
        """Show context menu for adding buttons or pages."""
        menu = QtWidgets.QMenu(self)
        create_button_action = menu.addAction("Add Button")
        add_page_action = menu.addAction("Add Page")

        action = menu.exec_(self.mapToGlobal(position))
        if action == create_button_action:
            self.create_button(position)
        elif action == add_page_action:
            main_window = self.window()
            if isinstance(main_window, CharacterPicker):
                main_window.add_page_to_current()
