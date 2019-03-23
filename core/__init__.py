import sys
from PyQt5.QtWidgets import QApplication

from core import gui #, server, client

class Run(object):
    def __init__(self):
        App = QApplication(sys.argv)
        window = gui.MainWindow()   
        window.exec()
        sys.exit(App.exec())
