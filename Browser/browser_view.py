from PySide6 import QtWidgets

class BrowserPanelView(QtWidgets.QWidget):
    def __init__(self, model):
        super(BrowserPanelView, self).__init__()
        self.model = model

    def init_ui(self):
        files = self.model.get_file_list()
        layout = self.display_files(files)
        self.setLayout(layout)

    def display_files(self, files:list[str]):
        layout = QtWidgets.QVBoxLayout()
        for f in files:
            file_btn = QtWidgets.QPushButton(f)
            file_btn.clicked.connect(self.on_select_file)
            layout.addWidget(file_btn)
        # layout.addLayout(QtWidgets.)
        return layout

    def on_select_file(self):
        print("file selected")