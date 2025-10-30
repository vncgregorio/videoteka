"""Main entry point for the Videoteka application."""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from version import get_version


def main():
    """Run the application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Videoteka")
    app.setOrganizationName("Videoteka")
    app.setApplicationVersion(get_version())
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

