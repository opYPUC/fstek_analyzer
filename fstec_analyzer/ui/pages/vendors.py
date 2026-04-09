
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton, QComboBox,
    QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
import pandas as pd

from core import analytics, export as exp
from ui.widgets import SectionHeader, DataTable, ExportBar
from ui.charts import bar_chart, pie_chart
from ui.theme import COLORS


class VendorsPage(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)


        hdr = QHBoxLayout()
        title = QLabel("Анализ вендоров и ПО")
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

        self._vendors_tab = self._build_vendors_tab()
        self._software_tab = self._build_software_tab()
        self._fix_rate_tab = self._build_fix_rate_tab()
        self._critical_vendors_tab = self._build_critical_vendors_tab()

        tabs.addTab(self._vendors_tab, "Топ вендоров")
        tabs.addTab(self._software_tab, "Топ ПО")
        tabs.addTab(self._fix_rate_tab, "Скорость устранения")
        tabs.addTab(self._critical_vendors_tab, "Критические уязвимости")

    def _build_vendors_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)


        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Показать топ:"))
        self._vendor_limit = QComboBox()
        for n in [10, 20, 30, 50]:
            self._vendor_limit.addItem(str(n), n)
        self._vendor_limit.setCurrentIndex(1)
        self._vendor_limit.currentIndexChanged.connect(self._reload_vendors)
        ctrl.addWidget(self._vendor_limit)
        ctrl.addStretch()

        export_bar = ExportBar(
            on_csv=lambda: self._export("vendors", "csv"),
            on_excel=lambda: self._export("vendors", "excel"),
        )
        ctrl.addWidget(export_bar)
        layout.addLayout(ctrl)


        splitter = QSplitter(Qt.Orientation.Vertical)

        self._vendor_chart_container = QWidget()
        self._vendor_chart_layout = QVBoxLayout(self._vendor_chart_container)
        self._vendor_chart_layout.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._vendor_chart_container)

        self._vendor_table = DataTable()
        splitter.addWidget(self._vendor_table)
        splitter.setSizes([350, 250])

        layout.addWidget(splitter, 1)
        return w

    def _build_software_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Показать топ:"))
        self._sw_limit = QComboBox()
        for n in [10, 20, 30, 50]:
            self._sw_limit.addItem(str(n), n)
        self._sw_limit.setCurrentIndex(1)
        self._sw_limit.currentIndexChanged.connect(self._reload_software)
        ctrl.addWidget(self._sw_limit)
        ctrl.addStretch()
        export_bar = ExportBar(
            on_csv=lambda: self._export("software", "csv"),
            on_excel=lambda: self._export("software", "excel"),
        )
        ctrl.addWidget(export_bar)
        layout.addLayout(ctrl)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self._sw_chart_container = QWidget()
        self._sw_chart_layout = QVBoxLayout(self._sw_chart_container)
        self._sw_chart_layout.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._sw_chart_container)

        self._sw_table = DataTable()
        splitter.addWidget(self._sw_table)
        splitter.setSizes([350, 250])

        layout.addWidget(splitter, 1)
        return w

    def _build_fix_rate_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Процент устранённых уязвимостей по вендорам (мин. 50 уязвимостей)")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        export_bar = ExportBar(
            on_csv=lambda: self._export("fix_rate", "csv"),
            on_excel=lambda: self._export("fix_rate", "excel"),
        )
        layout.addWidget(export_bar)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self._fix_chart_container = QWidget()
        self._fix_chart_layout = QVBoxLayout(self._fix_chart_container)
        self._fix_chart_layout.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._fix_chart_container)

        self._fix_table = DataTable()
        splitter.addWidget(self._fix_table)
        splitter.setSizes([300, 250])

        layout.addWidget(splitter, 1)
        return w

    def _build_critical_vendors_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Вендоры с наибольшим числом критических уязвимостей")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        export_bar = ExportBar(
            on_csv=lambda: self._export("critical_vendors", "csv"),
            on_excel=lambda: self._export("critical_vendors", "excel"),
        )
        layout.addWidget(export_bar)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self._crit_chart_container = QWidget()
        self._crit_chart_layout = QVBoxLayout(self._crit_chart_container)
        self._crit_chart_layout.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._crit_chart_container)

        self._crit_table = DataTable()
        splitter.addWidget(self._crit_table)
        splitter.setSizes([300, 250])

        layout.addWidget(splitter, 1)
        return w


    def refresh(self):
        self._reload_vendors()
        self._reload_software()
        self._reload_fix_rate()
        self._reload_critical()

    def _reload_vendors(self):
        try:
            limit = self._vendor_limit.currentData()
            self._vendors_df = analytics.top_vendors(limit)
            self._replace_chart(self._vendor_chart_layout,
                bar_chart(self._vendors_df, "vendor", "count",
                          title=f"Топ {limit} вендоров",
                          horizontal=True, figsize=(9, max(4, limit * 0.35))))
            self._vendor_table.load_dataframe(self._vendors_df)
        except Exception as e:
            self.status_message.emit(f"Ошибка: {e}")

    def _reload_software(self):
        try:
            limit = self._sw_limit.currentData()
            self._sw_df = analytics.top_software(limit)
            self._replace_chart(self._sw_chart_layout,
                bar_chart(self._sw_df, "software", "count",
                          title=f"Топ {limit} ПО",
                          horizontal=True, figsize=(9, max(4, limit * 0.35))))
            self._sw_table.load_dataframe(self._sw_df)
        except Exception as e:
            self.status_message.emit(f"Ошибка: {e}")

    def _reload_fix_rate(self):
        try:
            self._fix_df = analytics.vendor_fix_rate(20)
            self._replace_chart(self._fix_chart_layout,
                bar_chart(self._fix_df, "vendor", "fix_rate",
                          title="% устранённых уязвимостей (топ 20 вендоров)",
                          horizontal=True, figsize=(9, 7)))
            self._fix_table.load_dataframe(self._fix_df)
        except Exception as e:
            self.status_message.emit(f"Ошибка: {e}")

    def _reload_critical(self):
        try:
            self._crit_df = analytics.critical_vendors(15)
            self._replace_chart(self._crit_chart_layout,
                bar_chart(self._crit_df, "vendor", "critical_count",
                          title="Критические уязвимости по вендорам",
                          horizontal=True, figsize=(9, 5)))
            self._crit_table.load_dataframe(self._crit_df)
        except Exception as e:
            self.status_message.emit(f"Ошибка: {e}")

    def _replace_chart(self, layout, new_chart):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        layout.addWidget(new_chart)

    def _export(self, dataset: str, fmt: str):
        df_map = {
            "vendors": getattr(self, "_vendors_df", None),
            "software": getattr(self, "_sw_df", None),
            "fix_rate": getattr(self, "_fix_df", None),
            "critical_vendors": getattr(self, "_crit_df", None),
        }
        df = df_map.get(dataset)
        if df is None or df.empty:
            self.status_message.emit("Нет данных для экспорта")
            return
        try:
            if fmt == "csv":
                path = exp.export_csv(df, dataset)
            else:
                path = exp.export_excel({dataset: df}, dataset)
            self.status_message.emit(f"✓ Сохранено: {path}")
        except Exception as e:
            self.status_message.emit(f"Ошибка экспорта: {e}")
