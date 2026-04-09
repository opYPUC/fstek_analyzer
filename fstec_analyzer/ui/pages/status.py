
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from core import analytics, export as exp
from ui.widgets import DataTable, ExportBar
from ui.charts import bar_chart, pie_chart, line_chart
from ui.theme import COLORS


class StatusPage(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dfs = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("Статусы и устранение")
        title.setObjectName("page-title")
        hdr.addWidget(title)
        hdr.addStretch()
        btn = QPushButton("↻ Обновить")
        btn.setObjectName("btn-secondary")
        btn.clicked.connect(self.refresh)
        hdr.addWidget(btn)
        root.addLayout(hdr)

        tabs = QTabWidget()
        root.addWidget(tabs, 1)

        tabs.addTab(self._build_status_tab(), "Статусы")
        tabs.addTab(self._build_fix_tab(), "Устранение")
        tabs.addTab(self._build_exploit_tab(), "Эксплойты")
        tabs.addTab(self._build_swtype_tab(), "Типы ПО")

    def _build_status_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Распределение уязвимостей по статусу подтверждения")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("status", "csv"),
            on_excel=lambda: self._export("status", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._status_pie_w = QWidget()
        self._status_pie_l = QVBoxLayout(self._status_pie_w)
        self._status_pie_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._status_pie_w)

        self._status_table = DataTable()
        splitter.addWidget(self._status_table)
        splitter.setSizes([450, 350])
        layout.addWidget(splitter, 1)
        return w

    def _build_fix_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Информация об устранении уязвимостей")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("fix_info", "csv"),
            on_excel=lambda: self._export("fix_info", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._fix_pie_w = QWidget()
        self._fix_pie_l = QVBoxLayout(self._fix_pie_w)
        self._fix_pie_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._fix_pie_w)

        self._fix_table = DataTable()
        splitter.addWidget(self._fix_table)
        splitter.setSizes([450, 350])
        layout.addWidget(splitter, 1)
        return w

    def _build_exploit_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Наличие публично известных эксплойтов")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("exploit", "csv"),
            on_excel=lambda: self._export("exploit", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._exploit_pie_w = QWidget()
        self._exploit_pie_l = QVBoxLayout(self._exploit_pie_w)
        self._exploit_pie_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._exploit_pie_w)

        self._exploit_table = DataTable()
        splitter.addWidget(self._exploit_table)
        splitter.setSizes([450, 350])
        layout.addWidget(splitter, 1)
        return w

    def _build_swtype_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Распределение уязвимостей по типу ПО")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("swtype", "csv"),
            on_excel=lambda: self._export("swtype", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Vertical)
        self._swtype_chart_w = QWidget()
        self._swtype_chart_l = QVBoxLayout(self._swtype_chart_w)
        self._swtype_chart_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._swtype_chart_w)

        self._swtype_table = DataTable()
        splitter.addWidget(self._swtype_table)
        splitter.setSizes([340, 200])
        layout.addWidget(splitter, 1)
        return w


    def refresh(self):
        self._load_status()
        self._load_fix_info()
        self._load_exploit()
        self._load_swtype()

    def _load_status(self):
        try:
            df = analytics.status_distribution()
            self._dfs["status"] = df
            chart = pie_chart(df, "status", "count",
                              title="Статус уязвимостей",
                              figsize=(7, 5))
            self._replace(self._status_pie_l, chart)
            self._status_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (status): {e}")

    def _load_fix_info(self):
        try:
            df = analytics.fix_info_distribution()
            self._dfs["fix_info"] = df
            chart = pie_chart(df, "fix_info", "count",
                              title="Информация об устранении",
                              figsize=(7, 5))
            self._replace(self._fix_pie_l, chart)
            self._fix_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (fix_info): {e}")

    def _load_exploit(self):
        try:
            df = analytics.exploit_distribution()
            self._dfs["exploit"] = df
            chart = pie_chart(df, "exploit", "count",
                              title="Наличие эксплойта",
                              figsize=(7, 5))
            self._replace(self._exploit_pie_l, chart)
            self._exploit_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (exploit): {e}")

    def _load_swtype(self):
        try:
            df = analytics.software_type_distribution()
            self._dfs["swtype"] = df
            chart = bar_chart(df, "software_type", "count",
                              title="Топ типов ПО",
                              horizontal=True, figsize=(10, 5))
            self._replace(self._swtype_chart_l, chart)
            self._swtype_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (swtype): {e}")

    def _replace(self, layout, widget):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        layout.addWidget(widget)

    def _export(self, dataset: str, fmt: str):
        df = self._dfs.get(dataset)
        if df is None or df.empty:
            self.status_message.emit("Нет данных для экспорта")
            return
        try:
            if fmt == "csv":
                path = exp.export_csv(df, f"status_{dataset}")
            else:
                path = exp.export_excel({dataset: df}, f"status_{dataset}")
            self.status_message.emit(f"✓ Сохранено: {path}")
        except Exception as e:
            self.status_message.emit(f"Ошибка экспорта: {e}")
