import pandas as pd
from core.database import execute_query


def top_vendors(limit: int = 20) -> pd.DataFrame:
    return execute_query(f"""
        SELECT vendor, COUNT(*) as count
        FROM vulnerabilities
        WHERE vendor IS NOT NULL AND vendor != '' AND vendor != 'nan'
        GROUP BY vendor
        ORDER BY count DESC
        LIMIT {limit}
    """)


def top_software(limit: int = 20) -> pd.DataFrame:
    return execute_query(f"""
        SELECT vendor, software, COUNT(*) as count
        FROM vulnerabilities
        WHERE software IS NOT NULL AND software != '' AND software != 'nan'
        GROUP BY vendor, software
        ORDER BY count DESC
        LIMIT {limit}
    """)


def vendor_severity_breakdown(vendor: str) -> pd.DataFrame:
    safe = vendor.replace("'", "''")
    return execute_query(f"""
        SELECT severity, COUNT(*) as count
        FROM vulnerabilities
        WHERE vendor = '{safe}'
        GROUP BY severity
        ORDER BY count DESC
    """)


def vendor_fix_rate(limit: int = 20) -> pd.DataFrame:
    return execute_query(f"""
        SELECT vendor,
               COUNT(*) as total,
               SUM(CASE WHEN fix_info LIKE '%устранена%' THEN 1 ELSE 0 END) as fixed,
               ROUND(100.0 * SUM(CASE WHEN fix_info LIKE '%устранена%' THEN 1 ELSE 0 END) / COUNT(*), 1) as fix_rate
        FROM vulnerabilities
        WHERE vendor IS NOT NULL AND vendor != '' AND vendor != 'nan'
        GROUP BY vendor
        HAVING total >= 50
        ORDER BY total DESC
        LIMIT {limit}
    """)


def vulns_by_year() -> pd.DataFrame:
    return execute_query("""
        SELECT year_published as year, COUNT(*) as count
        FROM vulnerabilities
        WHERE year_published IS NOT NULL AND year_published > 2000 AND year_published <= 2025
        GROUP BY year_published
        ORDER BY year_published
    """)


def vulns_by_year_severity() -> pd.DataFrame:
    return execute_query("""
        SELECT year_published as year, severity, COUNT(*) as count
        FROM vulnerabilities
        WHERE year_published IS NOT NULL AND year_published > 2000 AND year_published <= 2025
              AND severity != 'Неизвестно'
        GROUP BY year_published, severity
        ORDER BY year_published
    """)


def detection_to_publish_lag() -> pd.DataFrame:
    return execute_query("""
        SELECT year_detected as year,
               COUNT(*) as count,
               AVG(year_published - year_detected) as avg_lag_years
        FROM vulnerabilities
        WHERE year_detected IS NOT NULL AND year_published IS NOT NULL
              AND year_detected > 2000 AND year_detected <= 2025
        GROUP BY year_detected
        ORDER BY year_detected
    """)


def severity_distribution() -> pd.DataFrame:
    return execute_query("""
        SELECT severity, COUNT(*) as count
        FROM vulnerabilities
        GROUP BY severity
        ORDER BY count DESC
    """)


def cvss_distribution() -> pd.DataFrame:
    return execute_query("""
        SELECT ROUND(cvss_score, 0) as score_bucket,
               COUNT(*) as count
        FROM vulnerabilities
        WHERE cvss_score IS NOT NULL
        GROUP BY score_bucket
        ORDER BY score_bucket
    """)


def critical_vendors(limit: int = 15) -> pd.DataFrame:
    return execute_query(f"""
        SELECT vendor,
               COUNT(*) as total,
               SUM(CASE WHEN severity='Критический' THEN 1 ELSE 0 END) as critical_count,
               ROUND(100.0 * SUM(CASE WHEN severity='Критический' THEN 1 ELSE 0 END) / COUNT(*), 1) as critical_pct
        FROM vulnerabilities
        WHERE vendor IS NOT NULL AND vendor != '' AND vendor != 'nan'
        GROUP BY vendor
        HAVING total >= 100
        ORDER BY critical_count DESC
        LIMIT {limit}
    """)


def status_distribution() -> pd.DataFrame:
    return execute_query("""
        SELECT status, COUNT(*) as count
        FROM vulnerabilities
        GROUP BY status
        ORDER BY count DESC
    """)


def fix_info_distribution() -> pd.DataFrame:
    return execute_query("""
        SELECT fix_info, COUNT(*) as count
        FROM vulnerabilities
        GROUP BY fix_info
        ORDER BY count DESC
    """)


def exploit_distribution() -> pd.DataFrame:
    return execute_query("""
        SELECT exploit, COUNT(*) as count
        FROM vulnerabilities
        GROUP BY exploit
        ORDER BY count DESC
    """)


def unpatched_critical() -> pd.DataFrame:
    return execute_query("""
        SELECT vendor, software, id, name, cvss_score, year_published
        FROM vulnerabilities
        WHERE severity = 'Критический'
          AND (fix_info LIKE '%отсутствует%' OR fix_info IS NULL)
          AND exploit NOT LIKE '%уточн%'
        ORDER BY cvss_score DESC
        LIMIT 50
    """)


def top_cwe(limit: int = 20) -> pd.DataFrame:
    return execute_query(f"""
        SELECT cwe_type, cwe_description, COUNT(*) as count
        FROM vulnerabilities
        WHERE cwe_type IS NOT NULL AND cwe_type != '' AND cwe_type != 'nan'
        GROUP BY cwe_type
        ORDER BY count DESC
        LIMIT {limit}
    """)


def cwe_by_severity() -> pd.DataFrame:
    return execute_query("""
        SELECT cwe_type, severity, COUNT(*) as count
        FROM vulnerabilities
        WHERE cwe_type IS NOT NULL AND cwe_type != '' AND cwe_type != 'nan'
              AND severity != 'Неизвестно'
        GROUP BY cwe_type, severity
        ORDER BY count DESC
        LIMIT 100
    """)


def exploit_trend_by_year() -> pd.DataFrame:
    return execute_query("""
        SELECT year_published as year,
               SUM(CASE WHEN exploit LIKE '%открытом%' OR exploit = 'Существует' THEN 1 ELSE 0 END) as with_exploit,
               COUNT(*) as total
        FROM vulnerabilities
        WHERE year_published IS NOT NULL AND year_published > 2000 AND year_published <= 2025
        GROUP BY year_published
        ORDER BY year_published
    """)


def software_type_distribution() -> pd.DataFrame:
    return execute_query("""
        SELECT software_type, COUNT(*) as count
        FROM vulnerabilities
        WHERE software_type IS NOT NULL AND software_type != '' AND software_type != 'nan'
        GROUP BY software_type
        ORDER BY count DESC
        LIMIT 15
    """)


def summary_stats() -> dict:
    df = execute_query("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN severity='Критический' THEN 1 ELSE 0 END) as critical,
            SUM(CASE WHEN severity='Высокий' THEN 1 ELSE 0 END) as high,
            SUM(CASE WHEN severity='Средний' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN severity='Низкий' THEN 1 ELSE 0 END) as low,
            SUM(CASE WHEN fix_info LIKE '%устранена%' THEN 1 ELSE 0 END) as fixed,
            SUM(CASE WHEN exploit NOT LIKE '%уточн%' AND exploit IS NOT NULL THEN 1 ELSE 0 END) as with_exploit,
            COUNT(DISTINCT vendor) as unique_vendors,
            COUNT(DISTINCT software) as unique_software,
            AVG(cvss_score) as avg_cvss
        FROM vulnerabilities
    """)
    return df.iloc[0].to_dict()
