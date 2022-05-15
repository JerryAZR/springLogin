import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget
)

class Entry(QWidget):
    def __init__(self, name="", port=22, index=-1):
        super(Entry, self).__init__()
        self.active = False
        self.name = name
        self.port = port
        self.index = index
        self.initUI()
        self.initActions()
        self.turnOff()

    def initUI(self):
        # Load the Qt ui (xml) file
        myPath = os.path.dirname(__file__)
        uiFile = "connEntry.ui"
        uic.loadUi(os.path.join(myPath, "ui", uiFile), self)
        self.nameLabel.setText(self.name)
        logIcon = "math-log.svg"
        self.logBtn.setIcon(QIcon(os.path.join(myPath, "ui", logIcon)))
        editIcon = "playlist-edit.svg"
        self.editBtn.setIcon(QIcon(os.path.join(myPath, "ui", editIcon)))
        trashIcon = "trash-can.svg"
        self.deleteBtn.setIcon(QIcon(os.path.join(myPath, "ui", trashIcon)))

    def initActions(self):
        # Connect signals and slots
        # This is only a test
        self.startBtn.clicked.connect(self.toggle)

    # Setters
    def setName(self, name: str):
        self.name = name
        self.nameLabel.setText(self.name)

    def setPort(self, port: int):
        self.port = port

    def setIndex(self, index: int):
        self.index = index

    # Status image helper
    def turnOn(self):
        self.active = True
        myPath = os.path.dirname(__file__)
        iconFile = "green.svg"
        iconPath = os.path.join(myPath, "ui", iconFile)
        self.status.setPixmap(QIcon(iconPath).pixmap(20, 20))
        stopIcon = "close-octagon.svg"
        self.startBtn.setIcon(QIcon(os.path.join(myPath, "ui", stopIcon)))

    def turnOff(self):
        self.active = False
        myPath = os.path.dirname(__file__)
        iconFile = "red.svg"
        iconPath = os.path.join(myPath, "ui", iconFile)
        self.status.setPixmap(QIcon(iconPath).pixmap(20, 20))
        startIcon = "play.svg"
        self.startBtn.setIcon(QIcon(os.path.join(myPath, "ui", startIcon)))

    def toggle(self):
        if self.active:
            self.turnOff()
        else:
            self.turnOn()
