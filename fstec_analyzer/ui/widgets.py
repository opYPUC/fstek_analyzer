
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

import pandas as pd
from ui.theme import COLORS, SEVERITY_COLORS


class StatCard(QFrame):

    def __init__(self, label: str, value: str, color: str = None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumWidth(150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)


        accent = color or COLORS["accent_blue"]
        self.setStyleSheet(
            f"QFrame#card {{ border-top: 3px solid {accent}; }}"
        )

        val_label = QLabel(value)
        val_label.setObjectName("card-value")
        val_label.setStyleSheet(f"color: {accent}; font-size: 30px; font-weight: bold;")
        layout.addWidget(val_label)

        lbl = QLabel(label.upper())
        lbl.setObjectName("card-label")
        layout.addWidget(lbl)

        self.value_label = val_label

    def update_value(self, value: str):
        self.value_label.setText(value)


class SectionHeader(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("section-header")


class DataTable(QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(True)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setStyleSheet(f"""
            QTableWidget {{ alternate-background-color: {COLORS['bg_input']}; }}

        """)
    def __init__(self, on_csv=None, on_excel=None, on_json=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Экспорт:"))
        layout.addWidget(QLabel("", objectName="filler"))

        if on_csv:
            btn = QPushButton("⬇ CSV")
            btn.setObjectName("btn-secondary")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(on_csv)
            layout.addWidget(btn)

        if on_excel:
            btn = QPushButton("⬇ Excel")
            btn.setObjectName("btn-success")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(on_excel)
            layout.addWidget(btn)

        if on_json:
            btn = QPushButton("⬇ JSON")
            btn.setObjectName("btn-secondary")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(on_json)
            layout.addWidget(btn)

        layout.addStretch()


def make_label(text: str, color: str = None, bold: bool = False, size: int = 13) -> QLabel:
    lbl = QLabel(text)
    style = f"font-size: {size}px;"
    if color:
        style += f" color: {color};"
    if bold:
        style += " font-weight: bold;"
    lbl.setStyleSheet(style)
    return lbl
