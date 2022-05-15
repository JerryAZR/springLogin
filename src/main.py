import sys
from homepage import HomePage
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = HomePage()
    main.show()
    sys.exit(app.exec_())
