

COLORS = {
    "bg_dark":       "#0D1117",
    "bg_panel":      "#161B22",
    "bg_card":       "#1C2333",
    "bg_input":      "#21262D",
    "border":        "#30363D",
    "border_active": "#388BFD",

    "text_primary":  "#E6EDF3",
    "text_secondary":"#8B949E",
    "text_muted":    "#484F58",

    "accent_blue":   "#388BFD",
    "accent_green":  "#3FB950",
    "accent_orange": "#D29922",
    "accent_red":    "#F85149",
    "accent_purple": "#BC8CFF",
    "accent_cyan":   "#39C5CF",


    "sev_critical":  "#F85149",
    "sev_high":      "#D29922",
    "sev_medium":    "#388BFD",
    "sev_low":       "#3FB950",
    "sev_unknown":   "#8B949E",
}

SEVERITY_COLORS = {
    "Критический": COLORS["sev_critical"],
    "Высокий":     COLORS["sev_high"],
    "Средний":     COLORS["sev_medium"],
    "Низкий":      COLORS["sev_low"],
    "Неизвестно":  COLORS["sev_unknown"],
}


QSS = f"""
/* ── Global ── */
QMainWindow, QDialog, QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
    font-family: "JetBrains Mono", "Consolas", "Courier New", monospace;
    font-size: 13px;
}}

/* ── Sidebar ── */

    background-color: {COLORS['bg_panel']};
    border-right: 1px solid {COLORS['border']};
    min-width: 220px;
    max-width: 220px;
}}


    font-size: 11px;
    font-weight: bold;
    color: {COLORS['accent_blue']};
    padding: 20px 16px 8px 16px;
    letter-spacing: 2px;
}}


    font-size: 10px;
    color: {COLORS['text_muted']};
    padding: 0 16px 16px 16px;
}}

QPushButton
    background: transparent;
    border: none;
    text-align: left;
    padding: 10px 16px;
    color: {COLORS['text_secondary']};
    font-size: 13px;
    border-radius: 6px;
    margin: 1px 8px;
}}
QPushButton
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
}}
QPushButton
    background-color: {COLORS['accent_blue']}22;
    color: {COLORS['accent_blue']};
    border-left: 3px solid {COLORS['accent_blue']};
    font-weight: bold;
}}

/* ── Content area ── */

    background-color: {COLORS['bg_dark']};
}}


    font-size: 22px;
    font-weight: bold;
    color: {COLORS['text_primary']};
    padding: 0;
    margin: 0;
}}


    font-size: 12px;
    color: {COLORS['text_muted']};
}}

/* ── Cards ── */
QFrame
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 16px;
}}

QLabel
    font-size: 32px;
    font-weight: bold;
    color: {COLORS['text_primary']};
}}

QLabel
    font-size: 11px;
    color: {COLORS['text_secondary']};
    letter-spacing: 1px;
}}

/* ── Buttons ── */
QPushButton
    background-color: {COLORS['accent_blue']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}}
QPushButton
    background-color:
}}
QPushButton
    background-color:
}}

QPushButton
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
}}
QPushButton
    border-color: {COLORS['accent_blue']};
    color: {COLORS['accent_blue']};
}}

QPushButton
    background-color: {COLORS['accent_red']}22;
    color: {COLORS['accent_red']};
    border: 1px solid {COLORS['accent_red']}44;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
}}
QPushButton
    background-color: {COLORS['accent_red']}44;
}}

QPushButton
    background-color: {COLORS['accent_green']}22;
    color: {COLORS['accent_green']};
    border: 1px solid {COLORS['accent_green']}44;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
}}
QPushButton
    background-color: {COLORS['accent_green']}44;
}}

/* ── Tables ── */
QTableWidget, QTableView {{
    background-color: {COLORS['bg_panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: {COLORS['border']};
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_blue']}33;
    selection-color: {COLORS['text_primary']};
    font-size: 12px;
}}
QTableWidget::item, QTableView::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {COLORS['border']};
}}
QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {COLORS['accent_blue']}33;
}}
QHeaderView::section {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_secondary']};
    border: none;
    border-bottom: 1px solid {COLORS['border']};
    border-right: 1px solid {COLORS['border']};
    padding: 8px 10px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
}}

/* ── Text inputs ── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['accent_blue']};
}}

QComboBox {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
}}
QComboBox:focus {{
    border-color: {COLORS['accent_blue']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['accent_blue']}44;
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {COLORS['bg_panel']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_muted']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {COLORS['bg_panel']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {COLORS['border']};
    border-radius: 4px;
    min-width: 30px;
}}

/* ── Tabs ── */
QTabWidget::pane {{
    background-color: {COLORS['bg_panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    padding: 10px 18px;
    font-size: 12px;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{
    color: {COLORS['accent_blue']};
    border-bottom: 2px solid {COLORS['accent_blue']};
}}
QTabBar::tab:hover {{
    color: {COLORS['text_primary']};
}}

/* ── Progress bar ── */
QProgressBar {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    text-align: center;
    color: {COLORS['text_primary']};
    font-size: 12px;
}}
QProgressBar::chunk {{
    background-color: {COLORS['accent_blue']};
    border-radius: 5px;
}}

/* ── Labels ── */
QLabel
    font-size: 14px;
    font-weight: bold;
    color: {COLORS['text_primary']};
    padding: 8px 0;
}}

QLabel
    background-color: {COLORS['sev_critical']}22;
    color: {COLORS['sev_critical']};
    border: 1px solid {COLORS['sev_critical']}44;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}}
QLabel
    background-color: {COLORS['sev_high']}22;
    color: {COLORS['sev_high']};
    border: 1px solid {COLORS['sev_high']}44;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}}
QLabel
    background-color: {COLORS['sev_medium']}22;
    color: {COLORS['sev_medium']};
    border: 1px solid {COLORS['sev_medium']}44;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}}
QLabel
    background-color: {COLORS['sev_low']}22;
    color: {COLORS['sev_low']};
    border: 1px solid {COLORS['sev_low']}44;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}}

/* ── Splitter ── */
QSplitter::handle {{
    background: {COLORS['border']};
}}

/* ── Status bar ── */
QStatusBar {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border']};
    font-size: 11px;
    padding: 2px 8px;
}}

/* ── Group boxes ── */
QGroupBox {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px;
    font-size: 12px;
    color: {COLORS['text_secondary']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {COLORS['text_secondary']};
    font-size: 11px;
    letter-spacing: 1px;
}}

/* ── Tooltips ── */
QToolTip {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}
"""
