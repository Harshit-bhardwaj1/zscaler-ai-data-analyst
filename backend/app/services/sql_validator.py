import sqlglot
from sqlglot import exp


ALLOWED_TABLES = {
    "customers",
    "subscriptions",
    "usage",
    "support_tickets",
    "revenue_events",
}


def validate_sql(sql: str) -> dict:
    """
    Validate AI-generated SQL before execution.

    Rules:
    - Only SELECT / WITH queries are allowed.
    - No INSERT, UPDATE, DELETE, DROP, ALTER, etc.
    - Only known application tables can be queried.
    - CTE names are allowed and are not treated as real tables.
    - Multiple SQL statements are rejected.
    """

    if not sql or not sql.strip():
        return {
            "valid": False,
            "error": "SQL query is empty.",
        }

    sql = sql.strip()

    # Remove one trailing semicolon
    if sql.endswith(";"):
        sql = sql[:-1].strip()

    # Prevent multiple statements
    if ";" in sql:
        return {
            "valid": False,
            "error": "Multiple SQL statements are not allowed.",
        }

    try:
        statements = sqlglot.parse(sql, read="postgres")
    except Exception as e:
        return {
            "valid": False,
            "error": f"SQL parsing failed: {str(e)}",
        }

    if len(statements) != 1:
        return {
            "valid": False,
            "error": "Only one SQL statement is allowed.",
        }

    statement = statements[0]

    # ---------------------------------------------------------
    # Only SELECT / WITH queries
    # ---------------------------------------------------------

    if not isinstance(statement, exp.Query):
        return {
            "valid": False,
            "error": "Only SELECT queries are allowed.",
        }

    # ---------------------------------------------------------
    # Reject dangerous operations
    # ---------------------------------------------------------

    forbidden = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.TruncateTable,
    )

    for node in statement.walk():
        if isinstance(node, forbidden):
            return {
                "valid": False,
                "error": "Unsafe SQL operation detected.",
            }

    # ---------------------------------------------------------
    # Find CTE names
    # ---------------------------------------------------------
    # Example:
    #
    # WITH latest_usage AS (...)
    #
    # latest_usage is NOT a real database table.
    # It is a temporary CTE.
    # ---------------------------------------------------------

    cte_names = set()

    for cte in statement.find_all(exp.CTE):
        alias = cte.alias

        if alias:
            cte_names.add(alias.lower())

    # ---------------------------------------------------------
    # Find referenced tables
    # ---------------------------------------------------------

    referenced_tables = set()

    for table in statement.find_all(exp.Table):
        table_name = table.name.lower()

        if table_name:
            referenced_tables.add(table_name)

    # Remove CTE names from table references
    real_tables = referenced_tables - cte_names

    # ---------------------------------------------------------
    # Check unknown tables
    # ---------------------------------------------------------

    unknown_tables = real_tables - ALLOWED_TABLES

    if unknown_tables:
        return {
            "valid": False,
            "error": (
                "Query references unknown table(s): "
                + ", ".join(sorted(unknown_tables))
            ),
        }

    # ---------------------------------------------------------
    # Success
    # ---------------------------------------------------------

    return {
        "valid": True,
        "error": None,
        "sql": sql,
        "tables": sorted(real_tables),
        "ctes": sorted(cte_names),
    }