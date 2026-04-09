
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QSplitter, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
import pandas as pd

from core import analytics, export as exp
from ui.widgets import DataTable, ExportBar, StatCard
from ui.charts import bar_chart, pie_chart, heatmap_chart, line_chart
from ui.theme import COLORS


class SeverityPage(QWidget):
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
        title = QLabel("Анализ критичности")
        title.setObjectName("page-title")
        hdr.addWidget(title)
        hdr.addStretch()
        btn = QPushButton("↻ Обновить")
        btn.setObjectName("btn-secondary")
        btn.clicked.connect(self.refresh)
        hdr.addWidget(btn)
        root.addLayout(hdr)


        self._cards_row = QHBoxLayout()
        self._cards_row.setSpacing(12)
        root.addLayout(self._cards_row)

        tabs = QTabWidget()
        root.addWidget(tabs, 1)

        tabs.addTab(self._build_dist_tab(), "Распределение")
        tabs.addTab(self._build_cvss_tab(), "CVSS")
        tabs.addTab(self._build_cwe_tab(), "CWE")
        tabs.addTab(self._build_unpatched_tab(), "Критические без патча")

    def _build_dist_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("severity", "csv"),
            on_excel=lambda: self._export("severity", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._sev_pie_w = QWidget()
        self._sev_pie_l = QVBoxLayout(self._sev_pie_w)
        self._sev_pie_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._sev_pie_w)

        self._sev_bar_w = QWidget()
        self._sev_bar_l = QVBoxLayout(self._sev_bar_w)
        self._sev_bar_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._sev_bar_w)

        splitter.setSizes([400, 500])
        layout.addWidget(splitter, 1)
        return w

    def _build_cvss_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Распределение числовых оценок CVSS (по баллам)")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("cvss", "csv"),
            on_excel=lambda: self._export("cvss", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Vertical)
        self._cvss_chart_w = QWidget()
        self._cvss_chart_l = QVBoxLayout(self._cvss_chart_w)
        self._cvss_chart_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._cvss_chart_w)

        self._cvss_table = DataTable()
        splitter.addWidget(self._cvss_table)
        splitter.setSizes([320, 200])
        layout.addWidget(splitter, 1)
        return w

    def _build_cwe_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel("Топ типов ошибок CWE и их распределение по уровню опасности")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("cwe", "csv"),
            on_excel=lambda: self._export("cwe", "excel"),
        ))

        splitter = QSplitter(Qt.Orientation.Vertical)
        self._cwe_chart_w = QWidget()
        self._cwe_chart_l = QVBoxLayout(self._cwe_chart_w)
        self._cwe_chart_l.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._cwe_chart_w)

        splitter2 = QSplitter(Qt.Orientation.Horizontal)
        self._cwe_heat_w = QWidget()
        self._cwe_heat_l = QVBoxLayout(self._cwe_heat_w)
        self._cwe_heat_l.setContentsMargins(0, 0, 0, 0)
        splitter2.addWidget(self._cwe_heat_w)

        self._cwe_table = DataTable()
        splitter2.addWidget(self._cwe_table)
        splitter2.setSizes([500, 400])

        splitter.addWidget(splitter2)
        splitter.setSizes([300, 380])
        layout.addWidget(splitter, 1)
        return w

    def _build_unpatched_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lbl = QLabel(
            "⚠  Критические уязвимости без информации об устранении "
            "(наиболее опасные активные угрозы)"
        )
        lbl.setStyleSheet(f"color: {COLORS['accent_orange']}; font-size: 12px;")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        layout.addWidget(ExportBar(
            on_csv=lambda: self._export("unpatched", "csv"),
            on_excel=lambda: self._export("unpatched", "excel"),
        ))

        self._unpatched_table = DataTable()
        layout.addWidget(self._unpatched_table, 1)
        return w


    def refresh(self):
        self._load_severity()
        self._load_cvss()
        self._load_cwe()
        self._load_unpatched()
        self._update_cards()

    def _update_cards(self):
        while self._cards_row.count():
            item = self._cards_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        df = self._dfs.get("severity")
        if df is None or df.empty:
            return
        sev_map = dict(zip(df["severity"], df["count"]))
        total = df["count"].sum()

        configs = [
            ("Критический", COLORS["sev_critical"]),
            ("Высокий",     COLORS["sev_high"]),
            ("Средний",     COLORS["sev_medium"]),
            ("Низкий",      COLORS["sev_low"]),
        ]
        for sev, color in configs:
            cnt = sev_map.get(sev, 0)
            pct = f"{cnt / total * 100:.1f}%" if total else "0%"
            card = StatCard(sev, f"{cnt:,}\n{pct}", color)
            self._cards_row.addWidget(card)

    def _load_severity(self):
        try:
            df = analytics.severity_distribution()
            self._dfs["severity"] = df
            if df.empty:
                return
            pie = pie_chart(df, "severity", "count",
                            title="Доля уязвимостей по уровню опасности",
                            figsize=(6, 5))
            bar = bar_chart(df, "severity", "count",
                            title="Количество уязвимостей по уровню опасности",
                            figsize=(6, 4))
            self._replace(self._sev_pie_l, pie)
            self._replace(self._sev_bar_l, bar)
        except Exception as e:
            self.status_message.emit(f"Ошибка (severity): {e}")

    def _load_cvss(self):
        try:
            df = analytics.cvss_distribution()
            self._dfs["cvss"] = df
            if df.empty:
                return
            df["score_bucket"] = df["score_bucket"].astype(str)
            chart = bar_chart(df, "score_bucket", "count",
                              title="Распределение CVSS оценок",
                              figsize=(10, 4))
            self._replace(self._cvss_chart_l, chart)
            self._cvss_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (cvss): {e}")

    def _load_cwe(self):
        try:
            cwe_df = analytics.top_cwe(20)
            self._dfs["cwe"] = cwe_df
            if cwe_df.empty:
                return

            chart = bar_chart(cwe_df, "cwe_type", "count",
                              title="Топ 20 типов ошибок CWE",
                              horizontal=True, figsize=(9, 6))
            self._replace(self._cwe_chart_l, chart)
            self._cwe_table.load_dataframe(cwe_df)


            heat_df = analytics.cwe_by_severity()
            if not heat_df.empty:
                top_cwes = cwe_df["cwe_type"].head(15).tolist()
                heat_df = heat_df[heat_df["cwe_type"].isin(top_cwes)]
                pivot = heat_df.pivot_table(
                    index="cwe_type", columns="severity",
                    values="count", fill_value=0
                )
                col_order = ["Критический", "Высокий", "Средний", "Низкий"]
                pivot = pivot[[c for c in col_order if c in pivot.columns]]
                hmap = heatmap_chart(pivot,
                                     title="CWE × Уровень опасности (топ 15)",
                                     figsize=(7, 6))
                self._replace(self._cwe_heat_l, hmap)
        except Exception as e:
            self.status_message.emit(f"Ошибка (cwe): {e}")

    def _load_unpatched(self):
        try:
            df = analytics.unpatched_critical()
            self._dfs["unpatched"] = df
            self._unpatched_table.load_dataframe(df)
        except Exception as e:
            self.status_message.emit(f"Ошибка (unpatched): {e}")

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
                path = exp.export_csv(df, f"severity_{dataset}")
            else:
                path = exp.export_excel({dataset: df}, f"severity_{dataset}")
            self.status_message.emit(f"✓ Сохранено: {path}")
        except Exception as e:
            self.status_message.emit(f"Ошибка экспорта: {e}")
