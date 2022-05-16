import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget
)


class LogDisplay(QWidget):
    def __init__(self):
        super(LogDisplay, self).__init__()
        self.name = None
        self.initUI()
        self.initActions()

    def initUI(self):
        myPath = os.path.dirname(__file__)
        uiFile = "logdisplay.ui"
        uic.loadUi(os.path.join(myPath, "ui", uiFile), self)

    def initActions(self):
        self.closeBtn.clicked.connect(self.hide)

    def setName(self, name: str):
        # Set name of current connection
        self.name = name
        self.title.setText(f"Log of {name}")

    def addText(self, text: str):
        # Add text to log window
        self.textEdit.append(text)
