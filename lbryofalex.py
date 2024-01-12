import sys
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
)

import lbrytools as lbryt


class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a QLineEdit for search input
        self.edit_search = QLineEdit(self)
        self.edit_search.returnPressed.connect(self.searchClaims)

        # Create a button
        btn_search = QPushButton("Search", self)
        btn_search.clicked.connect(self.searchClaims)

        # Create a QListWidget to display search results
        self.list_widget = QListWidget()

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.edit_search)
        layout.addWidget(btn_search)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def searchClaims(self):
        search_text = self.edit_search.text()
        results = lbryt.list_search_claims(text=search_text)
        self.list_widget.clear()
        claims = results.get("claims", [{}])
        claims.sort(key=lambda claim: float(claim.get("amount", "0")), reverse=True)
        for claim in claims:
            amount = float(claim.get("amount", "0"))
            canonical_url = claim.get("canonical_url", "Canonical URL not found")
            item_text = f"({amount:.2f}) {canonical_url}"
            list_item = QListWidgetItem(item_text)
            self.list_widget.addItem(list_item)


class LBRYOfAlexandria(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel("LBRY of Alex", self)

        self.search_widget = SearchWidget()

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.search_widget)

        self.central_widget = QWidget(self)
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        self.setGeometry(350, 350, 400, 300)
        self.setWindowTitle("LBRY of Alexandria")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    lbry_app = LBRYOfAlexandria()
    lbry_app.show()
    sys.exit(app.exec_())
