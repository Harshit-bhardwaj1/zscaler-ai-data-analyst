from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session


def make_json_safe(value):
    """
    Convert PostgreSQL/Python values into JSON-safe values.
    """

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def execute_query(
    db: Session,
    sql: str,
    max_rows: int = 100,
) -> dict:
    """
    Execute a validated SELECT query and return rows + metadata.
    """

    try:
        result = db.execute(text(sql))

        columns = list(result.keys())

        rows = []

        for row in result.fetchmany(max_rows):
            row_dict = {}

            for column, value in zip(columns, row):
                row_dict[column] = make_json_safe(value)

            rows.append(row_dict)

        return {
            "success": True,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": str(e),
        }