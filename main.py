import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QFileDialog,
                               QHBoxLayout, QMessageBox)

from nodal_view import NodalView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nodal Interface")
        self.setGeometry(100, 100, 1000, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Nodal view
        self.nodal_view = NodalView()
        layout.addWidget(self.nodal_view)

        # Button bar
        button_layout = QVBoxLayout()

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