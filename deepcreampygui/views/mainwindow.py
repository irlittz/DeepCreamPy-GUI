import os
import tempfile

import PIL.Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter, QPixmap
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QMainWindow

import decensor
from deepcreampygui.paths import get_home_path
from deepcreampygui.views.ui.mainwindow import Ui_MainWindow

# 10%
ZOOM_FACTOR = 0.1


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.action_open.triggered.connect(self.open_file)
        self.ui.action_save.triggered.connect(self.save_file)
        self.ui.action_close.triggered.connect(self.close_file)
        self.ui.action_undo.triggered.connect(self.ui.graphics_view.undo)

        self.ui.pen_size.valueChanged.connect(self.change_pen_size)
        self.ui.decensor.clicked.connect(self.decensor)

        self.original_path = None

    def _get_graphics_view_image(self):
        scene = self.ui.graphics_view.scene()

        # Get rectangle that includes all items in the scene and make the scene exactly that size.
        bounding_rectangle = scene.itemsBoundingRect()
        scene.setSceneRect(bounding_rectangle)

        # Create and save image
        image = QImage(bounding_rectangle.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        scene.render(painter)
        painter.end()

        return image

    def open_file(self):
        path, mask = QFileDialog.getOpenFileName(self, 'Open...', directory=get_home_path())
        if path:
            self.original_path = path
            self.load_file(path)

    def save_file(self):
        path, mask = QFileDialog.getSaveFileName(self, 'Save...', directory=get_home_path())
        if path:
            image = self._get_graphics_view_image()
            image.save(path, 'PNG')

    def close_file(self):
        self.ui.graphics_view.setScene(None)
        self.original_path = None

    def load_file(self, path):
        scene = QGraphicsScene(self.ui.graphics_view)
        item = scene.addPixmap(QPixmap(path))
        self.ui.graphics_view.setScene(scene)
        self.ui.graphics_view.fitInView(item, Qt.KeepAspectRatio)

    def change_pen_size(self, value):
        self.ui.graphics_view.pen.setWidth(value)

    def decensor(self):
        image = self._get_graphics_view_image()
        colored_path = tempfile.mkstemp('.png')[1]
        image.save(colored_path, 'PNG')
        original = PIL.Image.open(self.original_path)
        colored = PIL.Image.open(colored_path)

        original_file_name = os.path.basename(self.original_path)
        name, extension = os.path.splitext(original_file_name)
        output_path = os.path.join(os.path.dirname(self.original_path), '{}_decensored{}'.format(name, extension))

        # Taken straight from the original ui.py
        decensorer = decensor.Decensor()
        decensor.is_mosaic = self.ui.mosaic.isChecked()
        # For some reason it has to be the colored image twice?
        decensorer.decensor_image(colored.convert('RGB'), colored.convert('RGB'), output_path)
