
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QSplitter, QPlainTextEdit,
    QLineEdit, QComboBox, QFrame, QMessageBox, QFileDialog,
    QCompleter
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QStringListModel
from PyQt6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat

import pandas as pd
import re

from core import database as db, export as exp
from ui.widgets import DataTable, ExportBar
from ui.theme import COLORS


class SQLHighlighter(QSyntaxHighlighter):
    KEYWORDS = [
        "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "LIKE",
        "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET", "JOIN",
        "LEFT", "RIGHT", "INNER", "ON", "AS", "DISTINCT", "COUNT",
        "SUM", "AVG", "MIN", "MAX", "ROUND", "CASE", "WHEN", "THEN",
        "ELSE", "END", "NULL", "IS", "DESC", "ASC", "WITH", "UNION",
        "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "TABLE",
    ]

    def __init__(self, document):
        super().__init__(document)
        self._rules = []

        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor(COLORS["accent_blue"]))
        kw_fmt.setFontWeight(700)
        pattern = r'\b(' + '|'.join(self.KEYWORDS) + r')\b'
        self._rules.append((re.compile(pattern, re.IGNORECASE), kw_fmt))

        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor(COLORS["accent_green"]))
        self._rules.append((re.compile(r"'[^']*'"), str_fmt))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor(COLORS["text_muted"]))
        self._rules.append((re.compile(r'--[^\n]*'), comment_fmt))

        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor(COLORS["accent_orange"]))
        self._rules.append((re.compile(r'\b\d+(\.\d+)?\b'), num_fmt))

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


class QueryWorker(QThread):
    finished = pyqtSignal(object, str)

    def __init__(self, sql: str):
        super().__init__()
        self.sql = sql

    def run(self):
        try:
            df = db.execute_query(self.sql)
            self.finished.emit(df, "")
        except Exception as e:
            self.finished.emit(None, str(e))


