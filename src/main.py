"""

main.py

Main entry point for the MaRMAT application.

Author:
    - Aiden deBoer

Date: 2025-06-18

"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from controllers.gui_controller import MainController


def main():
    """Main function to run the command line interface."""

    app = QApplication(sys.argv)

    # Set default font
    default_font = QFont("Calibri", 18)  # Set font family and size
    app.setFont(default_font)


    # Load the main controller
    controller = MainController()
    controller.run()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()