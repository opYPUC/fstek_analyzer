
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QStatusBar,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from ui.theme import COLORS, QSS
from ui.pages.loader import LoaderPage
from ui.pages.dashboard import DashboardPage
from ui.pages.vendors import VendorsPage
from ui.pages.timeline import TimelinePage
from ui.pages.severity import SeverityPage
from ui.pages.status import StatusPage
from ui.pages.browser import BrowserPage
from core import database as db

NAV_ITEMS = [
    ("Главная",      "dashboard"),
    ("Вендоры / ПО", "vendors"),
    ("Время",        "timeline"),
    ("Критичность",  "severity"),
    ("Статусы",      "status"),
    ("БД / SQL",     "browser"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("БДУ ФСТЭК Анализатор")
        self.setMinimumSize(1280, 780)
        self.resize(1440, 900)
        self.setStyleSheet(QSS)
        self._pages: dict[str, QWidget] = {}
        self._nav_buttons: dict[str, QPushButton] = {}
        self._visited: set[str] = set()
        self._build_layout()
        self._add_status_bar()
        if db.is_db_loaded():
            self._show_app()
        else:
            self._show_loader()

    def _build_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._sidebar = QWidget()
        self._sidebar.setObjectName("sidebar")
        self._sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sidebar_layout = QVBoxLayout(self._sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        logo_frame = QWidget()
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(16, 20, 16, 12)
        logo_layout.setSpacing(2)
        logo_lbl = QLabel("ФСТЭК БДУ")
        logo_lbl.setObjectName("sidebar-logo")
        logo_layout.addWidget(logo_lbl)
        ver_lbl = QLabel("v1.0  •  Анализатор")
        ver_lbl.setObjectName("sidebar-version")
        logo_layout.addWidget(ver_lbl)
        sidebar_layout.addWidget(logo_frame)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"background: {COLORS['border']}; max-height: 1px;")
        sidebar_layout.addWidget(div)
        sidebar_layout.addSpacing(8)

        nav_label = QLabel("АНАЛИЗ")
        nav_label.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 10px; letter-spacing: 2px; padding: 4px 24px;"
        )
        sidebar_layout.addWidget(nav_label)

        self._nav_area = QVBoxLayout()
        self._nav_area.setSpacing(2)
        sidebar_layout.addLayout(self._nav_area)
        sidebar_layout.addStretch()

        footer = QLabel("Банк данных\nугроз безопасности")
        footer.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 10px; padding: 12px 16px; line-height: 1.4;"
        )
        sidebar_layout.addWidget(footer)
        main_layout.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        main_layout.addWidget(self._stack, 1)

    def _add_status_bar(self):
        self._status_bar = QStatusBar()
        self._status_bar.setSizeGripEnabled(False)
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Готово")

    def _show_loader(self, show_back: bool = False):
        self._sidebar.setVisible(False)
        loader = LoaderPage(self, show_back=show_back)
        loader.load_complete.connect(self._on_load_complete)
        if show_back:
            loader.go_back.connect(self._on_loader_back)
        self._stack.addWidget(loader)
        self._stack.setCurrentWidget(loader)

    def _on_load_complete(self, count: int):
        self._status_bar.showMessage(f"✓ Загружено {count:,} уязвимостей")
        self._visited.clear()
        self._show_app()

    def _on_loader_back(self):
        loader = self._stack.currentWidget()
        self._stack.removeWidget(loader)
        loader.deleteLater()
        self._sidebar.setVisible(True)
        current_key = next(
            (k for k, btn in self._nav_buttons.items() if btn.isChecked()),
            "dashboard"
        )
        page = self._pages.get(current_key)
        if page:
            self._stack.setCurrentWidget(page)

    def _show_app(self):
        self._sidebar.setVisible(True)
        while self._stack.count() > 0:
            w = self._stack.widget(0)
            self._stack.removeWidget(w)
            w.deleteLater()
        while self._nav_area.count():
            item = self._nav_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._nav_buttons.clear()
        self._pages.clear()

        page_classes = {
            "dashboard": DashboardPage,
            "vendors":   VendorsPage,
            "timeline":  TimelinePage,
            "severity":  SeverityPage,
            "status":    StatusPage,
            "browser":   BrowserPage,
        }

        for label, key in NAV_ITEMS:
            page = page_classes[key](self)
            if hasattr(page, "status_message"):
                page.status_message.connect(self._status_bar.showMessage)
            self._pages[key] = page
            self._stack.addWidget(page)

            btn = QPushButton(f"  {label}")
            btn.setObjectName("nav-btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            self._nav_area.addWidget(btn)
            self._nav_buttons[key] = btn

        self._nav_area.addSpacing(12)
        load_btn = QPushButton("  Загрузить файл")
        load_btn.setObjectName("nav-btn")
        load_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        load_btn.clicked.connect(self._reload_file)
        self._nav_area.addWidget(load_btn)

        self._navigate("dashboard")

    def _navigate(self, key: str):
        for k, btn in self._nav_buttons.items():
            btn.setChecked(k == key)
        page = self._pages.get(key)
        if not page:
            return
        self._stack.setCurrentWidget(page)

        if key not in self._visited:
            self._visited.add(key)
            if key == "browser":
                page.init_browse()
            elif hasattr(page, "refresh"):
                page.refresh()

    def _reload_file(self):
        self._show_loader(show_back=True)
