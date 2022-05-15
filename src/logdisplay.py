import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget
)

class LogDisplay(QWidget):
    def __init__(self):
        super(LogDisplay, self).__init__()
        self.initUI()
        self.initActions()

    def initUI(self):
        myPath = os.path.dirname(__file__)
        uiFile = "logdisplay.ui"
        uic.loadUi(os.path.join(myPath, "ui", uiFile), self)

    def initActions(self):
        self.closeBtn.clicked.connect(self.hide)