class BrowserPage(QWidget):
    status_message = pyqtSignal(str)

    PRESET_QUERIES = {
        "Все поля (100 строк)":
            "SELECT * FROM vulnerabilities LIMIT 100",
        "Критические без патча":
            ("SELECT id, vendor, software, name, cvss_score, year_published\n"
             "FROM vulnerabilities\n"
             "WHERE severity = 'Критический'\n"
             "  AND fix_info LIKE '%отсутствует%'\n"
             "ORDER BY cvss_score DESC\nLIMIT 50"),
        "Топ вендоров":
            ("SELECT vendor, COUNT(*) AS total\n"
             "FROM vulnerabilities\n"
             "WHERE vendor IS NOT NULL AND vendor != 'nan'\n"
             "GROUP BY vendor\nORDER BY total DESC\nLIMIT 20"),
        "По годам и критичности":
            ("SELECT year_published, severity, COUNT(*) AS count\n"
             "FROM vulnerabilities\n"
             "WHERE year_published IS NOT NULL\n"
             "GROUP BY year_published, severity\n"
             "ORDER BY year_published"),
        "Уязвимости с эксплойтом":
            ("SELECT id, vendor, software, severity, cvss_score, exploit\n"
             "FROM vulnerabilities\n"
             "WHERE exploit NOT LIKE '%уточн%'\n"
             "  AND exploit IS NOT NULL\n"
             "ORDER BY cvss_score DESC\nLIMIT 100"),
        "CWE статистика":
            ("SELECT cwe_type, cwe_description, COUNT(*) AS count\n"
             "FROM vulnerabilities\n"
             "WHERE cwe_type IS NOT NULL AND cwe_type != 'nan'\n"
             "GROUP BY cwe_type\nORDER BY count DESC\nLIMIT 30"),
        "Microsoft критические":
            ("SELECT id, software, severity, cvss_score,\n"
             "       fix_info, year_published\n"
             "FROM vulnerabilities\n"
             "WHERE vendor LIKE '%Microsoft%'\n"
             "  AND severity = 'Критический'\n"
             "ORDER BY cvss_score DESC\nLIMIT 50"),
        "Колонки таблицы":
            "PRAGMA table_info(vulnerabilities)",
        "Количество записей":
            "SELECT COUNT(*) AS total FROM vulnerabilities",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_df: pd.DataFrame | None = None
        self._worker: QueryWorker | None = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)


        hdr = QHBoxLayout()
        title = QLabel("База данных / SQL")
        title.setObjectName("page-title")
        hdr.addWidget(title)
        hdr.addStretch()
        root.addLayout(hdr)

        tabs = QTabWidget()
        root.addWidget(tabs, 1)

        tabs.addTab(self._build_sql_tab(), "SQL-консоль")
        tabs.addTab(self._build_browse_tab(), "Обзор таблицы")
        tabs.addTab(self._build_schema_tab(), "Схема")


    def _build_sql_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)


        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Готовые запросы:"))
        self._preset_combo = QComboBox()
        self._preset_combo.addItem("— выберите запрос —")
        for name in self.PRESET_QUERIES:
            self._preset_combo.addItem(name)
        self._preset_combo.currentTextChanged.connect(self._load_preset)
        preset_row.addWidget(self._preset_combo, 1)
        layout.addLayout(preset_row)


        self._sql_editor = QPlainTextEdit()
        self._sql_editor.setPlaceholderText(
            "Введите SQL-запрос...\n\nПример:\n"
            "SELECT vendor, COUNT(*) as n\n"
            "FROM vulnerabilities\n"
            "WHERE severity = 'Критический'\n"
            "GROUP BY vendor ORDER BY n DESC LIMIT 20"
        )
        self._sql_editor.setFont(QFont("JetBrains Mono, Consolas, Courier New", 13))
        self._sql_editor.setMinimumHeight(140)
        self._sql_editor.setMaximumHeight(220)
        self._highlighter = SQLHighlighter(self._sql_editor.document())
        layout.addWidget(self._sql_editor)


        btn_row = QHBoxLayout()
        self._run_btn = QPushButton("▶  Выполнить  (Ctrl+Enter)")
        self._run_btn.setObjectName("btn-primary")
        self._run_btn.clicked.connect(self._run_query)
        btn_row.addWidget(self._run_btn)

        clear_btn = QPushButton("✕ Очистить")
        clear_btn.setObjectName("btn-secondary")
        clear_btn.clicked.connect(self._sql_editor.clear)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()

        self._row_count_lbl = QLabel("")
        self._row_count_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        btn_row.addWidget(self._row_count_lbl)

        export_bar = ExportBar(
            on_csv=lambda: self._export_result("csv"),
            on_excel=lambda: self._export_result("excel"),
            on_json=lambda: self._export_result("json"),
        )
        btn_row.addWidget(export_bar)
        layout.addLayout(btn_row)


        from PyQt6.QtGui import QKeySequence, QShortcut
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self._sql_editor)
        shortcut.activated.connect(self._run_query)


        self._result_table = DataTable()
        layout.addWidget(self._result_table, 1)


        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet(
            f"color: {COLORS['accent_red']}; font-size: 12px; padding: 4px;"
        )
        self._error_lbl.setWordWrap(True)
        layout.addWidget(self._error_lbl)

        return w

    def _load_preset(self, name: str):
        if name in self.PRESET_QUERIES:
            self._sql_editor.setPlainText(self.PRESET_QUERIES[name])

    def _run_query(self):
        sql = self._sql_editor.toPlainText().strip()
        if not sql:
            return


        destructive = re.compile(r'^\s*(DROP|DELETE|TRUNCATE|ALTER|INSERT|UPDATE)',
                                 re.IGNORECASE | re.MULTILINE)
        if destructive.search(sql):
            self._error_lbl.setText(
                "!  Запросы на изменение/удаление данных запрещены в этом режиме."
            )
            return

        self._error_lbl.setText("")
        self._run_btn.setEnabled(False)
        self._run_btn.setText("⏳ Выполняется...")
        self.status_message.emit("Выполняется запрос...")

        self._worker = QueryWorker(sql)
        self._worker.finished.connect(self._on_query_done)
        self._worker.start()

    @pyqtSlot(object, str)
    def _on_query_done(self, df, error: str):
        self._run_btn.setEnabled(True)
        self._run_btn.setText("▶  Выполнить  (Ctrl+Enter)")

        if error:
            self._error_lbl.setText(f"❌ Ошибка: {error}")
            self.status_message.emit(f"Ошибка запроса: {error}")
            return

        self._current_df = df
        self._result_table.load_dataframe(df)
        rows = len(df)
        self._row_count_lbl.setText(f"{rows:,} строк · {len(df.columns)} столбцов")
        self.status_message.emit(f"✓ Запрос выполнен: {rows:,} строк")

    def _export_result(self, fmt: str):
        if self._current_df is None or self._current_df.empty:
            self.status_message.emit("Нет результатов для экспорта")
            return
        try:
            if fmt == "csv":
                path = exp.export_csv(self._current_df, "query_result")
            elif fmt == "excel":
                path = exp.export_excel({"Результат": self._current_df}, "query_result")
            else:
                path = exp.export_json(
                    self._current_df.to_dict(orient="records"), "query_result"
                )
            self.status_message.emit(f"✓ Сохранено: {path}")
        except Exception as e:
            self.status_message.emit(f"Ошибка экспорта: {e}")


    def _build_browse_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        ctrl = QHBoxLayout()


        ctrl.addWidget(QLabel("Поиск:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Введите текст для поиска по всей таблице...")
        self._search_edit.setMinimumWidth(280)
        ctrl.addWidget(self._search_edit, 2)


        ctrl.addWidget(QLabel("Столбец:"))
        self._col_combo = QComboBox()
        self._col_combo.setMinimumWidth(180)
        ctrl.addWidget(self._col_combo)


        ctrl.addWidget(QLabel("Критичность:"))
        self._sev_combo = QComboBox()
        self._sev_combo.addItems(["Все", "Критический", "Высокий", "Средний", "Низкий"])
        ctrl.addWidget(self._sev_combo)

        search_btn = QPushButton("Найти")
        search_btn.setObjectName("btn-primary")
        search_btn.clicked.connect(self._do_search)
        ctrl.addWidget(search_btn)
        ctrl.addStretch()

        self._browse_count = QLabel("")
        self._browse_count.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        ctrl.addWidget(self._browse_count)

        layout.addLayout(ctrl)

        export_bar = ExportBar(
            on_csv=lambda: self._export_browse("csv"),
            on_excel=lambda: self._export_browse("excel"),
        )
        layout.addWidget(export_bar)

        self._browse_table = DataTable()
        layout.addWidget(self._browse_table, 1)

        self._browse_df: pd.DataFrame | None = None
        return w

    def _do_search(self):
        term = self._search_edit.text().strip()
        col = self._col_combo.currentText()
        sev = self._sev_combo.currentText()

        where_clauses = []
        params_sql = []

        if term:
            col_name = col if col and col != "Все столбцы" else None
            if col_name:
                where_clauses.append(f"{col_name} LIKE '%{term.replace(chr(39), chr(39)*2)}%'")
            else:
                like_cols = ["id", "vendor", "software", "name", "cve_ids",
                             "cwe_type", "description"]
                parts = [f"{c} LIKE '%{term.replace(chr(39), chr(39)*2)}%'"
                         for c in like_cols]
                where_clauses.append("(" + " OR ".join(parts) + ")")

        if sev != "Все":
            where_clauses.append(f"severity = '{sev}'")

        where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        sql = (
            "SELECT id, vendor, software, version, severity, cvss_score,\n"
            "       status, fix_info, exploit, year_published, cwe_type\n"
            f"FROM vulnerabilities\n{where}\n"
            "ORDER BY cvss_score DESC\nLIMIT 500"
        )
        try:
            self._browse_df = db.execute_query(sql)
            self._browse_table.load_dataframe(self._browse_df)
            self._browse_count.setText(f"{len(self._browse_df):,} строк")
            self.status_message.emit(f"Найдено: {len(self._browse_df):,} строк")
        except Exception as e:
            self.status_message.emit(f"Ошибка: {e}")

    def _export_browse(self, fmt: str):
        if self._browse_df is None or self._browse_df.empty:
            self.status_message.emit("Нет данных для экспорта")
            return
        try:
            if fmt == "csv":
                path = exp.export_csv(self._browse_df, "browse_result")
            else:
                path = exp.export_excel({"Результат": self._browse_df}, "browse_result")
            self.status_message.emit(f"✓ Сохранено: {path}")
        except Exception as e:
            self.status_message.emit(f"Ошибка экспорта: {e}")


    def _build_schema_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        lbl = QLabel("Структура таблицы vulnerabilities")
        lbl.setObjectName("section-header")
        layout.addWidget(lbl)

        self._schema_table = DataTable()
        layout.addWidget(self._schema_table, 1)
        return w


    def init_browse(self):
        try:
            cols = db.get_table_columns()
            self._col_combo.clear()
            self._col_combo.addItem("Все столбцы")
            self._col_combo.addItems(cols)

            schema_df = db.execute_query("PRAGMA table_info(vulnerabilities)")
            self._schema_table.load_dataframe(schema_df)

            self._do_search()
        except Exception as e:
            self.status_message.emit(f"Ошибка инициализации браузера: {e}")

    def refresh(self):
        self.init_browse()
