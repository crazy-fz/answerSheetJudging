import sys
from PyQt5.QtWidgets import QApplication,QWidget
from PyQt5.QtWidgets import QMainWindow
from mainwindow import *

if __name__ == "__main__":
    app=QApplication(sys.argv)
    mainwindow=QMainWindow()
    ui=Ui_MainWindow()
    ui.setupUi(mainwindow)
    mainwindow.show()
    sys.exit(app.exec())