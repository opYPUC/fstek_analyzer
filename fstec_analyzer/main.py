
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).parent)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("БДУ ФСТЭК Анализатор")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FSTEC Analyzer")

    if sys.platform == "win32":
        default_font = QFont("Segoe UI", 13)
    else:
        default_font = QFont("", 13)
    app.setFont(default_font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
