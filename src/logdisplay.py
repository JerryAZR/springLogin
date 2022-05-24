import os
from PyQt5 import uic
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import (
    QWidget,
    QTextEdit
)


class LogDisplay(QWidget):
    def __init__(self):
        super(LogDisplay, self).__init__()
        self.initUI()
        self.initActions()
        self.process = QProcess()
        self.tabWidget.clear()
        self.logs = {}

    def initUI(self):
        myPath = os.path.dirname(__file__)
        uiFile = "logdisplay.ui"
        uic.loadUi(os.path.join(myPath, "ui", uiFile), self)

    def initActions(self):
        self.closeBtn.clicked.connect(self.hide)
        self.openBtn.clicked.connect(self.openLog)
        self.tabWidget.tabCloseRequested.connect(self.removeTab)

    def setName(self, name: str):
        # Set name of current connection
        if name not in self.logs:
            self.logs[name] = QTextEdit()
            self.tabWidget.addTab(self.logs[name], name)
        self.tabWidget.setCurrentWidget(self.logs[name])

    def addText(self, name: str, text: str):
        # Add text to log window
        if name in self.logs:
            self.logs[name].append(text)

    def removeTab(self, index: int):
        name = self.tabWidget.tabText(index)
        self.logs.pop(name)
        self.tabWidget.removeTab(index)

    def openLog(self):
        # Open log in text editor
        self.process.kill()
        name = self.tabWidget.tabText(self.tabWidget.currentIndex())
        options = ["/c", "start", f"{name}.log"]
        self.process.start("cmd", options)
