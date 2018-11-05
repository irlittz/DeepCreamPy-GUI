import collections

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QApplication, QGraphicsView

ZOOM_FACTOR = 0.1


class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.pen = QPen(Qt.green, 3, join=Qt.MiterJoin)
        self.item_batch = []
        self.item_batches = collections.deque()

    def wheelEvent(self, event):
        if self.scene() and QApplication.keyboardModifiers() == Qt.ControlModifier:
            transform = self.transform()
            scale = 1 + ZOOM_FACTOR if event.angleDelta().y() > 0 else 1 - ZOOM_FACTOR
            self.setTransform(transform * scale)

    def mousePressEvent(self, event):
        if not self.scene():
            return

        position = self.mapToScene(event.x(), event.y())
        item = self.scene().addRect(
            position.x(), position.y(), self.pen.width(), self.pen.width(), self.pen, self.pen.brush())
        self.item_batch.append(item)

    # TODO: Calculate line between new and last-known position, and draw a rectangle for each point on the line,
    # TODO: addLine() seems to add a different-looking pattern
    def mouseMoveEvent(self, event):
        self.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.item_batch:
            self.item_batches.append(self.item_batch)
        self.item_batch = []

    # TODO: This is super ugly because we don't use addLine()
    def undo(self):
        if not self.item_batches:
            return

        item_batch = self.item_batches.pop()
        scene = self.scene()
        for item in item_batch:
            scene.removeItem(item)
