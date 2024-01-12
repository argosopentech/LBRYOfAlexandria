import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QMessageBox

import pathlib
import lbrytools as lbryt
import json

class LBRYApp(QMainWindow):
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

        # Create a central widget and set the layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set window properties
        self.setGeometry(300, 300, 300, 120)
        self.setWindowTitle('LBRY Search Demo')

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    lbry_app = LBRYApp()
    lbry_app.show()
    sys.exit(app.exec_())


