
import pandas as pd
import json
from pathlib import Path
from datetime import datetime


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_csv(df: pd.DataFrame, name: str, output_dir: str = "exports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = f"{output_dir}/{name}_{_timestamp()}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def export_excel(dataframes: dict[str, pd.DataFrame], name: str, output_dir: str = "exports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = f"{output_dir}/{name}_{_timestamp()}.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return path


def export_json(data: dict | list, name: str, output_dir: str = "exports") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = f"{output_dir}/{name}_{_timestamp()}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    return path


def export_full_report(analytics_fn_map: dict, output_dir: str = "exports") -> str:
    sheets = {}
    for sheet_name, fn in analytics_fn_map.items():
        try:
            df = fn()
            if isinstance(df, pd.DataFrame) and not df.empty:
                sheets[sheet_name] = df
        except Exception:
            pass
    return export_excel(sheets, "full_report", output_dir)
