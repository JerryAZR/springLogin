import keyring
import json
import subprocess
import traceback
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QLineEdit,
    QMessageBox
)
from entry import Entry
from logdisplay import LogDisplay

class HomePage(QMainWindow):
    java = "java"
    project = "demo.jar"
    jsonfile = "history.json"

    def __init__(self) -> None:
        super(HomePage, self).__init__()
        self.logDisplay = LogDisplay()
        self.initUI()
        self.load()
        self.initActions()
        # Hide editor and log on start up
        self.logDisplay.hide()
        self.editorWidget.hide()

    def initUI(self):
        # Load the Qt ui (xml) file
        myPath = os.path.dirname(__file__)
        uiFile = "mainwindow.ui"
        uic.loadUi(os.path.join(myPath, "ui", uiFile), self)
        xIcon = "close.svg"
        self.closeEditorBtn.setIcon(QIcon(os.path.join(myPath, "ui", xIcon)))
        self.centralLayout.addWidget(self.logDisplay)
        # TODO: Scale the image to fit window
        self.setStyleSheet(
            "QMainWindow {\
                background-image: url(bg.jpg);\
                background-position: top left;\
                background-origin: content;}")

    def initActions(self):
        # Connect signals and slots (handlers)
        self.showBtn.pressed.connect(self.showPassword)
        self.showBtn.released.connect(self.hidePassword)
        self.loginBtn.clicked.connect(self.submit)
        self.saveBtn.clicked.connect(self.save)
        self.cancelBtn.clicked.connect(self.editorWidget.hide)
        self.nameSel.currentIndexChanged.connect(self.autofill)
        self.closeEditorBtn.clicked.connect(self.editorWidget.hide)

    def showPassword(self):
        self.pwLine.setEchoMode(QLineEdit.Normal)

    def hidePassword(self):
        self.pwLine.setEchoMode(QLineEdit.Password)

    def save(self):
        # Save log in info to a json file
        name = self.nameSel.currentText()
        url = self.urlSel.currentText()
        port = self.portSel.currentText()
        username = self.userSel.currentText()
        password = self.pwLine.text()
        # Verify user input
        if url == "" or port == "" or username == "":
            self.toast("Missing log in information")
            return
        # Save account info
        system = f"{url}:{port}"
        if self.saveCheck.isChecked():
            keyring.set_password(system, username, password)
        else:
            keyring.set_password(system, username, "")

        # Create JSON entry
        jentry = {
            "url": url,
            "port": port,
            "user": username
        }
        # Auto generate name if none provided
        if name == "":
            name = url
        # TODO: warn user on overwrite
        self.history[name] = jentry
        self.history["Previous"] = self.nameSel.currentIndex()
        with open(self.jsonfile, "w") as out_file:
            json.dump(self.history, out_file, indent=4)
        # Reload selections
        self.load()
        # Restore password
        self.pwLine.setText(password)

    def makeEditFunc(self, index: int):
        return lambda: (self.autofill(index), self.editorWidget.show())

    def makeLogFunc(self):
        return self.logDisplay.show

    def load(self):
        # Load history from json file
        try:
            with open(self.jsonfile, "r") as in_file:
                self.history = json.load(in_file)
            # First clear the selections
            self.nameSel.clear()
            self.urlSel.clear()
            self.portSel.clear()
            self.userSel.clear()

            i = 0
            for key in self.history:
                if key == "Previous":
                    continue
                self.nameSel.addItem(key)
                self.urlSel.addItem(self.history[key]["url"])
                self.portSel.addItem(self.history[key]["port"])
                self.userSel.addItem(self.history[key]["user"])
                # Add status entry
                newEntry = Entry(key, self.history[key]["port"])
                self.entries.addWidget(newEntry)
                # Bind functions
                newEntry.editBtn.clicked.connect(self.makeEditFunc(i))
                newEntry.logBtn.clicked.connect(self.makeLogFunc())
                # Update index counter
                i += 1
            
            self.autofill(self.history["Previous"])
        except FileNotFoundError:
            self.history = {}

    def submit(self):
        # Retrieve log in info
        name = self.nameSel.currentText()
        url = self.urlSel.currentText()
        port = self.portSel.currentText()
        username = self.userSel.currentText()
        password = self.pwLine.text()
        # Save (Maybe make this optional?)
        # self.save()
        if url == "" or port == "" or username == "" or password == "":
            self.toast("Missing log in information")
            return
        # Update history
        self.history["Previous"] = self.nameSel.currentIndex()
        with open(self.jsonfile, "w") as out_file:
            json.dump(self.history, out_file, indent=4)
        # Construct command
        option1 = f"--spring.datasource.url={url}"
        option2 = f"--spring.datasource.username={username}"
        option3 = f"--spring.datasource.password={password}"
        option4 = f"--server.port={port}"
        cmd = [self.java, "-jar", self.project, option1, option2, option3, option4]
        try:
            subprocess.run(cmd)
            self.toast("Successful.")
        except Exception:
            self.toast("A problem has occured. Please check error.log for details.")
            with open("error.log", "w") as outfile:
                outfile.write(traceback.format_exc())
            self.toast(traceback.format_exc())

    def autofill(self, index):
        # using try-except because this function could fail when reloading
        try:
            if (self.nameSel.currentIndex() != index):
                self.nameSel.setCurrentIndex(index)
            self.urlSel.setCurrentIndex(index)
            self.portSel.setCurrentIndex(index)
            self.userSel.setCurrentIndex(index)

            # Get password
            entryName = self.nameSel.currentText()
            entry = self.history[entryName]
            system = f"{entry['url']}:{entry['port']}"
            password = keyring.get_password(system, entry["user"])
            if password:
                self.pwLine.setText(password)
                self.saveCheck.setChecked(True)
            else:
                self.pwLine.setText("")
                self.saveCheck.setChecked(False)
        except Exception as e:
            print(e)

    def toast(self, message):
        box = QMessageBox(QMessageBox.Warning, "Warning", message)
        box.exec_()
