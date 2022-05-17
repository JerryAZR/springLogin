import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QLineEdit
)


class PwDialog(QDialog):
    def __init__(self, user: str):
        super(PwDialog, self).__init__()
        self.initUI()
        self.initActions()
        self.user.setText(user)

    def initUI(self):
        # Load the Qt ui (xml) file
        myPath = os.path.dirname(__file__)
        uiFile = "pwdialog.ui"
        uic.loadUi(os.path.join(myPath, "ui", uiFile), self)
        showIcon = "eye.svg"
        self.showBtn.setIcon(QIcon(os.path.join(myPath, "ui", showIcon)))

    def initActions(self):
        self.showBtn.pressed.connect(self.showPassword)
        self.showBtn.released.connect(self.hidePassword)

    def showPassword(self):
        self.pwLine.setEchoMode(QLineEdit.Normal)
        myPath = os.path.dirname(__file__)
        showIcon = "eye-off.svg"
        self.showBtn.setIcon(QIcon(os.path.join(myPath, "ui", showIcon)))

    def hidePassword(self):
        self.pwLine.setEchoMode(QLineEdit.Password)
        myPath = os.path.dirname(__file__)
        showIcon = "eye.svg"
        self.showBtn.setIcon(QIcon(os.path.join(myPath, "ui", showIcon)))

    def password(self):
        return self.pwLine.text()
