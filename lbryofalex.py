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
    QMessageBox,
)

import lbrytools as lbryt


class LBRYOfAlexandria(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel("LBRY of Alexandria", self)

        self.search_widget = SearchWidget(self)
        self.search_widget.list_widget.itemClicked.connect(
            self.search_widget.showClaimDetails
        )

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.search_widget)

        self.central_widget = QWidget(self)
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        self.setGeometry(350, 350, 800, 600)
        self.setWindowTitle("LBRY of Alexandria")


class SearchWidget(QWidget):
    LIST_ITEM_URI_ROLE = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
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
            canonical_url = claim.get("canonical_url")
            if canonical_url is None:
                continue
            item_text = f"({amount:.2f}) {canonical_url}"
            list_item = QListWidgetItem(item_text)
            list_item.setData(self.LIST_ITEM_URI_ROLE, claim["canonical_url"])
            self.list_widget.addItem(list_item)
            list_item.setFlags(list_item.flags() | 2)  # Make item selectable

    def showClaimDetails(self, item):
        uri = item.data(self.LIST_ITEM_URI_ROLE)
        if uri:
            print("PJDEBUG: showClaimDetails")
            claim_details_widget = ClaimDetailsWidget(uri, parent=self.parent)
            claim_details_widget.setWindowTitle(f"Claim Details - {uri}")
            print("About to show claim details widget")
            claim_details_widget.show()
            print("Claim details widget shown")


class ClaimDetailsWidget(QWidget):
    def __init__(self, uri, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI(uri)

    def initUI(self, uri):
        # Create a QLabel to display URI
        uri_label = QLabel(f"URI: {uri}", self)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(uri_label)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    lbry_app = LBRYOfAlexandria()
    lbry_app.show()
    print("About to enter the event loop")
    sys.exit(app.exec_())
    print("Exited the event loop")  # This line should not be reached
