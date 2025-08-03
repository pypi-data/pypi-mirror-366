from PySide6.QtWidgets import QMainWindow

from .ui.{{ module.name }} import Ui_{{ class.name }}


class {{ class.name }}(QMainWindow, Ui_{{ class.name }}):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
