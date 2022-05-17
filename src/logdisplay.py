import os
from PyQt5 import uic
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import (
    QWidget
)


class LogDisplay(QWidget):
    def __init__(self):
        super(LogDisplay, self).__init__()
        self.name = None
        self.initUI()
        self.initActions()
        self.process = QProcess()

    def initUI(self):
        myPath = os.path.dirname(__file__)
        uiFile = "logdisplay.ui"
        uic.loadUi(os.path.join(myPath, "ui", uiFile), self)

    def initActions(self):
        self.closeBtn.clicked.connect(self.hide)
        self.openBtn.clicked.connect(self.openLog)

    def setName(self, name: str):
        # Set name of current connection
        self.name = name
        self.title.setText(f"Log of {name}")

    def addText(self, text: str):
        # Add text to log window
        self.textEdit.append(text)

    def openLog(self):
        # Open log in text editor
        self.process.kill()
        options = ["/c", "start", f"{self.name}.log"]
        self.process.start("cmd", options)
