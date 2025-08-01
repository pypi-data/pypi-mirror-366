from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QPushButton


class ImageIndexLabel(QLabel):
    def __init__(self, parent, n_images, fontsize=25):
        super().__init__(parent)
        self.n_images = n_images
        self.colors = {False: "lightgray", True: "green"}
        self.style_template = f"font-size: {fontsize}px;" + "background-color: {color}"
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.set_values(0, False, 0)

    def _set_selected(self, selected):
        self.setStyleSheet(self.style_template.format(color=self.colors[selected]))

    def _set_index(self, idx: int, n_selected: int):
        self.setText(f"{idx + 1}/{self.n_images} ({n_selected})")
        self.adjustSize()

    def set_values(self, idx: int, current_selected: bool, n_selected: int):
        self._set_selected(current_selected)
        self._set_index(idx, n_selected)


def show_no_target_dir_dialog(parent) -> int:
    """Show a dialog box when no target directory is selected.

    Returns:
        int: 0 for exit without copying, 1 for continue culling, 2 for select target directory
    """

    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("No Target Directory Selected")
    msg_box.setText("You have not selected a target directory")
    msg_box.setInformativeText("Do you want to exit without copying?")

    # Create custom buttons
    exit_button = QPushButton("Yes, exit without copying")
    continue_button = QPushButton("No, continue culling")
    select_button = QPushButton("Select Target Directory")

    msg_box.addButton(exit_button, QMessageBox.ButtonRole.YesRole)
    msg_box.addButton(continue_button, QMessageBox.ButtonRole.NoRole)
    msg_box.addButton(select_button, QMessageBox.ButtonRole.ActionRole)

    # Show the dialog and handle the response
    response = msg_box.exec()  # for some reason this is 2, 3, or 4
    return response - 2
