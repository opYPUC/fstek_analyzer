
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
import pandas as pd

from core import analytics, export as exp
from ui.widgets import DataTable, ExportBar
from ui.charts import line_chart, bar_chart, stacked_bar
from ui.theme import COLORS


class TimelinePage(QWidget):
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
        title = QLabel("Временной анализ")
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

        tabs.addTab(self._build_yearly_tab(), "По годам")
        tabs.addTab(self._build_severity_trend_tab(), "Тренд критичности")
        tabs.addTab(self._build_exploit_trend_tab(), "Тренд эксплойтов")
        tabs.addTab(self._build_lag_tab(), "Время до публикации")


    def _build_yearly_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Количество опубликованных уязвимостей по годам")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("yearly", "csv"),
            on_excel=lambda: self._export("yearly", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Vertical)
        self._yearly_chart_w = QWidget()
        self._yearly_chart_l = QVBoxLayout(self._yearly_chart_w)
        self._yearly_chart_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._yearly_chart_w)

        self._yearly_table = DataTable()
        splitter.addWidget(self._yearly_table)
        splitter.setSizes([350, 200])
        layout.addWidget(splitter, 1)
        return w

    def _build_severity_trend_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Распределение уязвимостей по уровню опасности в динамике")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("sev_trend", "csv"),
            on_excel=lambda: self._export("sev_trend", "excel"),
        ))

        self._sev_trend_chart_w = QWidget()
        self._sev_trend_chart_l = QVBoxLayout(self._sev_trend_chart_w)
        self._sev_trend_chart_l.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._sev_trend_chart_w, 1)
        return w

    def _build_exploit_trend_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Доля уязвимостей с публично известным эксплойтом по годам")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("exploit_trend", "csv"),
            on_excel=lambda: self._export("exploit_trend", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Vertical)
        self._exploit_chart_w = QWidget()
        self._exploit_chart_l = QVBoxLayout(self._exploit_chart_w)
        self._exploit_chart_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._exploit_chart_w)

        self._exploit_table = DataTable()
        splitter.addWidget(self._exploit_table)
        splitter.setSizes([320, 200])
        layout.addWidget(splitter, 1)
        return w

    def _build_lag_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Среднее время (в годах) между датой обнаружения и публикацией в БДУ")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("lag", "csv"),
            on_excel=lambda: self._export("lag", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Vertical)
        self._lag_chart_w = QWidget()
        self._lag_chart_l = QVBoxLayout(self._lag_chart_w)
        self._lag_chart_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._lag_chart_w)

        self._lag_table = DataTable()
        splitter.addWidget(self._lag_table)
        splitter.setSizes([320, 200])
        layout.addWidget(splitter, 1)
        return w


    def refresh(self):
        self._load_yearly()
        self._load_severity_trend()
        self._load_exploit_trend()
        self._load_lag()

    def _load_yearly(self):
        try:
            df = analytics.vulns_by_year()
            self._dfs["yearly"] = df
            chart = bar_chart(df, "year", "count",
                              title="Уязвимости по годам",
                              figsize=(10, 4))
            self._replace(self._yearly_chart_l, chart)
            self._yearly_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (yearly): {e}")

    def _load_severity_trend(self):
        try:
            df = analytics.vulns_by_year_severity()
            self._dfs["sev_trend"] = df
            if df.empty:
                return
            pivot = df.pivot_table(index="year", columns="severity",
                                   values="count", fill_value=0)

            col_order = ["Критический", "Высокий", "Средний", "Низкий"]
            pivot = pivot[[c for c in col_order if c in pivot.columns]]
            chart = stacked_bar(pivot,
                                title="Уязвимости по уровню опасности и году",
                                figsize=(11, 5))
            self._replace(self._sev_trend_chart_l, chart)
        except Exception as e:
            self.status_message.emit(f"Ошибка (sev_trend): {e}")

    def _load_exploit_trend(self):
        try:
            df = analytics.exploit_trend_by_year()
            self._dfs["exploit_trend"] = df
            if not df.empty:
                df["exploit_pct"] = (df["with_exploit"] / df["total"] * 100).round(1)
                chart = line_chart(df, "year", ["with_exploit"],
                                   title="Уязвимости с эксплойтом по годам",
                                   figsize=(10, 4))
                self._replace(self._exploit_chart_l, chart)
                self._exploit_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (exploit_trend): {e}")

    def _load_lag(self):
        try:
            df = analytics.detection_to_publish_lag()
            self._dfs["lag"] = df
            if not df.empty:
                df["avg_lag_years"] = df["avg_lag_years"].round(2)
                chart = bar_chart(df, "year", "avg_lag_years",
                                  title="Среднее время обнаружение → публикация (лет)",
                                  figsize=(10, 4))
                self._replace(self._lag_chart_l, chart)
                self._lag_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (lag): {e}")

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
                path = exp.export_csv(df, f"timeline_{dataset}")
            else:
                path = exp.export_excel({dataset: df}, f"timeline_{dataset}")
            self.status_message.emit(f"✓ Сохранено: {path}")
        except Exception as e:
            self.status_message.emit(f"Ошибка экспорта: {e}")
