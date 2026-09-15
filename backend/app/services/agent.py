from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.services.llm import generate_sql
from app.services.sql_validator import validate_sql
from app.services.query_executor import execute_query


# ============================================================
# DATABASE SCHEMA
# ============================================================

SCHEMA_CONTEXT = """
Database: PostgreSQL

Available tables:

customers
- customer_id
- customer_name
- region
- segment
- industry
- status
- created_at

subscriptions
- subscription_id
- customer_id
- plan
- mrr
- start_date
- end_date
- status

usage
- usage_id
- customer_id
- usage_month
- active_users
- licensed_users
- adoption_rate

support_tickets
- ticket_id
- customer_id
- created_at
- category
- priority
- status

revenue_events
- event_id
- customer_id
- event_date
- event_type
- amount

Important relationships:

customers.customer_id = subscriptions.customer_id
customers.customer_id = usage.customer_id
customers.customer_id = support_tickets.customer_id
customers.customer_id = revenue_events.customer_id

Business meanings:

adoption_rate = product adoption percentage
mrr = monthly recurring revenue
active_users = active product users
support_tickets = customer support issues
revenue_events = new, expansion, contraction and churn revenue changes
"""


# ============================================================
# TABLE DETECTION
# ============================================================

def detect_tables(question: str) -> list[str]:
    """
    Identify tables relevant to the business question.

    This is intentionally deterministic so the workflow remains
    explainable even when an LLM is unavailable.
    """

    q = question.lower()

    selected: set[str] = set()

    # --------------------------------------------------------
    # Customers
    # --------------------------------------------------------

    customer_keywords = [
        "customer",
        "customers",
        "company",
        "companies",
        "region",
        "regions",
        "segment",
        "segments",
        "industry",
        "health",
        "business health",
    ]

    if any(word in q for word in customer_keywords):
        selected.add("customers")

    # --------------------------------------------------------
    # Subscriptions
    # --------------------------------------------------------

    subscription_keywords = [
        "mrr",
        "monthly recurring revenue",
        "subscription",
        "subscriptions",
        "plan",
        "plans",
        "revenue by customer",
    ]

    if any(word in q for word in subscription_keywords):
        selected.add("subscriptions")

    # --------------------------------------------------------
    # Usage
    # --------------------------------------------------------

    usage_keywords = [
        "usage",
        "adoption",
        "adoption rate",
        "active users",
        "active user",
        "users",
        "declining usage",
        "decline in usage",
        "declining adoption",
        "low adoption",
        "utilization",
        "churn risk",
        "at risk",
        "risk",
    ]

    if any(word in q for word in usage_keywords):
        selected.add("usage")

    # --------------------------------------------------------
    # Support
    # --------------------------------------------------------

    support_keywords = [
        "ticket",
        "tickets",
        "support",
        "support ticket",
        "support tickets",
        "issue",
        "issues",
        "bug",
        "bugs",
        "reliability",
        "priority",
        "open ticket",
        "ticket volume",
        "churn risk",
        "at risk",
    ]

    if any(word in q for word in support_keywords):
        selected.add("support_tickets")

    # --------------------------------------------------------
    # Revenue Events
    # --------------------------------------------------------

    revenue_keywords = [
        "expansion",
        "expansions",
        "contraction",
        "contractions",
        "revenue event",
        "revenue events",
        "growth driver",
        "growth drivers",
        "revenue growth",
        "revenue impact",
        "churn revenue",
        "new revenue",
    ]

    if any(word in q for word in revenue_keywords):
        selected.add("revenue_events")

    # --------------------------------------------------------
    # Churn questions need multiple tables
    # --------------------------------------------------------

    if any(
        word in q
        for word in [
            "churn",
            "retention",
            "risk",
            "at risk",
        ]
    ):
        selected.update(
            {
                "customers",
                "subscriptions",
                "usage",
                "support_tickets",
            }
        )

    # --------------------------------------------------------
    # If nothing was identified, use customers as the
    # starting point. The agent can still ask for clarification.
    # --------------------------------------------------------

    if not selected:
        selected.add("customers")

    return sorted(selected)


# ============================================================
# WORKFLOW HELPER
# ============================================================

def workflow_step(
    step: str,
    status: str,
    message: str,
    **extra: Any,
) -> dict[str, Any]:

    result = {
        "step": step,
        "status": status,
        "message": message,
    }

    result.update(extra)

    return result


# ============================================================
# DETERMINISTIC FALLBACK SQL
# ============================================================

