import json
from pathlib import Path

from PySide6.QtCore import Qt, QPoint, QRect, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu, QInputDialog, QRubberBand, QGraphicsTextItem

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QFont, QColor

from Node.node import Node
from Node.socket import Socket
from Node.connection import Connection
from Node.comment import Comment


class NodalView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        max_val = 1000000
        self.scene.setSceneRect(-max_val, -max_val, max_val * 2, max_val * 2)

        # Background
        self.setBackgroundBrush(QBrush(QColor(30, 30, 40)))

        # Connection drawing
        self.temp_connection = None
        self.start_socket = None

        # Selection
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

        # Node tracking
        self.nodes = {}  # Dictionary to track nodes by ID
        self.comments = {}  # Dictionary to track comment by ID

        # Add some example nodes
        self.add_node("Input Node", -250, -100)
        self.add_node("Process Node", 0, -100)
        self.add_node("Output Node", 250, -100)

        # Node contextual menu
        self.node_context_menu = QMenu()
        self.rename_action = self.node_context_menu.addAction("Rename Node")
        self.delete_action = self.node_context_menu.addAction("Delete Node")

        # Scene context menu
        self.scene_context_menu = QMenu()
        self.create_action = self.scene_context_menu.addAction("Create Node")
        self.create_text_action = self.scene_context_menu.addAction("Create Text")

        self.show_grid = False
        # Enable drop events
        self.setAcceptDrops(True)

    def add_text(self, text, x, y, id=None):
        """
        add a comment
        todo: redondance with add node
        :param text:
        :param x:
        :param y:
        :param id:
        :return:
        """
        comment = Comment(text,x,y,id)
        # text_item = QGraphicsTextItem(text)
        # text_item.setFont(QFont("Arial", 14))
        # text_item.setDefaultTextColor(QColor("#1DB954"))  # Spotify green, why not
        #
        # # Center the text on the drop position
        # text_item.setPos(
        #     x - text_item.boundingRect().width() / 2,
        #     y - text_item.boundingRect().height() / 2,
        # )
        self.scene.addItem(comment)
        self.comments[comment.node_id] = comment

    def add_node(self, title, x, y, node_id=None, center=False):
        node = Node(title, x, y, node_id, center)
        self.scene.addItem(node)
        self.nodes[node.node_id] = node
        return node

    def dragEnterEvent(self, event):
        # Accept if it contains URLs (files dragged from desktop)
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # Check if at least one file is an MP3
            if any(url.toLocalFile().lower().endswith('.mp3') or url.toLocalFile().lower().endswith('.wav') for url in urls):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        # Must also accept dragMoveEvent, otherwise drop won't fire
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.mp3') or file_path.lower().endswith('.wav'):
                    # Convert drop position to scene coordinates
                    scene_pos = self.mapToScene(event.position().toPoint())
                    self.add_filename_label(file_path, scene_pos)
            event.acceptProposedAction()

    def add_filename_label(self, file_path: str, pos: QPointF):
        filename = Path(file_path).name  # e.g. "mysong.mp3"
        self.add_node(filename, pos.x(), pos.y(), center=True)
        print("youpi")


    def show_node_context_menu(self, node: Node, event):
        """
        display the context menu for nodes
        :param node: node clicked on
        :param event: event trigged by the click
        """
        action = self.node_context_menu.exec(event.globalPos())
        if action == self.rename_action:
            self.rename_node_action(node)
        elif action == self.delete_action:
            node.delete()

    def show_scene_context_menu(self, event):
        """
        context menu for the global scene, when clicking on the background
        :param event:
        todo: redondance ici
        """
        action = self.scene_context_menu.exec(event.globalPos())
        if action == self.create_action:
            node_name, ok = QInputDialog.getText(self, "Create Node",
                                                 "Enter node name:",
                                                 text="New Node")
            if ok and node_name:
                pos = self.mapToScene(event.pos())
                self.add_node(node_name, pos.x(), pos.y())

        if action == self.create_text_action:
            text, ok = QInputDialog.getText(self, "Create Text",
                                                 "Enter Text:",
                                                 text="")
            if ok and text:
                pos = self.mapToScene(event.pos())
                self.add_text(text,pos.x(),pos.y())

    def drawBackground(self, painter, rect):
        """Draw a grid background for infinite canvas feel"""
        super().drawBackground(painter, rect)

        # Draw grid
        painter.setPen(QPen(QColor(150, 150, 150), 0))

        if not self.show_grid:
            return
        # Grid spacing (adjusts with zoom)
        grid_size = 50

        # Calculate visible area
        left = int(rect.left() / grid_size) * grid_size
        top = int(rect.top() / grid_size) * grid_size
        right = int(rect.right() / grid_size) * grid_size
        bottom = int(rect.bottom() / grid_size) * grid_size

        # Draw vertical lines
        x = left
        while x <= right:
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += grid_size

        # Draw horizontal lines
        y = top
        while y <= bottom:
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += grid_size
        # Draw origin axes in different color
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.drawLine(int(rect.left()), 0, int(rect.right()), 0)  # X-axis
        painter.drawLine(0, int(rect.top()), 0, int(rect.bottom()))  # Y-axis

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())

        # Find the node (item might be a child like Socket or text)
        node = None
        if isinstance(item, Node):
            node = item
        elif item and item.parentItem() and isinstance(item.parentItem(), Node):
            node = item.parentItem()

        if node:
            self.show_node_context_menu(node, event)
        else:
            self.show_scene_context_menu(event)

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

            elif not item:  # Draw selection
                self.origin = event.pos()
                # Set the geometry of the rubber band to a 1x1 rectangle at the origin
                self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
                self.rubberBand.show()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_connection:
            self.temp_connection.end_pos = self.mapToScene(event.position().toPoint())
            self.temp_connection.update_path()

        # Update the rubber band's geometry while dragging
        elif self.rubberBand.isVisible():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

        super().mouseMoveEvent(event)

    def handle_connection_target(self, event):
        """
        function that handle what is going on when the connection is dropped.
        If dropped on a slot, connection is done otherwise connection is removed
        :param event:
        :return:
        """
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

    def handle_selection_dropped(self):
        """
        Handle the action when a selection is finishing
        :return:
        """
        self.rubberBand.hide()
        selection_rect = self.rubberBand.geometry()
        for i, n in self.nodes.items():
            if self.mapToScene(selection_rect).boundingRect().intersects(n.rect()):
                n.setSelected(True)

    def mouseReleaseEvent(self, event):
        if self.temp_connection:
            self.handle_connection_target(event)
        elif self.rubberBand.isVisible():  # finalise the selection
            self.handle_selection_dropped()

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
            "connections": [],
            "comments": []
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

        for node_id, comment in self.comments.items():
            comment_data = {
                "id": node_id,
                "title": comment.title,
                "x": comment.pos().x(),
                "y": comment.pos().y()
            }
            graph_data["comments"].append(comment_data)

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

            # Load comments
            for node_data in graph_data.get("comments",{}):
                self.add_text(
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
