
import sqlite3
import pandas as pd
from pathlib import Path
import re


DB_PATH = Path(__file__).parent.parent / "data" / "fstec.db"
COLUMN_MAP = {
    "Идентификатор": "id",
    "Наименование уязвимости": "name",
    "Описание уязвимости": "description",
    "Вендор ПО": "vendor",
    "Название ПО": "software",
    "Версия ПО": "version",
    "Тип ПО": "software_type",
    "Наименование ОС и тип аппаратной платформы": "os_platform",
    "Класс уязвимости": "vuln_class",
    "Дата выявления": "date_detected",
    "CVSS 2.0": "cvss2",
    "CVSS 3.0": "cvss3",
    "CVSS 4.0": "cvss4",
    "Уровень опасности уязвимости": "severity_raw",
    "Возможные меры по устранению": "mitigation",
    "Статус уязвимости": "status",
    "Наличие эксплойта": "exploit",
    "Информация об устранении": "fix_info",
    "Ссылки на источники": "references",
    "Идентификаторы других систем описаний уязвимости": "cve_ids",
    "Способ эксплуатации": "exploit_method",
    "Способ устранения": "fix_method",
    "Дата публикации": "date_published",
    "Дата последнего обновления": "date_updated",
    "Последствия эксплуатации уязвимости": "impact",
    "Состояние уязвимости": "state",
    "Описание ошибки CWE": "cwe_description",
    "Тип ошибки CWE": "cwe_type",
}

SEVERITY_KEYWORDS = {
    "Критический": "Критический",
    "Высокий": "Высокий",
    "Средний": "Средний",
    "Низкий": "Низкий",
}


def _extract_severity(text: str) -> str:
    if not isinstance(text, str):
        return "Неизвестно"
    for key in SEVERITY_KEYWORDS:
        if key in text:
            return key
    return "Неизвестно"


def _extract_cvss_score(text: str) -> float | None:
    if not isinstance(text, str):
        return None
    m = re.search(r"[\d]+[,.][\d]+", text)
    if m:
        return float(m.group().replace(",", "."))
    return None


def load_xlsx(xlsx_path: str, progress_callback=None) -> int:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if progress_callback:
        progress_callback("Чтение XLSX файла...")

    df = pd.read_excel(xlsx_path, header=2, dtype=str)
    df = df.rename(columns=COLUMN_MAP)


    keep = list(COLUMN_MAP.values())
    existing = [c for c in keep if c in df.columns]
    df = df[existing].copy()


    df = df.dropna(subset=["id"])
    df = df[df["id"].str.startswith("BDU:", na=False)]

    if progress_callback:
        progress_callback(f"Обработка {len(df)} записей...")


    if "severity_raw" in df.columns:
        df["severity"] = df["severity_raw"].apply(_extract_severity)
    else:
        df["severity"] = "Неизвестно"


    def best_cvss(row):
        for col in ["cvss3", "cvss2", "cvss4"]:
            val = _extract_cvss_score(row.get(col, ""))
            if val is not None:
                return val
        return None

    df["cvss_score"] = df.apply(best_cvss, axis=1)


    def extract_year(val):
        if not isinstance(val, str):
            return None
        m = re.search(r"\d{4}", val)
        return int(m.group()) if m else None

    df["year_published"] = df.get("date_published", pd.Series()).apply(extract_year)
    df["year_detected"] = df.get("date_detected", pd.Series()).apply(extract_year)

    if progress_callback:
        progress_callback("Сохранение в базу данных...")

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("vulnerabilities", conn, if_exists="replace", index=False)


    conn.execute("CREATE INDEX IF NOT EXISTS idx_vendor ON vulnerabilities(vendor)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_severity ON vulnerabilities(severity)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON vulnerabilities(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON vulnerabilities(year_published)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cwe ON vulnerabilities(cwe_type)")
    conn.commit()
    conn.close()

    return len(df)


def get_connection() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError("База данных не найдена. Загрузите XLSX файл.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_db_loaded() -> bool:
    if not DB_PATH.exists():
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.execute("SELECT COUNT(*) FROM vulnerabilities")
        count = cur.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def execute_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()


def get_table_columns() -> list[str]:
    conn = get_connection()
    cursor = conn.execute("PRAGMA table_info(vulnerabilities)")
    cols = [row[1] for row in cursor.fetchall()]
    conn.close()
    return cols