def fallback_sql(question: str) -> tuple[str, list[str], list[str]]:
    """
    Deterministic SQL for the main assessment scenarios.

    Returns:
        sql,
        tables_used,
        assumptions
    """

    q = question.lower()

    # ========================================================
    # 1. CHURN RISK
    # ========================================================

    if any(
        phrase in q
        for phrase in [
            "churn risk",
            "highest risk",
            "at risk customer",
            "customers at risk",
        ]
    ):

        sql = """
        WITH latest_usage AS (
            SELECT DISTINCT ON (customer_id)
                customer_id,
                usage_month,
                active_users,
                adoption_rate
            FROM usage
            ORDER BY customer_id, usage_month DESC
        ),
        previous_usage AS (
            SELECT DISTINCT ON (customer_id)
                customer_id,
                active_users,
                adoption_rate
            FROM usage
            ORDER BY customer_id, usage_month ASC
        ),
        ticket_summary AS (
            SELECT
                customer_id,
                COUNT(*) AS ticket_count,
                COUNT(*) FILTER (
                    WHERE priority = 'High'
                    AND status = 'Open'
                ) AS high_open_tickets
            FROM support_tickets
            GROUP BY customer_id
        )
        SELECT
            c.customer_id,
            c.customer_name,
            c.region,
            c.segment,
            c.status AS customer_status,
            s.mrr,
            lu.adoption_rate AS latest_adoption,
            pu.adoption_rate AS previous_adoption,
            lu.active_users AS latest_active_users,
            pu.active_users AS previous_active_users,
            COALESCE(ts.ticket_count, 0) AS ticket_count,
            COALESCE(ts.high_open_tickets, 0) AS high_open_tickets,
            (
                CASE
                    WHEN lu.adoption_rate < 50 THEN 40
                    WHEN lu.adoption_rate < 70 THEN 20
                    ELSE 0
                END
                +
                CASE
                    WHEN lu.adoption_rate < pu.adoption_rate THEN 25
                    ELSE 0
                END
                +
                CASE
                    WHEN COALESCE(ts.high_open_tickets, 0) > 0 THEN 35
                    ELSE 0
                END
            ) AS risk_score
        FROM customers c
        LEFT JOIN subscriptions s
            ON c.customer_id = s.customer_id
        LEFT JOIN latest_usage lu
            ON c.customer_id = lu.customer_id
        LEFT JOIN previous_usage pu
            ON c.customer_id = pu.customer_id
        LEFT JOIN ticket_summary ts
            ON c.customer_id = ts.customer_id
        ORDER BY risk_score DESC, s.mrr DESC
        LIMIT 100
        """

        assumptions = [
            "Low adoption below 50% is treated as a strong churn-risk signal.",
            "Declining adoption is treated as a risk signal.",
            "Open high-priority support tickets increase risk.",
            "The churn score is a rule-based indicator, not a prediction model.",
        ]

        return (
            sql,
            [
                "customers",
                "subscriptions",
                "usage",
                "support_tickets",
            ],
            assumptions,
        )

    # ========================================================
    # 2. HIGHEST MRR REGION
    # ========================================================

    if (
        "highest mrr" in q
        or "mrr region" in q
        or "region has the highest" in q
    ):

        sql = """
        SELECT
            c.region,
            SUM(s.mrr) AS total_mrr,
            COUNT(DISTINCT c.customer_id) AS customer_count
        FROM customers c
        JOIN subscriptions s
            ON c.customer_id = s.customer_id
        WHERE s.status = 'active'
        GROUP BY c.region
        ORDER BY total_mrr DESC
        LIMIT 100
        """

        return (
            sql,
            ["customers", "subscriptions"],
            [
                "Only active subscriptions are included in regional MRR."
            ],
        )

    # ========================================================
    # 3. RECENT EXPANSION
    # ========================================================

    if (
        "expansion" in q
        or "expanded" in q
        or "recent revenue" in q
    ):

        sql = """
        SELECT
            r.event_id,
            r.event_date,
            c.customer_id,
            c.customer_name,
            c.region,
            r.event_type,
            r.amount
        FROM revenue_events r
        JOIN customers c
            ON r.customer_id = c.customer_id
        WHERE r.event_type = 'expansion'
        ORDER BY r.event_date DESC
        LIMIT 100
        """

        return (
            sql,
            ["revenue_events", "customers"],
            [
                "Expansion is identified using revenue_events.event_type = 'expansion'."
            ],
        )

    # ========================================================
    # 4. LOW ADOPTION + SUPPORT TICKETS
    # ========================================================

    if (
        "low adoption" in q
        or (
            "adoption" in q
            and "ticket" in q
        )
    ):

        sql = """
        WITH latest_usage AS (
            SELECT DISTINCT ON (customer_id)
                customer_id,
                usage_month,
                active_users,
                adoption_rate
            FROM usage
            ORDER BY customer_id, usage_month DESC
        ),
        ticket_summary AS (
            SELECT
                customer_id,
                COUNT(*) AS ticket_count,
                COUNT(*) FILTER (
                    WHERE status = 'Open'
                ) AS open_ticket_count
            FROM support_tickets
            GROUP BY customer_id
        )
        SELECT
            c.customer_id,
            c.customer_name,
            c.region,
            c.segment,
            lu.adoption_rate AS latest_adoption,
            lu.active_users AS latest_active_users,
            COALESCE(ts.ticket_count, 0) AS ticket_count,
            COALESCE(ts.open_ticket_count, 0) AS open_ticket_count
        FROM customers c
        JOIN latest_usage lu
            ON c.customer_id = lu.customer_id
        LEFT JOIN ticket_summary ts
            ON c.customer_id = ts.customer_id
        WHERE lu.adoption_rate < 50
          AND COALESCE(ts.ticket_count, 0) > 0
        ORDER BY lu.adoption_rate ASC
        LIMIT 100
        """

        return (
            sql,
            [
                "customers",
                "usage",
                "support_tickets",
            ],
            [
                "Latest available usage record is used for adoption.",
                "Adoption below 50% is treated as low adoption for this analysis.",
            ],
        )

    # ========================================================
    # 5. HIGHEST AVERAGE ADOPTION SEGMENT
    # ========================================================

    if (
        "highest average adoption" in q
        or "average adoption segment" in q
        or (
            "average adoption" in q
            and "segment" in q
        )
        or (
            "adoption rate" in q
            and "segment" in q
        )
    ):

        sql = """
        SELECT
            c.segment,
            ROUND(AVG(u.adoption_rate), 2) AS average_adoption,
            COUNT(DISTINCT c.customer_id) AS customer_count
        FROM customers c
        JOIN usage u
            ON c.customer_id = u.customer_id
        GROUP BY c.segment
        ORDER BY average_adoption DESC
        LIMIT 100
        """

        return (
            sql,
            ["customers", "usage"],
            [
                "Average adoption is calculated across available usage records."
            ],
        )

    # ========================================================
    # 6. REVENUE GROWTH DRIVERS
    # ========================================================

    if (
        "growth driver" in q
        or "growth drivers" in q
        or "revenue growth" in q
        or "revenue drivers" in q
    ):

        sql = """
        SELECT
            event_type,
            COUNT(*) AS event_count,
            SUM(amount) AS total_amount
        FROM revenue_events
        GROUP BY event_type
        ORDER BY total_amount DESC
        LIMIT 100
        """

        return (
            sql,
            ["revenue_events"],
            [
                "Revenue growth drivers are evaluated from recorded revenue events.",
                "Positive event amounts contribute positively and negative amounts reduce revenue.",
            ],
        )

    # ========================================================
    # 7. HIGH TICKET VOLUME + DECLINING USAGE
    # ========================================================

    if (
        "high ticket volume" in q
        or (
            "ticket volume" in q
            and "declining usage" in q
        )
        or (
            "tickets" in q
            and "declining usage" in q
        )
    ):

        sql = """
        WITH usage_change AS (
            SELECT
                customer_id,
                MAX(adoption_rate) FILTER (
                    WHERE usage_month = (
                        SELECT MIN(u2.usage_month)
                        FROM usage u2
                        WHERE u2.customer_id = usage.customer_id
                    )
                ) AS previous_adoption,
                MAX(adoption_rate) FILTER (
                    WHERE usage_month = (
                        SELECT MAX(u3.usage_month)
                        FROM usage u3
                        WHERE u3.customer_id = usage.customer_id
                    )
                ) AS latest_adoption
            FROM usage
            GROUP BY customer_id
        ),
        ticket_summary AS (
            SELECT
                customer_id,
                COUNT(*) AS ticket_count
            FROM support_tickets
            GROUP BY customer_id
        )
        SELECT
            c.customer_id,
            c.customer_name,
            c.region,
            c.segment,
            uc.previous_adoption,
            uc.latest_adoption,
            (
                uc.latest_adoption - uc.previous_adoption
            ) AS adoption_change,
            ts.ticket_count
        FROM customers c
        JOIN usage_change uc
            ON c.customer_id = uc.customer_id
        JOIN ticket_summary ts
            ON c.customer_id = ts.customer_id
        WHERE uc.latest_adoption < uc.previous_adoption
          AND ts.ticket_count >= 1
          AND c.status = 'active'
        ORDER BY ts.ticket_count DESC, adoption_change ASC
        LIMIT 100
        """

        return (
            sql,
            [
                "customers",
                "usage",
                "support_tickets",
            ],
            [
                "A customer is considered to have declining usage when latest adoption is below previous adoption.",
                "At least one support ticket is treated as ticket volume for this small prototype dataset.",
            ],
        )

    # ========================================================
    # 8. BUSINESS HEALTH BY REGION
    # ========================================================

    if (
        "business health" in q
        or "health by region" in q
        or "region health" in q
    ):

        sql = """
        WITH latest_usage AS (
            SELECT DISTINCT ON (customer_id)
                customer_id,
                adoption_rate
            FROM usage
            ORDER BY customer_id, usage_month DESC
        ),
        ticket_summary AS (
            SELECT
                customer_id,
                COUNT(*) AS ticket_count,
                COUNT(*) FILTER (
                    WHERE status = 'Open'
                ) AS open_ticket_count
            FROM support_tickets
            GROUP BY customer_id
        )
        SELECT
            c.region,
            COUNT(DISTINCT c.customer_id) AS customers,
            SUM(
                CASE
                    WHEN s.status = 'active'
                    THEN s.mrr
                    ELSE 0
                END
            ) AS active_mrr,
            ROUND(AVG(lu.adoption_rate), 2) AS average_adoption,
            COALESCE(SUM(ts.ticket_count), 0) AS ticket_count,
            COALESCE(SUM(ts.open_ticket_count), 0) AS open_ticket_count
        FROM customers c
        LEFT JOIN subscriptions s
            ON c.customer_id = s.customer_id
        LEFT JOIN latest_usage lu
            ON c.customer_id = lu.customer_id
        LEFT JOIN ticket_summary ts
            ON c.customer_id = ts.customer_id
        GROUP BY c.region
        ORDER BY active_mrr DESC
        LIMIT 100
        """

        return (
            sql,
            [
                "customers",
                "subscriptions",
                "usage",
                "support_tickets",
            ],
            [
                "Regional health is represented using active MRR, average adoption and support activity."
            ],
        )

    # ========================================================
    # 9. TOP CHURN REASONS / SUPPORT CATEGORIES
    # ========================================================

    if (
        "churn reason" in q
        or "churn reasons" in q
        or "reason for churn" in q
    ):

        sql = """
        SELECT
            st.category,
            COUNT(*) AS ticket_count,
            COUNT(*) FILTER (
                WHERE st.priority = 'High'
            ) AS high_priority_tickets,
            COUNT(*) FILTER (
                WHERE st.status = 'Open'
            ) AS open_tickets
        FROM support_tickets st
        JOIN customers c
            ON st.customer_id = c.customer_id
        WHERE c.status = 'churned'
        GROUP BY st.category
        ORDER BY ticket_count DESC, high_priority_tickets DESC
        LIMIT 100
        """

        return (
            sql,
            ["support_tickets", "customers"],
            [
                "The dataset does not contain a dedicated churn-reason field.",
                "Support ticket categories are used as a proxy for churn reasons.",
            ],
        )

    # ========================================================
    # 10. MISSING CHURN DATA
    # ========================================================

    if (
        "missing churn" in q
        or "churn data" in q
        or "missing data" in q
    ):

        sql = """
        SELECT
            c.customer_id,
            c.customer_name,
            c.status,
            'No recorded churn event' AS churn_data_status
        FROM customers c
        WHERE NOT EXISTS (
            SELECT 1
            FROM revenue_events r
            WHERE r.customer_id = c.customer_id
              AND r.event_type = 'churn'
        )
        ORDER BY c.customer_id
        LIMIT 100
        """

        return (
            sql,
            ["customers", "revenue_events"],
            [
                "Missing churn data is interpreted as customers without a recorded revenue_events event_type = 'churn'."
            ],
        )

    # ========================================================
    # DEFAULT
    # ========================================================

    sql = """
    SELECT
        customer_id,
        customer_name,
        region,
        segment,
        industry,
        status,
        created_at
    FROM customers
    ORDER BY customer_id
    LIMIT 100
    """

    return (
        sql,
        ["customers"],
        [
            "The question did not match a specialized deterministic analysis rule.",
            "Customer records are returned as a safe fallback.",
        ],
    )


