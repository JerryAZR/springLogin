import keyring
import json
import os
import traceback
from PyQt5 import uic
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QLineEdit,
    QMessageBox
)
from entry import Entry
from logdisplay import LogDisplay
from pwdialog import PwDialog


class HomePage(QMainWindow):
    java = "java"
    project = "demo.jar"
    jsonfile = "history.json"
    helperDialects = ["dialect1", "dialect2"]

    def __init__(self) -> None:
        super(HomePage, self).__init__()
        # Dictionary for all QProcess objects
        self.processes = {}
        self.logDisplay = LogDisplay()
        self.initUI()
        self.load()
        self.initActions()
        # Hide editor and log on start up
        self.logDisplay.hide()
        self.editor.hide()

    def initUI(self):
        # Load the Qt ui (xml) file
        myPath = os.path.dirname(__file__)
        uiFile = "mainwindow.ui"
        uic.loadUi(os.path.join(myPath, "ui", uiFile), self)
        xIcon = "close.svg"
        self.closeEditorBtn.setIcon(QIcon(os.path.join(myPath, "ui", xIcon)))
        addIcon = "plus.svg"
        self.addBtn.setIcon(QIcon(os.path.join(myPath, "ui", addIcon)))
        self.centralLayout.addWidget(self.logDisplay)
        # Update helperDialect combo box
        self.helperSel.addItems(self.helperDialects)
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
        self.cancelBtn.clicked.connect(self.editor.hide)
        self.nameSel.currentIndexChanged.connect(self.autofill)
        self.closeEditorBtn.clicked.connect(self.editor.hide)
        self.addBtn.clicked.connect(
            lambda: (self.nameSel.setCurrentIndex(-1), self.editor.show())
        )

    def showPassword(self):
        self.pwLine.setEchoMode(QLineEdit.Normal)

    def hidePassword(self):
        self.pwLine.setEchoMode(QLineEdit.Password)

    def save(self):
        # Save log in info to a json file
        name = self.nameSel.currentText()
        url = self.urlSel.currentText()
        port = self.portSel.currentText()
        helperIdx = self.helperSel.currentIndex()
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
            "user": username,
            "helper": helperIdx
        }
        # Auto generate name if none provided
        if name == "":
            name = f"{username}@{url}:{port}"
        # TODO: warn user on overwrite
        self.history[name] = jentry
        with open(self.jsonfile, "w") as out_file:
            json.dump(self.history, out_file, indent=4)
        # Reload selections
        self.load()
        # Restore everything
        self.autofill(self.nameSel.findText(name))
        self.pwLine.setText(password)

    # Signal handlers (slots)
    def makeEditFunc(self, index: int):
        return lambda: (self.autofill(index), self.editor.show())

    def makeLogFunc(self, name: str):
        def setupLog():
            if self.logDisplay.name != name:
                self.logDisplay.setName(name)
                self.logDisplay.addText('-' * 32)
                self.logDisplay.addText(f"Streaming log of {name}")
                self.logDisplay.addText('-' * 32)
            self.logDisplay.show()
        return setupLog

    def makeDeleteFunc(self, name: str):
        def deleteSaved():
            self.history.pop(name, None)
            with open(self.jsonfile, "w") as out_file:
                json.dump(self.history, out_file, indent=4)
            self.load()
        return deleteSaved

    def makeLogHandlerFunc(self, name: str):
        def handler():
            log = str(self.processes[name].readAll(), "utf-8")
            # Always write to the log file
            with open(name + ".log", "a") as logFile:
                logFile.write(log)
            # Write to log display area only if selected
            if self.logDisplay.name == name:
                self.logDisplay.addText(log)
        return handler

    def makeStartFunc(self, index: int, name: str):
        def toggleState():
            if self.processes[name].state() == QProcess.NotRunning:
                self.autofill(index)
                # Set up log display
                self.logDisplay.setName(name)
                self.submit()
            else:
                self.processes[name].kill()
        return toggleState

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
            # Clear status panel
            for i in reversed(range(self.entries.count())):
                self.entries.itemAt(i).widget().setParent(None)

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
                newEntry.logBtn.clicked.connect(self.makeLogFunc(key))
                newEntry.deleteBtn.clicked.connect(self.makeDeleteFunc(key))
                newEntry.startBtn.clicked.connect(self.makeStartFunc(i, key))
                # Create associate QProcess object
                # Be careful not to remove existing ones
                if key not in self.processes:
                    self.processes[key] = QProcess()
                    self.processes[key].setProcessChannelMode(
                        QProcess.MergedChannels
                    )
                    # TODO: connect error signals
                    self.processes[key].started.connect(newEntry.turnOn)
                    self.processes[key].finished.connect(newEntry.turnOff)
                    self.processes[key].readyRead.connect(
                        self.makeLogHandlerFunc(key)
                    )
                # Update index counter
                i += 1

        except FileNotFoundError:
            self.history = {}

        # # Finally, add a "Custom" entry
        # newEntry = Entry("(Custom connection)")
        # newEntry.editBtn.clicked.connect(
        #     lambda: (self.nameSel.setCurrentIndex(-1), self.editor.show())
        # )
        # # Disable buttons
        # newEntry.startBtn.setDisabled(True)
        # newEntry.logBtn.setDisabled(True)
        # self.entries.addWidget(newEntry)

    def submit(self):
        # Retrieve log in info
        name = self.nameSel.currentText()
        url = self.urlSel.currentText()
        port = self.portSel.currentText()
        helper = self.helperSel.currentText()
        username = self.userSel.currentText()
        password = self.pwLine.text()
        # Save (Maybe make this optional?)
        # self.save()
        if url == "" or port == "" or username == "":
            self.toast("Missing log in information")
            return
        if password == "":
            askPass = PwDialog(f"{username}@{url}:{port}")
            if askPass.exec_() == askPass.Accepted:
                password = askPass.password()
            else:
                return

        # Construct command
        op1 = f"--spring.datasource.url={url}"
        op2 = f"--spring.datasource.username={username}"
        op3 = f"--spring.datasource.password={password}"
        op4 = f"--server.port={port}"
        op5 = f"--pagehelper.helperDialect={helper}"
        args = ["-jar", self.project, op1, op2, op3, op4, op5]

        if name not in self.processes:
            # Create new if not found
            self.processes[name] = QProcess()
        self.processes[name].start(self.java, args)
        # Probably not a good idea to call this in the UI thread
        # TODO: Fix it so the UI thread is not blocked
        if self.processes[name].waitForStarted():
            pass
        else:
            self.toast(self.processes[name].errorString())

    def autofill(self, index):
        # using try-except because this function could fail when reloading
        try:
            entryName = self.nameSel.currentText()
            if entryName in self.history:
                entry = self.history[entryName]
                # Get pagehelper.helperDialect (Always update selection)
                helperIdx = entry["helper"]
                self.helperSel.setCurrentIndex(helperIdx)
            else:
                entry = None

            if (self.nameSel.currentIndex() != index):
                # Make sure the indexChanged signal is only emitted once
                self.nameSel.setCurrentIndex(index)
            else:
                if (self.urlSel.currentIndex() == index and
                        self.portSel.currentIndex() == index and
                        self.userSel.currentIndex() == index):
                    # Already selected so return directly
                    return
            self.urlSel.setCurrentIndex(index)
            self.portSel.setCurrentIndex(index)
            self.userSel.setCurrentIndex(index)

            # Get password
            if entry is not None:
                system = f"{entry['url']}:{entry['port']}"
                password = keyring.get_password(system, entry["user"])
                if password:
                    self.pwLine.setText(password)
                    self.saveCheck.setChecked(True)
            else:
                self.pwLine.setText("")
                self.saveCheck.setChecked(False)
        except Exception:
            traceback.print_exc()

    def toast(self, message):
        box = QMessageBox(QMessageBox.Warning, "Warning", message)
        box.exec_()
