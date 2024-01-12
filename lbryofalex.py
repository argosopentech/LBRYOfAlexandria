import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QMessageBox

import pathlib
import lbrytools as lbryt
import json

class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a QLineEdit for search input
        self.edit_search = QLineEdit(self)

        # Create a button
        btn_search = QPushButton('Search', self)
        btn_search.clicked.connect(self.searchClaims)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.edit_search)
        layout.addWidget(btn_search)
        self.setLayout(layout)

    def searchClaims(self):
        # Get the search string from the QLineEdit
        search_text = self.edit_search.text()

        # Perform LBRY search
        results = lbryt.list_search_claims(text=search_text)

        # Extract the canonical_url field from the first claim (if available)
        claims = results.get('claims', [{}])
        parsed_claims = []
        for claim in claims:
            canonical_url = claim.get('canonical_url', 'Not found')
            parsed_claims.append(canonical_url)


        search_results = "\n".join(parsed_claims) if parsed_claims else "No results found"

        # Display the canonical_url in a QMessageBox
        QMessageBox.information(self, 'Search Results', search_results)

class LBRYOfAlexandria(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel('LBRY of Alex', self)

        self.search_widget = SearchWidget()

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.search_widget)

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

