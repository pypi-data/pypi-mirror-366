import argparse
import os
import pathlib
import shutil
import sys
import threading
import time
from typing import List, Optional, Tuple
from bisect import bisect

from PIL.ImageQt import toqpixmap
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
)

from photo_culling.caching import ImageCache
from photo_culling.utils import clip, get_subimage, get_image_fnames
from photo_culling.widgets import ImageIndexLabel, show_no_target_dir_dialog


class ImageViewer(QMainWindow):
    """A fast image viewer for culling photos with keyboard shortcuts and mouse controls."""

    def __init__(
        self,
        image_directory: str | pathlib.Path,
        target_directory: Optional[str | pathlib.Path],
        windowed: bool = False,
        default_select: bool = False,
    ) -> None:
        """Initialize the image viewer.

        Args:
            image_directory: Directory containing the images to view
            target_directory: Directory where selected images will be copied
            windowed: Whether to open in maximized window instead of full screen
            default_select: Whether to initially mark all photos as selected
        """
        super().__init__()
        self._setup_image_data(image_directory, target_directory, default_select)
        self._setup_ui(windowed)
        self._start_cache_thread()
        self.show_image()

    def _setup_image_data(
        self, image_directory: str | pathlib.Path, target_directory: Optional[str | pathlib.Path], default_select: bool
    ) -> None:
        """Set up image data and cache."""
        self.image_directory = pathlib.Path(image_directory)
        self.target_directory = pathlib.Path(target_directory) if target_directory else None
        self.image_fnames = get_image_fnames(self.image_directory)
        self.n_images = len(self.image_fnames)
        self.image_cache = ImageCache(self.image_fnames)
        self.is_selected = [default_select] * self.n_images
        self.current_index = 0
        self.exiting = False
        self.only_show_selected = False

    def _setup_ui(self, windowed: bool) -> None:
        """Set up the user interface."""
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image_label)

        self.pos_label = ImageIndexLabel(self, self.n_images)
        self.update_pos_label()

        self.setWindowTitle("Fast culling")
        screen_size = QApplication.primaryScreen().size()
        self.setGeometry(QRect(0, 0, screen_size.width() - 25, screen_size.height() - 100))
        if windowed:
            self.showNormal()
        else:
            self.showFullScreen()

    def _start_cache_thread(self) -> None:
        """Start the background thread for populating the image cache."""
        self.populate_cache_thread = threading.Thread(target=self._populate_cache)
        self.populate_cache_thread.start()

    def update_pos_label(self) -> None:
        """Update the position label with current image index and selection status."""
        self.pos_label.set_values(self.current_index, self.current_selected, self.n_selected)

    def get_target_dir(self) -> Optional[str]:
        """Get the target directory for copying selected images."""
        directory = str(QFileDialog.getExistingDirectory(self, "Select target directory", str(self.target_directory)))
        return directory if directory else None

    def _populate_cache(self) -> None:
        """Background thread to populate the image cache."""
        while not self.exiting:
            self.image_cache.load_next_required_item(self.current_index, self.get_current_resolution())
            self.image_cache.clean_cache(self.current_index, self.get_current_resolution())
            time.sleep(0.001)  # short sleep to reduce thread starvation and cpu load

    def show_image(self) -> None:
        """Display the current image."""
        preview = self.image_cache.get_preview(self.current_index, self.get_current_resolution())
        qpm = toqpixmap(preview)
        self.image_label.setPixmap(qpm)

    def navigate(self, step):
        if self.only_show_selected:
            selected_indices = [i for i, selected in enumerate(self.is_selected) if selected]
            if len(selected_indices) == 0:
                print("No selected images to navigate.")
                return
            idx_current = bisect(selected_indices, self.current_index) - 1
            idx_new = clip(idx_current + step, 0, len(selected_indices))
            self.current_index = selected_indices[idx_new]
        else:
            self.current_index = clip(self.current_index + step, 0, self.n_images)
        self.show_image()
        self.update_pos_label()

    def get_current_resolution(self) -> Tuple[int, int]:
        """Get the current window resolution."""
        s = self.image_label.size()
        return s.width(), s.height()

    def copy_selected_images(self, target_dir: str | pathlib.Path) -> None:
        """Copy selected images and related files to the target directory.

        Args:
            target_dir: Directory to copy selected images to
        """
        os.makedirs(target_dir, exist_ok=True)
        n_files_total = 0
        n_unique_photos = 0
        for selected, fname in zip(self.is_selected, self.image_fnames):
            if not selected:
                continue
            related_files = self.image_directory.glob(f"{fname.stem}.*")
            for f in related_files:
                shutil.copy(f, target_dir)
                n_files_total += 1
            n_unique_photos += 1
        print(f"Copied {n_unique_photos} photos, {n_files_total} files in total.")

    @property
    def n_selected(self) -> int:
        return sum(self.is_selected)

    @property
    def current_selected(self) -> bool:
        """Get whether the current image is selected."""
        return self.is_selected[self.current_index]

    def keyPressEvent(self, event: Optional[QKeyEvent] = None) -> None:
        if event is None:
            return
        key = event.key()

        if key in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.exit_viewer()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            step = 10 if (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier) else 1
            self.navigate(-step)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            step = 10 if (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier) else 1
            self.navigate(step)
        elif key == Qt.Key.Key_F11:
            self.toggle_full_screen()
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            self.set_selected(True)
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            self.set_selected(False)
        elif key == Qt.Key.Key_T:
            self.only_show_selected = not self.only_show_selected

    def exit_viewer(self) -> None:
        """Handle the escape key press."""
        if self.n_selected:
            target_dir = self.get_target_dir()
            while not target_dir:
                response = show_no_target_dir_dialog(self)
                if response == 0:
                    # Exit without copying
                    break
                elif response == 1:
                    # Continue culling
                    return
                elif response == 2:
                    # Select target directory again
                    target_dir = self.get_target_dir()
                    continue
            if target_dir:
                self.copy_selected_images(target_dir)
        self.exiting = True
        self.populate_cache_thread.join()
        self.close()

    def set_selected(self, selected: bool) -> None:
        self.is_selected[self.current_index] = selected
        self.update_pos_label()

    def to_fractional(self, pos: QPoint) -> Tuple[float, float]:
        """Convert pixel position to fractional coordinates.

        Args:
            pos: Pixel position to convert

        Returns:
            Tuple of (x, y) coordinates as fractions of window size
        """
        width, height = self.get_current_resolution()
        return pos.x() / width, pos.y() / height

    def mouseMoveEvent(self, event: Optional[QMouseEvent] = None) -> None:
        if event is None:
            return
        self.show_zoomed_image(*self.to_fractional(event.pos()))

    def mousePressEvent(self, event: Optional[QMouseEvent] = None) -> None:
        if event is None:
            return
        self.show_zoomed_image(*self.to_fractional(event.pos()))

    def mouseReleaseEvent(self, event: Optional[QMouseEvent] = None) -> None:
        if event is None:
            return
        self.show_image()

    def show_zoomed_image(self, frac_x: float, frac_y: float) -> None:
        """Show a zoomed portion of the current image.

        Args:
            frac_x: X coordinate as fraction of window width
            frac_y: Y coordinate as fraction of window height
        """
        sub_img = get_subimage(
            self.image_cache.get_full_image(self.current_index), (frac_x, frac_y), self.get_current_resolution()
        )
        qpm = toqpixmap(sub_img)
        self.image_label.setPixmap(qpm)

    def resizeEvent(self, event: Optional[QResizeEvent] = None) -> None:
        if event is None:
            return
        self.show_image()

    def toggle_full_screen(self) -> None:
        """Toggle between full screen and windowed mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


def main():
    parser = argparse.ArgumentParser(
        description="Photo Culling Tool: Navigate with left/right or A/D. Select images with up/down or W/S. Go only through selected images with T. Toggle fullscreen with F11. Quit with ESC."
    )
    parser.add_argument("directory", nargs="?", default=".")
    parser.add_argument("--target", default=None)
    parser.add_argument("--windowed", action="store_true", help="Open in maximized window instead of full screen")
    parser.add_argument(
        "--default-select", action="store_true", help="Initially mark all photos as selected (vs default unselected)"
    )
    args = parser.parse_args()
    directory = pathlib.Path(args.directory).resolve()
    if not directory.is_dir():
        print(f"Not a valid directory: {args.directory}")
    elif not get_image_fnames(directory):
        print(f"No jpg/jpeg files found in {args.directory}")
    else:
        app = QApplication(sys.argv)
        viewer = ImageViewer(directory, args.target, args.windowed, args.default_select)
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
