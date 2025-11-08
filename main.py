import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                               QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                               QGraphicsPathItem, QGraphicsTextItem, QPushButton,
                               QVBoxLayout, QWidget, QMenu, QInputDialog, QFileDialog,
                               QHBoxLayout, QMessageBox)
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QFont, QPainter


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
        ctrl1 = QPointF(start.x() + ctrl_offset, start.y())
        ctrl2 = QPointF(end.x() - ctrl_offset, end.y())
        path.cubicTo(ctrl1, ctrl2, end)

        self.setPath(path)


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
        socket = Socket(0, self.height / 2, 'input', self)
        self.input_sockets.append(socket)

        # Create single output socket
        socket = Socket(self.width, self.height / 2, 'output', self)
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


class NodalView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Background
        self.setBackgroundBrush(QBrush(QColor(30, 30, 40)))

        # Connection drawing
        self.temp_connection = None
        self.start_socket = None

        # Node tracking
        self.nodes = {}  # Dictionary to track nodes by ID

        # Add some example nodes
        self.add_node("Input Node", -250, -100)
        self.add_node("Process Node", 0, -100)
        self.add_node("Output Node", 250, -100)

    def add_node(self, title, x, y, node_id=None):
        node = Node(title, x, y, node_id)
        self.scene.addItem(node)
        self.nodes[node.node_id] = node
        return node

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())

        # Find the node (item might be a child like Socket or text)
        node = None
        if isinstance(item, Node):
            node = item
        elif item and item.parentItem() and isinstance(item.parentItem(), Node):
            node = item.parentItem()

        menu = QMenu()

        if node:
            # Context menu for node
            rename_action = menu.addAction("Rename Node")
            delete_action = menu.addAction("Delete Node")

            action = menu.exec(event.globalPos())

            if action == rename_action:
                new_name, ok = QInputDialog.getText(self, "Rename Node",
                                                    "Enter new name:",
                                                    text=node.title)
                if ok and new_name:
                    node.set_title(new_name)
            elif action == delete_action:
                node.delete()
        else:
            # Context menu for empty space
            create_action = menu.addAction("Create Node")

            action = menu.exec(event.globalPos())

            if action == create_action:
                node_name, ok = QInputDialog.getText(self, "Create Node",
                                                     "Enter node name:",
                                                     text="New Node")
                if ok and node_name:
                    pos = self.mapToScene(event.pos())
                    self.add_node(node_name, pos.x(), pos.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if isinstance(item, Socket):
                self.start_socket = item
                self.temp_connection = Connection(item)
                self.scene.addItem(self.temp_connection)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_connection:
            self.temp_connection.end_pos = self.mapToScene(event.position().toPoint())
            self.temp_connection.update_path()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.temp_connection:
            item = self.itemAt(event.position().toPoint())
            if isinstance(item, Socket) and item != self.start_socket:
                # Valid connection
                if (self.start_socket.socket_type != item.socket_type):
                    self.temp_connection.end_socket = item
                    self.start_socket.connections.append(self.temp_connection)
                    item.connections.append(self.temp_connection)
                    self.temp_connection.update_path()
                else:
                    self.scene.removeItem(self.temp_connection)
            else:
                self.scene.removeItem(self.temp_connection)

            self.temp_connection = None
            self.start_socket = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # Zoom with mouse wheel
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)

    def keyPressEvent(self, event):
        # Delete selected nodes with Delete or Backspace key
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for item in self.scene.selectedItems():
                if isinstance(item, Node):
                    item.delete()
        super().keyPressEvent(event)

    def save_graph(self, filename):
        """Save the graph to a JSON file"""
        graph_data = {
            "nodes": [],
            "connections": []
        }

        # Save nodes
        for node_id, node in self.nodes.items():
            node_data = {
                "id": node_id,
                "title": node.title,
                "x": node.pos().x(),
                "y": node.pos().y()
            }
            graph_data["nodes"].append(node_data)

        # Save connections
        processed_connections = set()
        for node_id, node in self.nodes.items():
            for socket in node.output_sockets:
                for connection in socket.connections:
                    if connection.end_socket and id(connection) not in processed_connections:
                        # Find the source and target nodes
                        source_node = connection.start_socket.parentItem()
                        target_node = connection.end_socket.parentItem()

                        conn_data = {
                            "source_node": source_node.node_id,
                            "target_node": target_node.node_id
                        }
                        graph_data["connections"].append(conn_data)
                        processed_connections.add(id(connection))

        try:
            with open(filename, 'w') as f:
                json.dump(graph_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving graph: {e}")
            return False

    def load_graph(self, filename):
        """Load a graph from a JSON file"""
        try:
            with open(filename, 'r') as f:
                graph_data = json.load(f)

            # Clear existing graph
            self.scene.clear()
            self.nodes.clear()

            # Load nodes
            for node_data in graph_data["nodes"]:
                self.add_node(
                    node_data["title"],
                    node_data["x"],
                    node_data["y"],
                    node_data["id"]
                )

            # Load connections
            for conn_data in graph_data["connections"]:
                source_node = self.nodes.get(conn_data["source_node"])
                target_node = self.nodes.get(conn_data["target_node"])

                if source_node and target_node:
                    # Get the output socket from source and input socket from target
                    start_socket = source_node.output_sockets[0]
                    end_socket = target_node.input_sockets[0]

                    # Create connection
                    connection = Connection(start_socket, end_socket)
                    self.scene.addItem(connection)
                    start_socket.connections.append(connection)
                    end_socket.connections.append(connection)
                    connection.update_path()

            return True
        except Exception as e:
            print(f"Error loading graph: {e}")
            return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nodal Interface")
        self.setGeometry(100, 100, 1000, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Nodal view
        self.nodal_view = NodalView()
        layout.addWidget(self.nodal_view)

        # Button bar
        button_layout = QHBoxLayout()

        # Add node button
        add_button = QPushButton("Add Node")
        add_button.clicked.connect(self.add_new_node)
        button_layout.addWidget(add_button)

        # Save button
        save_button = QPushButton("Save Graph")
        save_button.clicked.connect(self.save_graph)
        button_layout.addWidget(save_button)

        # Load button
        load_button = QPushButton("Load Graph")
        load_button.clicked.connect(self.load_graph)
        button_layout.addWidget(load_button)

        layout.addLayout(button_layout)

        self.node_counter = 1

    def add_new_node(self):
        self.nodal_view.add_node(f"Node {self.node_counter}", 0, 0)
        self.node_counter += 1

    def save_graph(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Graph",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            if self.nodal_view.save_graph(filename):
                QMessageBox.information(self, "Success", "Graph saved successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save graph.")

    def load_graph(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Graph",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            if self.nodal_view.load_graph(filename):
                QMessageBox.information(self, "Success", "Graph loaded successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to load graph.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())