
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
import pandas as pd

from core import analytics
from ui.widgets import StatCard, ExportBar
from ui.charts import bar_chart, pie_chart, line_chart
from ui.theme import COLORS
from core import export as exp


class DashboardPage(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)


        hdr = QHBoxLayout()
        title = QLabel("Сводная панель")
        title.setObjectName("page-title")
        hdr.addWidget(title)
        hdr.addStretch()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.setObjectName("btn-secondary")
        refresh_btn.clicked.connect(self.refresh)
        hdr.addWidget(refresh_btn)
        export_btn = QPushButton("Полный отчёт Excel")
        export_btn.setObjectName("btn-success")
        export_btn.clicked.connect(self._export_full)
        hdr.addWidget(export_btn)
        root.addLayout(hdr)


        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(10)
        root.addLayout(self.cards_layout)


        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        self.charts_layout = QVBoxLayout(scroll_content)
        self.charts_layout.setSpacing(16)
        self.charts_layout.setContentsMargins(0, 0, 4, 0)
        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

    def refresh(self):
        self._clear_layout(self.cards_layout)
        self._clear_layout(self.charts_layout)
        self._load_stats()
        self._load_charts()

    def _load_stats(self):
        try:
            s = analytics.summary_stats()
        except Exception as e:
            self.status_message.emit(f"Ошибка: {e}")
            return

        cards = [
            ("Всего уязвимостей", f"{int(s.get('total', 0)):,}",       COLORS["accent_blue"]),
            ("Критических",       f"{int(s.get('critical', 0)):,}",    COLORS["sev_critical"]),
            ("Высокий уровень",   f"{int(s.get('high', 0)):,}",        COLORS["sev_high"]),
            ("Устранено",         f"{int(s.get('fixed', 0)):,}",       COLORS["accent_green"]),
            ("С эксплойтом",      f"{int(s.get('with_exploit', 0)):,}",COLORS["accent_orange"]),
            ("Вендоров",          f"{int(s.get('unique_vendors', 0)):,}",COLORS["accent_purple"]),
            ("Ср. CVSS",          f"{s.get('avg_cvss') or 0:.1f}",     COLORS["accent_cyan"]),
        ]
        for label, value, color in cards:
            card = StatCard(label, value, color)
            self.cards_layout.addWidget(card)

    def _load_charts(self):
        try:

            row1 = QHBoxLayout()
            row1.setSpacing(12)

            sev_df = analytics.severity_distribution()
            if not sev_df.empty:
                chart1 = pie_chart(sev_df, "severity", "count",
                                   title="Распределение по уровню опасности",
                                   figsize=(6, 4))
                chart1.setMinimumHeight(280)
                row1.addWidget(chart1, 3)

            year_df = analytics.vulns_by_year()
            if not year_df.empty:
                chart2 = line_chart(year_df, "year", ["count"],
                                    title="Уязвимости по годам публикации",
                                    figsize=(8, 4))
                chart2.setMinimumHeight(280)
                row1.addWidget(chart2, 5)

            w1 = QWidget()
            w1.setLayout(row1)
            w1.setMinimumHeight(290)
            self.charts_layout.addWidget(w1)


            vendors_df = analytics.top_vendors(15)
            if not vendors_df.empty:
                chart3 = bar_chart(vendors_df, "vendor", "count",
                                   title="Топ 15 вендоров по количеству уязвимостей",
                                   horizontal=True, figsize=(10, 6))
                chart3.setMinimumHeight(380)
                self.charts_layout.addWidget(chart3)


            exp_df = analytics.exploit_trend_by_year()
            if not exp_df.empty:
                chart4 = line_chart(exp_df, "year", ["with_exploit", "total"],
                                    title="Уязвимости с известным эксплойтом по годам",
                                    figsize=(10, 4))
                chart4.setMinimumHeight(260)
                self.charts_layout.addWidget(chart4)

        except Exception as e:
            err = QLabel(f"Ошибка загрузки графиков: {e}")
            err.setStyleSheet(f"color: {COLORS['accent_red']};")
            self.charts_layout.addWidget(err)

    def _export_full(self):
        try:
            sheets = {
                "Сводка":     pd.DataFrame([analytics.summary_stats()]),
                "Вендоры":    analytics.top_vendors(50),
                "ПО":         analytics.top_software(50),
                "По годам":   analytics.vulns_by_year(),
                "Критичность":analytics.severity_distribution(),
                "Статусы":    analytics.status_distribution(),
                "CWE":        analytics.top_cwe(30),
                "Эксплойты":  analytics.exploit_distribution(),
            }
            path = exp.export_excel(sheets, "fstec_full_report")
            self.status_message.emit(f"Отчёт сохранён: {path}")
        except Exception as e:
            self.status_message.emit(f"Ошибка экспорта: {e}")

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
