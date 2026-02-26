"""Dialog showing full error details for a failed download."""
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt


class ErrorDetailsDialog(QDialog):
    """Modal dialog that shows video title, URL, and full error message."""

    def __init__(self, title: str, url: str, error_message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error details")
        self.setMinimumSize(480, 320)
        self.resize(560, 400)

        layout = QVBoxLayout(self)

        # Context: video title and URL
        self._title_label = QLabel()
        self._title_label.setWordWrap(True)
        self._title_label.setText(f"Video: {title}")
        layout.addWidget(self._title_label)

        self._url_label = QLabel()
        self._url_label.setWordWrap(True)
        self._url_label.setOpenExternalLinks(True)
        self._url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._url_label.setText(f"URL: {url}")
        layout.addWidget(self._url_label)

        # Full error text (scrollable, selectable)
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setPlaceholderText("No error message recorded.")
        if error_message:
            self._text.setPlainText(error_message)
        layout.addWidget(self._text)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