# ============================================================
# RESULT EXPLANATION
# ============================================================

def build_answer(
    question: str,
    rows: list[dict[str, Any]],
    tables_used: list[str],
    assumptions: list[str],
) -> str:

    if not rows:
        return (
            "I could not find enough matching data to answer this "
            "question from the available tables."
        )

    q = question.lower()

    first = rows[0]

    # ========================================================
    # CHURN RISK
    # ========================================================

    if "churn risk" in q or "highest risk" in q:

        name = first.get("customer_name", "The top customer")
        score = first.get("risk_score", first.get("churn_risk_score", "N/A"))
        adoption = first.get("latest_adoption", first.get("latest_adoption_rate", first.get("adoption_rate", "N/A")))
        high_tickets = first.get("high_open_tickets", first.get("open_high_priority_tickets", 0))
        status = first.get("customer_status", "unknown")

        return (
            f"**{name}** has the highest calculated churn-risk score "
            f"({score}). Latest adoption is {adoption}% and there are "
            f"{high_tickets} open high-priority support ticket(s). "
            f"The customer's current status is **{status}**. "
            f"The risk score is a rule-based indicator, not a prediction model."
        )

    # ========================================================
    # MRR REGION
    # ========================================================

    if (
        "highest mrr" in q
        or "mrr region" in q
        or "highest mrr region" in q
    ):

        region = first.get("region", "Unknown")
        mrr = first.get("total_mrr", 0)

        return (
            f"**{region}** has the highest active MRR at "
            f"**${float(mrr):,.0f}**."
        )

    # ========================================================
    # EXPANSION
    # ========================================================

    if "expansion" in q or "expanded" in q:

        if len(rows) == 1:

            name = rows[0].get("customer_name", "Customer")
            amount = rows[0].get("amount", 0)

            return (
                f"**{name}** has a recorded expansion event of "
                f"**${float(amount):,.0f}**."
            )

        total = sum(
            float(row.get("amount") or 0)
            for row in rows
        )

        names = ", ".join(
            str(row.get("customer_name"))
            for row in rows[:3]
        )

        return (
            f"I found **{len(rows)} expansion event(s)** totaling "
            f"**${total:,.0f}**. The most recent customers include "
            f"{names}."
        )

    # ========================================================
    # AVERAGE ADOPTION SEGMENT
    # ========================================================

    if (
        ("average adoption" in q or "adoption rate" in q)
        and "segment" in q
    ):

        if len(rows) > 1:
            summary = "; ".join(
                f"**{row.get('segment', 'Unknown')}**: "
                f"{float(row.get('average_adoption', 0)):.1f}%"
                for row in rows
            )
            segment = first.get("segment", "Unknown")
            adoption = first.get("average_adoption", first.get("avg_adoption", first.get("avg_adoption_rate", 0)))

            return (
                f"The segment averages are: {summary}. "
                f"**{segment}** has the highest average adoption at "
                f"**{float(adoption):.1f}%**."
            )

        segment = first.get("segment", "Unknown")
        adoption = first.get("average_adoption", 0)

        return (
            f"**{segment}** has the highest average adoption at "
            f"**{float(adoption):.1f}%** across the available usage records."
        )

    # ========================================================
    # REVENUE GROWTH
    # ========================================================

    if (
        "growth driver" in q
        or "growth drivers" in q
        or "revenue growth" in q
    ):

        event_type = first.get("event_type", "Unknown")
        amount = first.get("total_amount", 0)

        return (
            f"**{event_type.title()}** is the largest positive revenue "
            f"driver in the available events, with a net recorded amount "
            f"of **${float(amount):,.0f}**."
        )

    # ========================================================
    # LOW ADOPTION
    # ========================================================

    if "low adoption" in q or ("adoption" in q and "ticket" in q):

        names = ", ".join(
            str(row.get("customer_name"))
            for row in rows[:3]
        )

        return (
            f"I found **{len(rows)} customer(s)** with low adoption "
            f"and support activity. The customers include **{names}**."
        )

    # ========================================================
    # BUSINESS HEALTH
    # ========================================================

    if "business health" in q or "region health" in q:

        region = first.get("region", "Unknown")
        mrr = first.get(
            "active_mrr",
            first.get(
                "total_active_mrr",
                first.get("total_mrr", 0),
            ),
        )
        adoption = first.get(
            "average_adoption",
            first.get(
                "avg_adoption",
                first.get("avg_adoption_rate", 0),
            ),
        )

        return (
            f"**{region}** ranks highest by active MRR at "
            f"**${float(mrr):,.0f}**, with average adoption of "
            f"**{float(adoption):.1f}%**."
        )

    # ========================================================
    # CHURN REASONS
    # ========================================================

    if "churn reason" in q or "churn reasons" in q:

        category = first.get("category", "Unknown")
        count = first.get("ticket_count", 0)

        return (
            f"**{category}** is the most represented support category "
            f"among churned customers, with {count} ticket(s). "
            f"This is a proxy for churn reason because the dataset "
            f"does not contain a dedicated churn-reason field."
        )

    # ========================================================
    # HIGH TICKET + DECLINING USAGE
    # ========================================================

    if (
        "declining usage" in q
        or "high ticket volume" in q
    ):

        names = ", ".join(
            str(row.get("customer_name"))
            for row in rows[:3]
        )

        return (
            f"I found **{len(rows)} active customer(s)** with declining "
            f"adoption and support activity. The customers include "
            f"**{names}**."
        )

    # ========================================================
    # DEFAULT
    # ========================================================

    return (
        f"I found **{len(rows)} result(s)** relevant to the question. "
        f"The analysis used: {', '.join(tables_used)}."
    )


