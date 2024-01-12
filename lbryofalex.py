import sys
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
)

import pathlib
import lbrytools as lbryt
from lbrytools import download_single


class LBRYOfAlexandria(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        label = QLabel("LBRY of Alexandria", self)

        # Create a SearchWidget for LBRY claims search
        self.search_widget = SearchWidget(self)
        self.search_widget.list_widget.itemClicked.connect(
            self.search_widget.showClaimDetails
        )

        # Create a DownloadWidget for LBRY URI download
        self.download_widget = DownloadWidget(self)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.search_widget)
        layout.addWidget(self.download_widget)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(350, 350, 800, 600)
        self.setWindowTitle("LBRY of Alexandria")


class DownloadWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        label = QLabel("Download URI", self)

        # Create a QLineEdit for URI input
        self.edit_uri = QLineEdit(self)

        # Create a button for download
        btn_download = QPushButton("Download", self)
        btn_download.clicked.connect(self.downloadURI)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.edit_uri)
        layout.addWidget(btn_download)
        self.setLayout(layout)

    def downloadURI(self):
        uri = self.edit_uri.text()
        ddir = str(pathlib.Path.home() / "Documents" / "LBRYOfAlexandria")
        pathlib.Path(ddir).mkdir(parents=True, exist_ok=True)
        own_dir = True
        # Includes: download_path, channel_name, channel_claim_id, claim_name, content_fee
        #          download_directory, download_path, metadata, title, streaming_url
        result = lbryt.download_single(uri, ddir, own_dir)
        QMessageBox.information(self, "Download Result", f"Download result: {result}")


class SearchWidget(QWidget):
    LIST_ITEM_URI_ROLE = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.edit_search = QLineEdit(self)
        self.edit_search.returnPressed.connect(self.searchClaims)

        btn_search = QPushButton("Search", self)
        btn_search.clicked.connect(self.searchClaims)

        self.list_widget = QListWidget(self)
        self.list_widget.itemClicked.connect(self.showClaimDetails)

        self.claim_details_label = QLabel("Claim Details", self)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.edit_search)
        layout.addWidget(btn_search)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.claim_details_label)
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
            list_item.setFlags(list_item.flags() | 2)  # Make item selectable
            self.list_widget.addItem(list_item)

    def showClaimDetails(self, item):
        uri = item.data(self.LIST_ITEM_URI_ROLE)
        if uri:
            self.claim_details_label.setText(uri)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    lbry_app = LBRYOfAlexandria()
    lbry_app.show()
    sys.exit(app.exec_())
