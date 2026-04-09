
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

from core import database as db
from ui.theme import COLORS


class LoaderWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def run(self):
        try:
            count = db.load_xlsx(self.path, self.progress.emit)
            self.finished.emit(count)
        except Exception as e:
            self.error.emit(str(e))


class LoaderPage(QWidget):
    load_complete = pyqtSignal(int)
    go_back = pyqtSignal()

    def __init__(self, parent=None, show_back: bool = False):
        super().__init__(parent)
        self._worker = None
        self._show_back = show_back
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)


        if self._show_back:
            top_bar = QWidget()
            top_bar.setFixedHeight(50)
            top_layout = QHBoxLayout(top_bar)
            top_layout.setContentsMargins(16, 8, 16, 8)
            back_btn = QPushButton("← Назад")
            back_btn.setObjectName("btn-secondary")
            back_btn.setFixedWidth(110)
            back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            back_btn.clicked.connect(self.go_back.emit)
            top_layout.addWidget(back_btn)
            top_layout.addStretch()
            root.addWidget(top_bar)


        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(560)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel("[ БДУ ]")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {COLORS['accent_blue']}; letter-spacing: 4px;"
        )
        card_layout.addWidget(icon_lbl)

        title = QLabel("БДУ ФСТЭК Анализатор")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {COLORS['text_primary']}; letter-spacing: 1px;"
        )
        card_layout.addWidget(title)

        subtitle = QLabel("Инструмент анализа Банка данных угроз безопасности информации")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"font-size: 13px; color: {COLORS['text_secondary']};")
        card_layout.addWidget(subtitle)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {COLORS['border']};")
        line.setFixedHeight(1)
        card_layout.addWidget(line)

        info = QLabel(
            "Загрузите файл экспорта БДУ ФСТЭК в формате .xlsx\n"
            "для начала работы с аналитическим модулем.\n\n"
            "Первичная загрузка займёт 1-3 минуты (~85 000 записей)."
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        info.setStyleSheet(f"font-size: 13px; color: {COLORS['text_secondary']}; line-height: 1.6;")
        card_layout.addWidget(info)

        self._load_btn = QPushButton("Выбрать XLSX файл БДУ ФСТЭК")
        self._load_btn.setObjectName("btn-primary")
        self._load_btn.setMinimumHeight(44)
        self._load_btn.setFont(QFont("", 13))
        self._load_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._load_btn.clicked.connect(self._choose_file)
        card_layout.addWidget(self._load_btn)

        self._status_lbl = QLabel("")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        self._status_lbl.setWordWrap(True)
        card_layout.addWidget(self._status_lbl)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        self._progress.setFixedHeight(6)
        card_layout.addWidget(self._progress)

        if db.is_db_loaded():
            hint = QLabel("База данных уже загружена. Загрузить другой файл?")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setStyleSheet(f"font-size: 11px; color: {COLORS['accent_green']};")
            card_layout.addWidget(hint)

        center_layout.addWidget(card)
        root.addWidget(center_widget, 1)

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл БДУ ФСТЭК", "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if not path:
            return
        self._start_load(path)

    def _start_load(self, path: str):
        self._load_btn.setEnabled(False)
        self._load_btn.setText("Загрузка...")
        self._status_lbl.setText(f"Файл: {path}")
        self._progress.setVisible(True)

        self._worker = LoaderWorker(path)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, msg: str):
        self._status_lbl.setText(msg)

    def _on_finished(self, count: int):
        self._progress.setVisible(False)
        self._load_btn.setEnabled(True)
        self._load_btn.setText("Выбрать другой файл")
        self._status_lbl.setText(f"Загружено {count:,} уязвимостей. Переход к аналитике...")
        self._status_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS['accent_green']};")
        self.load_complete.emit(count)

    def _on_error(self, error: str):
        self._progress.setVisible(False)
        self._load_btn.setEnabled(True)
        self._load_btn.setText("Выбрать XLSX файл БДУ ФСТЭК")
        self._status_lbl.setText(f"Ошибка: {error}")
        self._status_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS['accent_red']};")