# ============================================================
# RESULT SHAPE VALIDATION
# ============================================================

def result_matches_question(question: str, rows: list[dict[str, Any]]) -> bool:
    """Verify that a safe AI query returned fields needed for the question."""
    if not rows:
        return True

    q = question.lower()
    keys = {str(k).lower() for k in rows[0].keys()}

    def has_any(*names: str) -> bool:
        return any(name.lower() in keys for name in names)

    if "churn risk" in q or "highest risk" in q:
        return (
            has_any("customer_name")
            and has_any("risk_score", "churn_risk_score")
            and has_any("latest_adoption", "latest_adoption_rate", "adoption_rate")
            and has_any("high_open_tickets", "open_high_priority_tickets")
        )

    if "highest mrr" in q or "mrr region" in q or "highest mrr region" in q:
        return has_any("region") and has_any("total_mrr", "active_mrr")

    if "low adoption" in q and "ticket" in q:
        return has_any("customer_name") and has_any("latest_adoption", "adoption_rate") and has_any("ticket_count")

    if ("average adoption" in q or "adoption rate" in q) and "segment" in q:
        return has_any("segment") and has_any("average_adoption", "avg_adoption", "avg_adoption_rate")

    if "high ticket volume" in q or ("ticket volume" in q and "declining usage" in q) or ("tickets" in q and "declining usage" in q):
        return (
            has_any("customer_name")
            and has_any("previous_adoption", "previous_adoption_rate")
            and has_any("latest_adoption", "latest_adoption_rate")
            and has_any("ticket_count")
        )

    if "business health" in q or "region health" in q:
        if not (
            has_any("region")
            and has_any("active_mrr", "total_active_mrr", "total_mrr")
            and has_any("average_adoption", "avg_adoption", "avg_adoption_rate")
            and has_any("ticket_count", "total_support_tickets")
        ):
            return False

        # In this prototype there are known active subscriptions.
        # If an AI query returns zero MRR for every region, it is
        # almost certainly using the wrong subscription/status field
        # or joining the data incorrectly.
        mrr_key = next(
            (
                key
                for key in [
                    "active_mrr",
                    "total_active_mrr",
                    "total_mrr",
                ]
                if key in keys
            ),
            None,
        )

        if mrr_key:
            try:
                all_zero = all(
                    float(row.get(mrr_key) or 0) == 0
                    for row in rows
                )
                if all_zero:
                    return False
            except (TypeError, ValueError):
                return False

        return True

    if "churn reason" in q or "churn reasons" in q or "reason for churn" in q:
        return has_any("category") and has_any("ticket_count")

    if "missing churn" in q or "churn data" in q or "missing data" in q:
        return has_any("customer_id") and has_any("customer_name")

    if "expansion" in q or "expanded" in q or "recent revenue" in q:
        return has_any("event_date") and has_any("amount")

    if "growth driver" in q or "growth drivers" in q or "revenue growth" in q or "revenue drivers" in q:
        return has_any("event_type") and has_any("total_amount", "amount")

    return True


