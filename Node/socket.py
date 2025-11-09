from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QPen, QBrush, QColor

class Socket(QGraphicsEllipseItem):
    def __init__(self, x, y, socket_type, parent=None):
        super().__init__(-8, -8, 16, 16, parent)
        self.socket_type = socket_type  # 'input' or 'output'
        self.connections = []
        self.setPos(x, y)

        # Styling
        if socket_type == 'input':
            self.setBrush(QBrush(QColor(100, 150, 255)))
        else:
            self.setBrush(QBrush(QColor(255, 150, 100)))
        self.setPen(QPen(QColor(50, 50, 50), 2))
        self.setZValue(2)

    def get_center(self):
        return self.parentItem().pos() + self.pos()