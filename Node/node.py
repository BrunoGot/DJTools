from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QFont

from .socket import Socket


class Node(QGraphicsItem):
    def __init__(self, title, x, y, node_id=None):
        super().__init__()
        self.title = title
        self.node_id = node_id if node_id else id(self)  # Unique identifier
        self.width = 180
        self.height = 120
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(1)

        # Title
        self.title_item = QGraphicsTextItem(title, self)
        font = QFont("Arial", 11, QFont.Weight.Bold)
        self.title_item.setFont(font)
        self.title_item.setDefaultTextColor(QColor(255, 255, 255))
        self.title_item.setPos(10, 5)

        # Sockets
        self.input_sockets = []
        self.output_sockets = []

        # Create single input socket
        socket = Socket(self.width/2, 0, 'input', self)
        self.input_sockets.append(socket)

        # Create single output socket
        socket = Socket(self.width/2, self.height, 'output', self)
        self.output_sockets.append(socket)

    def set_title(self, new_title):
        self.title = new_title
        self.title_item.setPlainText(new_title)

    def delete(self):
        # Remove all connections
        for socket in self.input_sockets + self.output_sockets:
            for connection in socket.connections[:]:  # Copy list to avoid modification during iteration
                if connection.scene():
                    connection.scene().removeItem(connection)
                # Remove from other socket's connections
                if connection.start_socket != socket:
                    if connection in connection.start_socket.connections:
                        connection.start_socket.connections.remove(connection)
                if connection.end_socket and connection.end_socket != socket:
                    if connection in connection.end_socket.connections:
                        connection.end_socket.connections.remove(connection)
            socket.connections.clear()

        # Remove from nodal view tracking
        view = self.scene().views()[0] if self.scene() and self.scene().views() else None
        if view and hasattr(view, 'nodes') and self.node_id in view.nodes:
            del view.nodes[self.node_id]

        # Remove node from scene
        if self.scene():
            self.scene().removeItem(self)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        # Node body
        gradient_start = QColor(60, 60, 80)
        gradient_end = QColor(40, 40, 60)

        if self.isSelected():
            gradient_start = QColor(80, 80, 120)
            gradient_end = QColor(60, 60, 100)

        # Draw rounded rectangle
        painter.setBrush(QBrush(gradient_start))
        painter.setPen(QPen(QColor(100, 100, 150), 2))
        painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)

        # Header bar
        painter.setBrush(QBrush(QColor(50, 50, 70)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width, 30, 10, 10)
        painter.drawRect(0, 20, self.width, 10)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update all connections when node moves
            for socket in self.input_sockets + self.output_sockets:
                for connection in socket.connections:
                    connection.update_path()
        return super().itemChange(change, value)
