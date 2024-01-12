import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit

import pathlib
import lbrytools as lbryt

class LBRYOfAlexandria(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel('LBRY of Alex', self)

        layout = QVBoxLayout()
        layout.addWidget(label)

        self.central_widget = QWidget(self)
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        self.setGeometry(350, 350, 300, 120)
        self.setWindowTitle('LBRY of Alexandria')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    lbry_app = LBRYOfAlexandria()
    lbry_app.show()
    sys.exit(app.exec_())