def normalize_result_rows(question: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize common equivalent aliases returned by AI-generated SQL."""
    normalized = []

    aliases = {
        "avg_adoption": "average_adoption",
        "avg_adoption_rate": "average_adoption",
        "total_active_mrr": "active_mrr",
        "open_high_priority_tickets": "high_open_tickets",
        "latest_adoption_rate": "latest_adoption",
        "previous_adoption_rate": "previous_adoption",
        "total_support_tickets": "ticket_count",
    }

    for row in rows:
        item = dict(row)
        for source, target in aliases.items():
            if target not in item and source in item:
                item[target] = item[source]
        normalized.append(item)

    return normalized


# ============================================================
# FOLLOW-UP DETECTION
# ============================================================

def is_follow_up(question: str) -> bool:

    q = question.lower().strip()

    follow_up_phrases = [
        "what should we do",
        "what should i do",
        "what can we do",
        "what action",
        "next step",
        "next steps",
        "recommend",
        "recommendation",
        "recommendations",
        "how should we",
        "how can we",
        "tell me more",
        "why",
        "explain that",
        "explain more",
        "give me evidence",
        "show me evidence",
        "more evidence",
    ]

    return any(
        phrase in q
        for phrase in follow_up_phrases
    )


# ============================================================
# FOLLOW-UP ANSWER
# ============================================================

def build_follow_up_answer(
    question: str,
    previous_answer: str | None,
    previous_evidence: list[dict[str, Any]],
) -> str:

    q = question.lower()

    if not previous_evidence:

        return (
            "I don't have enough previous result evidence to make "
            "a specific recommendation. Please ask the original "
            "business question first."
        )

    first = previous_evidence[0]

    # ========================================================
    # RECOMMENDATION
    # ========================================================

    if any(
        phrase in q
        for phrase in [
            "what should we do",
            "what should i do",
            "what action",
            "next step",
            "recommend",
            "recommendation",
            "how should we",
        ]
    ):

        name = first.get(
            "customer_name",
            "the customer",
        )

        adoption = first.get(
            "latest_adoption"
        )

        high_tickets = first.get(
            "high_open_tickets",
            0,
        )

        actions = []

        if adoption is not None:
            try:
                if float(adoption) < 50:
                    actions.append(
                        "schedule an immediate customer success review "
                        "focused on adoption"
                    )
            except (TypeError, ValueError):
                pass

        if high_tickets:
            actions.append(
                "prioritize resolution of the open high-priority support issue"
            )

        actions.append(
            "review recent product usage with the customer"
        )

        actions.append(
            "create a short-term adoption recovery plan"
        )

        return (
            f"For **{name}**, I would prioritize: "
            + "; ".join(actions)
            + ". These recommendations are based on the evidence "
            "from the previous analysis rather than introducing new data."
        )

    # ========================================================
    # EVIDENCE
    # ========================================================

    if "evidence" in q or "show me" in q:

        evidence_parts = []

        for key in [
            "customer_name",
            "customer_status",
            "mrr",
            "latest_adoption",
            "previous_adoption",
            "latest_active_users",
            "previous_active_users",
            "high_open_tickets",
            "ticket_count",
            "risk_score",
        ]:

            if key in first:
                evidence_parts.append(
                    f"{key.replace('_', ' ')} = {first[key]}"
                )

        if evidence_parts:

            return (
                f"Here is the evidence supporting the previous result: "
                + ", ".join(evidence_parts)
                + "."
            )

    # ========================================================
    # DEFAULT FOLLOW-UP
    # ========================================================

    return (
        "The previous analysis was based on the returned database "
        "evidence. The strongest available signal is the first "
        "result shown in the evidence table."
    )


# ============================================================
# MAIN AGENT
# ============================================================

def analyze_question(
    db: Session,
    question: str,
    conversation_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:

    conversation_history = conversation_history or []

    workflow: list[dict[str, Any]] = []

    question = question.strip()

    if not question:

        return {
            "success": False,
            "answer": "Please enter a business question.",
            "workflow": [],
            "tables_used": [],
            "evidence": [],
            "assumptions": [],
            "ai_used": False,
        }

    # ========================================================
    # FOLLOW-UP CHECK
    # ========================================================

    previous_result = None

    if conversation_history:

        for item in reversed(conversation_history):

            if (
                isinstance(item, dict)
                and item.get("result")
            ):
                previous_result = item["result"]
                break

    if (
        previous_result
        and is_follow_up(question)
    ):

        previous_evidence = (
            previous_result.get("evidence", [])
            if isinstance(previous_result, dict)
            else []
        )

        answer = build_follow_up_answer(
            question,
            previous_result.get("answer"),
            previous_evidence,
        )

        workflow.extend(
            [
                workflow_step(
                    "understand_question",
                    "completed",
                    "Follow-up question understood using previous conversation context.",
                ),
                workflow_step(
                    "validate_result",
                    "completed",
                    "Previous analysis evidence reused for the follow-up.",
                ),
                workflow_step(
                    "explain_result",
                    "completed",
                    "Recommendation generated from previous evidence.",
                ),
            ]
        )

        return {
            "success": True,
            "answer": answer,
            "workflow": workflow,
            "tables_used": previous_result.get(
                "tables_used",
                [],
            ),
            "sql": previous_result.get(
                "sql",
                "",
            ),
            "columns": previous_result.get(
                "columns",
                [],
            ),
            "evidence": previous_evidence,
            "row_count": len(previous_evidence),
            "assumptions": [
                "Follow-up uses evidence from the previous analysis.",
                "No new facts are introduced beyond the available database evidence.",
            ],
            "ai_used": previous_result.get(
                "ai_used",
                False,
            ),
        }

    # ========================================================
    # STEP 1 — UNDERSTAND
    # ========================================================

    workflow.append(
        workflow_step(
            "understand_question",
            "completed",
            "Business question understood.",
        )
    )

    # ========================================================
    # STEP 2 — SELECT TABLES
    # ========================================================

    detected_tables = detect_tables(question)

    workflow.append(
        workflow_step(
            "select_tables",
            "completed",
            "Relevant tables identified.",
            tables=detected_tables,
        )
    )

    # ========================================================
    # STEP 3 — GENERATE SQL
    # ========================================================

    sql = None
    ai_used = False
    assumptions: list[str] = []

    # --------------------------------------------------------
    # Try LLM first
    # --------------------------------------------------------

    try:

        llm_result = generate_sql(
            question=question,
            schema_context=SCHEMA_CONTEXT,
            conversation_history=conversation_history,
        )

        if isinstance(llm_result, dict):

            sql = llm_result.get("sql")

            if llm_result.get("assumptions"):
                assumptions.extend(
                    llm_result["assumptions"]
                )

            if sql:
                ai_used = True

        elif isinstance(llm_result, str):

            sql = llm_result

            if sql:
                ai_used = True

    except Exception as error:

        sql = None
        ai_used = False

        workflow.append(
            workflow_step(
                "generate_sql",
                "failed",
                f"Groq SQL generation failed: {str(error)}",
                ai_used=False,
            )
        )

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not sql:

        sql, fallback_tables, fallback_assumptions = (
            fallback_sql(question)
        )

        detected_tables = fallback_tables

        assumptions.extend(
            fallback_assumptions
        )

        workflow.append(
            workflow_step(
                "generate_sql",
                "fallback",
                "Using deterministic analyst rules.",
                ai_used=False,
            )
        )

    else:

        workflow.append(
            workflow_step(
                "generate_sql",
                "completed",
                "SQL generated by the AI model.",
                ai_used=True,
            )
        )

    # ========================================================
    # STEP 4 — VALIDATE SQL
    # ========================================================

    try:

        validation = validate_sql(sql)

        # Support both:
        # validate_sql(...) -> True
        # validate_sql(...) -> {"valid": True, ...}

        if isinstance(validation, dict):

            valid = validation.get(
                "valid",
                False,
            )

            validation_message = validation.get(
                "message",
                "SQL passed safety validation.",
            )

        else:

            valid = bool(validation)

            validation_message = (
                "SQL passed safety validation."
                if valid
                else "SQL failed safety validation."
            )

    except Exception as error:

        valid = False

        validation_message = str(error)

    # --------------------------------------------------------
    # If AI SQL fails, use safe deterministic fallback
    # --------------------------------------------------------

    if not valid and ai_used:

        workflow.append(
            workflow_step(
                "validate_sql",
                "failed",
                f"AI-generated SQL failed validation: {validation_message}",
            )
        )

        fallback_result = fallback_sql(question)

        sql = fallback_result[0]
        detected_tables = fallback_result[1]

        assumptions.extend(
            fallback_result[2]
        )

        ai_used = False

        workflow.append(
            workflow_step(
                "fallback_analysis",
                "completed",
                "AI query was rejected, so deterministic analyst rules were used.",
            )
        )

        try:

            validation = validate_sql(sql)

            if isinstance(validation, dict):
                valid = validation.get(
                    "valid",
                    False,
                )
                validation_message = validation.get(
                    "message",
                    "SQL passed safety validation.",
                )
            else:
                valid = bool(validation)
                validation_message = (
                    "SQL passed safety validation."
                )

        except Exception as error:

            valid = False
            validation_message = str(error)

    # --------------------------------------------------------
    # Final validation failure
    # --------------------------------------------------------

    if not valid:

        return {
            "success": False,
            "answer": (
                "I generated a query, but it did not pass "
                "the safety validation step. I did not execute it."
            ),
            "workflow": workflow
            + [
                workflow_step(
                    "validate_sql",
                    "failed",
                    validation_message,
                )
            ],
            "tables_used": detected_tables,
            "sql": sql,
            "evidence": [],
            "assumptions": assumptions,
            "ai_used": ai_used,
        }

    # ========================================================
    # VALIDATION SUCCESS
    # ========================================================

    workflow.append(
        workflow_step(
            "validate_sql",
            "completed",
            "SQL passed safety validation.",
        )
    )

    # ========================================================
    # STEP 5 — EXECUTE
    # ========================================================

    try:

        execution_result = execute_query(
            db,
            sql,
        )

        # Support dictionary result
        if isinstance(execution_result, dict):

            rows = execution_result.get(
                "rows",
                [],
            )

            columns = execution_result.get(
                "columns",
                [],
            )

        else:

            rows = execution_result
            columns = (
                list(rows[0].keys())
                if rows
                else []
            )

        if rows is None:
            rows = []

        rows = normalize_result_rows(question, rows)

        # Safe SQL can still answer the wrong business question.
        # Verify the result shape and fall back to deterministic rules
        # when the AI result cannot support the requested analysis.
        if ai_used and not result_matches_question(question, rows):
            fallback_result = fallback_sql(question)

            workflow.append(
                workflow_step(
                    "validate_result",
                    "failed",
                    "AI query returned fields that do not support the requested business analysis. Deterministic verification is being used.",
                )
            )

            sql = fallback_result[0]
            detected_tables = fallback_result[1]
            assumptions.extend(fallback_result[2])
            ai_used = False

            try:
                fallback_execution = execute_query(db, sql)

                if isinstance(fallback_execution, dict):
                    rows = fallback_execution.get("rows", []) or []
                    columns = fallback_execution.get("columns", [])
                else:
                    rows = fallback_execution or []
                    columns = list(rows[0].keys()) if rows else []

                rows = normalize_result_rows(question, rows)

                workflow.append(
                    workflow_step(
                        "fallback_analysis",
                        "completed",
                        "Deterministic analyst rules verified the requested business result.",
                    )
                )
            except Exception as fallback_error:
                workflow.append(
                    workflow_step(
                        "fallback_analysis",
                        "failed",
                        f"Fallback query execution failed: {str(fallback_error)}",
                    )
                )
                return {
                    "success": False,
                    "answer": "The AI result could not be verified and the deterministic verification query also failed.",
                    "workflow": workflow,
                    "tables_used": detected_tables,
                    "sql": sql,
                    "columns": [],
                    "evidence": [],
                    "row_count": 0,
                    "assumptions": assumptions,
                    "ai_used": False,
                }

    except Exception as error:

        workflow.append(
            workflow_step(
                "execute_query",
                "failed",
                f"Query execution failed: {str(error)}",
            )
        )

        return {
            "success": False,
            "answer": (
                "The validated query could not be executed. "
                "No result was returned."
            ),
            "workflow": workflow,
            "tables_used": detected_tables,
            "sql": sql,
            "columns": [],
            "evidence": [],
            "row_count": 0,
            "assumptions": assumptions,
            "ai_used": ai_used,
        }

    workflow.append(
        workflow_step(
            "execute_query",
            "completed",
            "Query executed successfully.",
        )
    )

    # ========================================================
    # STEP 6 — VALIDATE RESULT
    # ========================================================

    if not rows:

        workflow.append(
            workflow_step(
                "validate_result",
                "completed",
                "Query executed successfully but returned no matching data.",
            )
        )

        answer = (
            "I could not find matching data in the available tables. "
            "I did not invent a result."
        )

    else:

        workflow.append(
            workflow_step(
                "validate_result",
                "completed",
                "Result contains data.",
            )
        )

        # ====================================================
        # STEP 7 — EXPLAIN RESULT
        # ====================================================

        answer = build_answer(
            question,
            rows,
            detected_tables,
            assumptions,
        )

    workflow.append(
        workflow_step(
            "explain_result",
            "completed",
            "Business explanation generated with evidence.",
        )
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "success": True,
        "answer": answer,
        "workflow": workflow,
        "tables_used": detected_tables,
        "sql": sql.strip(),
        "columns": columns,
        "evidence": normalize_result_rows(question, rows[:100]),
        "row_count": len(rows),
        "assumptions": assumptions,
        "ai_used": ai_used,
    }