import json

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu, QInputDialog

from Node.node import Node
from Node.socket import Socket
from Node.connection import Connection

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
               self.rename_node_action(node)
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

    def rename_node_action(self, node):
        """
        handle the renaming process on a specific node : open input text window, set new title on node
        :param node:
        :return:
        """
        new_name, ok = QInputDialog.getText(self, "Rename Node",
                                            "Enter new name:",
                                            text=node.title)
        if ok and new_name:
            node.set_title(new_name)


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
        zoom_factor = 1.05
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