from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QColor, QPainterPath


class Connection(QGraphicsPathItem):
    def __init__(self, start_socket, end_socket=None):
        super().__init__()
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.end_pos = None

        # Styling
        pen = QPen(QColor(150, 150, 150), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.setZValue(0)

        self.update_path()

    def update_path(self):
        path = QPainterPath()
        start = self.start_socket.get_center()

        if self.end_socket:
            end = self.end_socket.get_center()
        elif self.end_pos:
            end = self.end_pos
        else:
            end = start

        path.moveTo(start)

        # Create curved connection
        ctrl_offset = abs(end.x() - start.x()) * 0.5
        ctrl1 = QPointF(start.x() , start.y()+ ctrl_offset)
        ctrl2 = QPointF(end.x() , end.y()- ctrl_offset)
        path.cubicTo(ctrl1, ctrl2, end)

        self.setPath(path)
