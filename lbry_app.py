import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit

import pathlib
import lbrytools as lbryt

class DownloadWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        if parent is not None:
            self.parent = parent
        self.initUI()

    def initUI(self):
        # Create a label and a line edit for URI input
        label_uri = QLabel('Enter URI:', self)
        self.edit_uri = QLineEdit(self)

        # Create a button for download
        btn_download = QPushButton('Download', self)
        btn_download.clicked.connect(self.downloadMedia)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(label_uri)
        layout.addWidget(self.edit_uri)
        layout.addWidget(btn_download)

        # Create a central widget and set the layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set window properties
        self.setGeometry(350, 350, 300, 120)
        self.setWindowTitle('Download URI')

    def downloadMedia(self):
        uri = self.edit_uri.text()
        ddir = str(pathlib.Path.home() / "Downloads")
        own_dir = True

        print(f"Downloading media from URI: {uri} to {ddir}")
        lbrynet_get_return = lbryt.download_single(uri, ddir, own_dir)
        # lbrynet_get_return includes these fields:
        #   - download_directory
        #   - metadata
        #   - title



if __name__ == '__main__':
    app = QApplication(sys.argv)
    lbry_app = DownloadWindow()
    lbry_app.show()
    sys.exit(app.exec_())

