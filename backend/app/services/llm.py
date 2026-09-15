from __future__ import annotations

import json
import re
from typing import Any

from groq import Groq

from app.config import settings


# ============================================================
# CONFIGURATION
# ============================================================
MODEL_NAME = "openai/gpt-oss-120b"


# ============================================================
# GROQ CLIENT
# ============================================================

def get_client() -> Groq:
    """
    Create a Groq client using the backend environment variable.
    Never expose the API key to the frontend.
    """

    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured in the backend environment."
        )

    return Groq(api_key=settings.GROQ_API_KEY)


# ============================================================
# SQL CLEANING
# ============================================================

def clean_sql(text: str) -> str:
    """
    Remove markdown code fences and surrounding text from
    an LLM-generated SQL response.
    """

    if not text:
        return ""

    text = text.strip()

    # Remove markdown fences.
    text = re.sub(r"```sql\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)

    # If the model returned extra explanation before SQL,
    # start from the first SELECT or WITH.
    select_match = re.search(
        r"\b(SELECT|WITH)\b",
        text,
        flags=re.IGNORECASE,
    )

    if select_match:
        text = text[select_match.start():]

    # Remove anything after a closing code fence if present.
    text = text.split("```")[0]

    return text.strip()


# ============================================================
# JSON EXTRACTION
# ============================================================

def parse_json_response(content: str) -> dict[str, Any] | None:
    """
    Safely parse JSON returned by the model.

    Expected structure:

    {
        "sql": "...",
        "assumptions": ["..."]
    }
    """

    if not content:
        return None

    content = content.strip()

    # Direct JSON.
    try:
        parsed = json.loads(content)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from surrounding text.
    match = re.search(
        r"\{.*\}",
        content,
        flags=re.DOTALL,
    )

    if match:
        try:
            parsed = json.loads(match.group(0))

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

    return None


# ============================================================
# CONVERSATION HISTORY
# ============================================================

def build_history(
    conversation_history: list[dict[str, Any]] | None,
) -> str:
    """
    Convert previous conversation messages into a compact
    context block for the SQL-generation model.
    """

    if not conversation_history:
        return "No previous conversation."

    history_lines: list[str] = []

    for item in conversation_history[-6:]:
        if not isinstance(item, dict):
            continue

        role = item.get("role", "")
        content = item.get("content", "")

        if role and content:
            history_lines.append(
                f"{role.upper()}: {content}"
            )

        # Preserve previous structured result when available.
        result = item.get("result")

        if isinstance(result, dict):
            previous_sql = result.get("sql")

            if previous_sql:
                history_lines.append(
                    f"PREVIOUS_SQL: {previous_sql}"
                )

    if not history_lines:
        return "No previous conversation."

    return "\n".join(history_lines)


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(
    question: str,
    schema_context: str,
    conversation_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Ask Groq to convert a natural-language business question
    into safe PostgreSQL SQL.

    The agent layer validates the generated SQL separately
    before execution.
    """

    client = get_client()

    history = build_history(conversation_history)

    system_prompt = f"""
You are the SQL generation engine for an AI Business Data Analyst.

Your job is ONLY to generate PostgreSQL SELECT queries.

DATABASE SCHEMA
---------------
{schema_context}

STRICT RULES
------------
1. Generate PostgreSQL SQL only.
2. Only use tables and columns present in the schema.
3. Only generate SELECT statements or WITH ... SELECT statements.
4. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE,
   GRANT, REVOKE, or other write/admin statements.
5. Never invent tables, columns, customers, metrics, or data.
6. Use explicit JOIN conditions.
7. When calculating percentages, preserve the correct numeric scale.
8. When the question asks for an average, use AVG().
9. When the question asks for totals, use SUM().
10. When the question asks for counts, use COUNT().
11. When the question asks for highest/lowest, ORDER BY and LIMIT appropriately.
12. Use the available relationships between tables.
13. If multiple months of usage are available, do not accidentally treat
    each customer as having only one record unless the question requires it.
14. For segment adoption questions, calculate the average across available
    usage records joined to customers by customer_id.
15. For MRR questions, use subscriptions.mrr and consider subscription status.
16. For churn-risk questions, use the available customer, subscription,
    usage, and support-ticket information.
17. Return at most 100 rows unless the question explicitly requires otherwise.
18. Do not explain the SQL outside the JSON response.

OUTPUT FORMAT
-------------
Return ONLY valid JSON:

{{
  "sql": "SELECT ...",
  "assumptions": [
    "short assumption if needed"
  ]
}}

If no special assumption is needed, return:

{{
  "sql": "SELECT ...",
  "assumptions": []
}}
"""

    user_prompt = f"""
CURRENT BUSINESS QUESTION
-------------------------
{question}

PREVIOUS CONVERSATION
---------------------
{history}

Generate the PostgreSQL query needed to answer the current question.
Return ONLY the required JSON object.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
        max_tokens=1200,
    )

    content = response.choices[0].message.content or ""

    parsed = parse_json_response(content)

    if parsed:
        sql = parsed.get("sql", "")

        if isinstance(sql, str):
            sql = clean_sql(sql)

        assumptions = parsed.get("assumptions", [])

        if not isinstance(assumptions, list):
            assumptions = []

        return {
            "sql": sql,
            "assumptions": [
                str(item)
                for item in assumptions
                if item
            ],
        }

    # Fallback parsing if model returned plain SQL instead of JSON.
    sql = clean_sql(content)

    if sql:
        return {
            "sql": sql,
            "assumptions": [
                "SQL was generated by the Groq language model."
            ],
        }

    raise RuntimeError(
        "Groq returned an empty or unparseable SQL response."
    )