import os
import json

# pip install PyQt5
# pip install pillow

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QListWidget,
    QLineEdit,
)
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt
from PIL import Image


class ImageResizerApp(QWidget):
    CONFIG_FILE = "config.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resizer - Drag & Drop or Browse")
        self.setGeometry(100, 100, 650, 550)
        self.setAcceptDrops(True)

        # Instance attributes
        self.output_folder = self.load_config()
        self.target_size = (1200, 628)
        self.dragged_files = []

        # Overall style
        self.setStyleSheet(
            "background-color: #2e2e2e; color: white; border-radius: 10px;"
            "font-size: 16px; font-family: Arial, sans-serif;"
        )

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_ui()

    def init_ui(self):
        # Title
        title_label = QLabel("Image Resizer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin-bottom: 10px;"
        )
        self.layout.addWidget(title_label)

        # Drag & drop hint
        hint_label = QLabel("Drag and Drop Image Files Here, or Use 'Browse Images'")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("margin-bottom: 10px;")
        self.layout.addWidget(hint_label)

        # File list
        self.file_list = QListWidget()
        self.file_list.setStyleSheet(
            "background-color: #3e3e3e; color: white; border-radius: 5px;"
            "font-size: 12px; padding: 5px;"
        )
        self.layout.addWidget(self.file_list)

        # Status label
        self.status_label = QLabel("Waiting for images...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")
        self.layout.addWidget(self.status_label)

        # Browse button
        browse_button = QPushButton("Browse Images")
        browse_button.setStyleSheet(
            "background-color: #6c757d; color: white; border-radius: 5px;"
            "font-size: 16px; padding: 10px;"
            "outline: none;"
        )
        browse_button.clicked.connect(self.browse_images)
        self.layout.addWidget(browse_button)

        # Preset size buttons
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)

        btn_1200x628 = QPushButton("Resize to 1200 x 628")
        btn_1200x628.setStyleSheet(
            "background-color: #4CAF50; color: white; border-radius: 5px;"
            "font-size: 16px; padding: 10px;"
            "outline: none;"
        )
        btn_1200x628.clicked.connect(lambda: self.set_size(1200, 628))
        button_layout.addWidget(btn_1200x628)

        btn_640x420 = QPushButton("Resize to 640 x 420")
        btn_640x420.setStyleSheet(
            "background-color: #008CBA; color: white; border-radius: 5px;"
            "font-size: 16px; padding: 10px;"
            "outline: none;"
        )
        btn_640x420.clicked.connect(lambda: self.set_size(640, 420))
        button_layout.addWidget(btn_640x420)

        # Custom size inputs
        custom_size_layout = QHBoxLayout()
        self.layout.addLayout(custom_size_layout)

        self.width_entry = QLineEdit()
        self.width_entry.setPlaceholderText("Width")
        self.width_entry.setAlignment(Qt.AlignCenter)
        self.width_entry.setStyleSheet(
            "background-color: #3e3e3e; color: white; border-radius: 5px;"
            "font-size: 16px; padding: 5px;"
        )
        custom_size_layout.addWidget(self.width_entry)

        self.height_entry = QLineEdit()
        self.height_entry.setPlaceholderText("Height")
        self.height_entry.setAlignment(Qt.AlignCenter)
        self.height_entry.setStyleSheet(
            "background-color: #3e3e3e; color: white; border-radius: 5px;"
            "font-size: 16px; padding: 5px;"
        )
        custom_size_layout.addWidget(self.height_entry)

        # Custom size button
        btn_custom = QPushButton("Resize to Custom Size")
        btn_custom.setStyleSheet(
            "background-color: #f39c12; color: white; border-radius: 5px;"
            "font-size: 16px; padding: 10px;"
            "outline: none;"
        )
        btn_custom.clicked.connect(self.set_custom_size)
        self.layout.addWidget(btn_custom)

        # Clear button
        btn_clear = QPushButton("Clear Images")
        btn_clear.setStyleSheet(
            "background-color: #D32F2F; color: white; border-radius: 5px;"
            "font-size: 16px; padding: 10px;"
            "outline: none;"
        )
        btn_clear.clicked.connect(self.clear_images)
        self.layout.addWidget(btn_clear)

        # Select output folder
        btn_folder = QPushButton("Select Output Folder")
        btn_folder.setStyleSheet(
            "background-color: #555; color: white; border-radius: 5px;"
            "font-size: 16px; padding: 10px;"
            "outline: none;"
        )
        btn_folder.clicked.connect(self.select_output_folder)
        self.layout.addWidget(btn_folder)

        # Output folder label
        self.output_label = QLabel(f"Output Folder: {self.output_folder}")
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setStyleSheet(
            "font-size: 12px; color: #bbbbbb; margin-top: 5px;"
        )
        self.layout.addWidget(self.output_label)

    # === Drag & Drop Events ===

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.dragged_files.extend(file_paths)  # store them in instance list
        self.file_list.addItems(os.path.basename(f) for f in file_paths)
        self.status_label.setText("Images ready to resize")
        event.accept()

    # === NEW: Browse Images ===

    def browse_images(self):
        """Open a file dialog to select image files, add them to the list."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",  # starting directory
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
        )
        if files:
            self.dragged_files.extend(files)
            self.file_list.addItems(os.path.basename(f) for f in files)
            self.status_label.setText("Images ready to resize")

    # === Resizing Logic ===

    def set_size(self, width, height):
        """Set a preset size and process images."""
        self.target_size = (width, height)
        self.process_images()

    def set_custom_size(self):
        """Set a custom size from the text fields and process images."""
        try:
            width = int(self.width_entry.text())
            height = int(self.height_entry.text())
            self.target_size = (width, height)
            self.process_images()
        except ValueError:
            self.status_label.setText(
                "Invalid input! Enter valid width and height values."
            )

    def process_images(self):
        """Resize each image in self.dragged_files to self.target_size,
        save to self.output_folder, and then delete the original image."""
        if not self.dragged_files:
            self.status_label.setText("No images have been added!")
            return

        # Resize + Save to output folder
        for img_path in self.dragged_files:
            filename = os.path.basename(img_path)
            output_path = os.path.join(self.output_folder, filename)
            self.resize_and_crop_save(img_path, output_path, self.target_size)

            # Delete the original file after processing
            try:
                os.remove(img_path)
            except Exception as e:
                print(f"Error deleting file {img_path}: {e}")

        # Show success message
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.status_label.setText(
            f"✅ Processed {len(self.dragged_files)} images to "
            f"{self.target_size[0]}x{self.target_size[1]}! Waiting for images..."
        )
        # Clear images from the list
        self.clear_images()

    @staticmethod
    def resize_and_crop_save(src_path, dst_path, target_size):
        """Open an image from `src_path`, resize/crop it, then save to `dst_path`."""
        img = Image.open(src_path)
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]

        # Determine new dimensions to preserve aspect ratio
        if img_ratio > target_ratio:
            # Wider than target ratio
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        else:
            # Taller or equal ratio
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)

        # Resize (maintain aspect ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Crop to exact target size
        left = (new_width - target_size[0]) // 2
        top = (new_height - target_size[1]) // 2
        right = left + target_size[0]
        bottom = top + target_size[1]

        cropped_img = img.crop((left, top, right, bottom))
        cropped_img.save(dst_path, quality=95)

    # === Folder & Config ===

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.save_config(folder)
            self.output_label.setText(f"Output Folder: {folder}")

    def load_config(self):
        """Return the saved output folder if config.json exists, else current folder."""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                return json.load(f).get("output_folder", os.getcwd())
        return os.getcwd()

    def save_config(self, folder):
        """Save the selected output folder to config.json."""
        with open(self.CONFIG_FILE, "w") as f:
            json.dump({"output_folder": folder}, f)

    def clear_images(self):
        """Clear the list widget and in-memory paths; do NOT overwrite the status label."""
        self.dragged_files.clear()
        self.file_list.clear()


if __name__ == "__main__":
    app = QApplication([])
    window = ImageResizerApp()
    window.show()
    app.exec_()
