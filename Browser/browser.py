from Browser.browser_model import BrowerModel
from Browser.browser_view import BrowserPanelView

class Browser():
    def __init__(self):
        self._model = BrowerModel()
        self._view = BrowserPanelView(model=self._model)
        self._view.init_ui()

    @property
    def view(self):
        return self._view

    @property
    def model(self):
        return self._model


