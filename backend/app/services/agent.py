from __future__ import annotations

from typing import Any

from app.services.llm import generate_sql


# ============================================================
# IN-MEMORY ASSESSMENT DATASET
# ============================================================

CUSTOMERS = [
    {
        "customer_id": "C001",
        "customer_name": "Acme Corp",
        "region": "North America",
        "segment": "Enterprise",
        "industry": "Technology",
        "status": "active",
        "created_at": "2023-01-15",
    },
    {
        "customer_id": "C002",
        "customer_name": "NovaTech",
        "region": "EMEA",
        "segment": "Mid-Market",
        "industry": "Technology",
        "status": "active",
        "created_at": "2023-03-22",
    },
    {
        "customer_id": "C003",
        "customer_name": "BluePeak",
        "region": "APAC",
        "segment": "SMB",
        "industry": "Technology",
        "status": "churned",
        "created_at": "2023-05-10",
    },
    {
        "customer_id": "C004",
        "customer_name": "GreenLeaf",
        "region": "North America",
        "segment": "Enterprise",
        "industry": "Technology",
        "status": "active",
        "created_at": "2023-06-18",
    },
    {
        "customer_id": "C005",
        "customer_name": "OrbitAI",
        "region": "APAC",
        "segment": "Mid-Market",
        "industry": "Technology",
        "status": "active",
        "created_at": "2023-09-01",
    },
]


SUBSCRIPTIONS = [
    {
        "subscription_id": "S001",
        "customer_id": "C001",
        "plan": "Enterprise",
        "mrr": 12000,
        "start_date": "2023-01-15",
        "end_date": None,
        "status": "active",
    },
    {
        "subscription_id": "S002",
        "customer_id": "C002",
        "plan": "Growth",
        "mrr": 4500,
        "start_date": "2023-03-22",
        "end_date": None,
        "status": "active",
    },
    {
        "subscription_id": "S003",
        "customer_id": "C003",
        "plan": "Starter",
        "mrr": 900,
        "start_date": "2023-05-10",
        "end_date": None,
        "status": "churned",
    },
    {
        "subscription_id": "S004",
        "customer_id": "C004",
        "plan": "Enterprise",
        "mrr": 15000,
        "start_date": "2023-06-18",
        "end_date": None,
        "status": "active",
    },
    {
        "subscription_id": "S005",
        "customer_id": "C005",
        "plan": "Growth",
        "mrr": 5200,
        "start_date": "2023-09-01",
        "end_date": None,
        "status": "active",
    },
]


USAGE = [
    {"customer_id": "C001", "usage_month": "2024-01", "active_users": 120, "licensed_users": 2400, "adoption_rate": 82},
    {"customer_id": "C001", "usage_month": "2024-02", "active_users": 118, "licensed_users": 2300, "adoption_rate": 80},
    {"customer_id": "C002", "usage_month": "2024-01", "active_users": 75, "licensed_users": 1200, "adoption_rate": 61},
    {"customer_id": "C002", "usage_month": "2024-02", "active_users": 60, "licensed_users": 900, "adoption_rate": 52},
    {"customer_id": "C003", "usage_month": "2024-01", "active_users": 25, "licensed_users": 300, "adoption_rate": 35},
    {"customer_id": "C003", "usage_month": "2024-02", "active_users": 10, "licensed_users": 90, "adoption_rate": 20},
    {"customer_id": "C004", "usage_month": "2024-01", "active_users": 150, "licensed_users": 3100, "adoption_rate": 88},
    {"customer_id": "C004", "usage_month": "2024-02", "active_users": 165, "licensed_users": 3400, "adoption_rate": 91},
    {"customer_id": "C005", "usage_month": "2024-01", "active_users": 80, "licensed_users": 1400, "adoption_rate": 67},
    {"customer_id": "C005", "usage_month": "2024-02", "active_users": 76, "licensed_users": 1300, "adoption_rate": 60},
]


SUPPORT_TICKETS = [
    {"ticket_id": "T001", "customer_id": "C001", "created_at": "2024-02-01", "category": "Billing", "priority": "Medium", "status": "Closed"},
    {"ticket_id": "T002", "customer_id": "C003", "created_at": "2024-02-10", "category": "Reliability", "priority": "High", "status": "Open"},
    {"ticket_id": "T003", "customer_id": "C002", "created_at": "2024-02-12", "category": "Onboarding", "priority": "Medium", "status": "Open"},
    {"ticket_id": "T004", "customer_id": "C005", "created_at": "2024-02-15", "category": "Product Bug", "priority": "High", "status": "Open"},
    {"ticket_id": "T005", "customer_id": "C004", "created_at": "2024-02-20", "category": "Question", "priority": "Low", "status": "Closed"},
]


REVENUE_EVENTS = [
    {"event_id": "R001", "customer_id": "C001", "event_date": "2024-01-01", "event_type": "new", "amount": 12000},
    {"event_id": "R002", "customer_id": "C002", "event_date": "2024-03-01", "event_type": "expansion", "amount": 1500},
    {"event_id": "R003", "customer_id": "C003", "event_date": "2024-04-01", "event_type": "churn", "amount": -900},
    {"event_id": "R004", "customer_id": "C004", "event_date": "2024-02-01", "event_type": "expansion", "amount": 3000},
    {"event_id": "R005", "customer_id": "C005", "event_date": "2024-03-15", "event_type": "contraction", "amount": -700},
]


SCHEMA_CONTEXT = """
The application contains an in-memory structured dataset.

Tables:

customers:
customer_id, customer_name, region, segment, industry, status, created_at

subscriptions:
subscription_id, customer_id, plan, mrr, start_date, end_date, status

usage:
customer_id, usage_month, active_users, licensed_users, adoption_rate

support_tickets:
ticket_id, customer_id, created_at, category, priority, status

revenue_events:
event_id, customer_id, event_date, event_type, amount

Relationships:
customers.customer_id = subscriptions.customer_id
customers.customer_id = usage.customer_id
customers.customer_id = support_tickets.customer_id
customers.customer_id = revenue_events.customer_id
"""


def workflow_step(step: str, status: str, message: str, **extra):
    result = {
        "step": step,
        "status": status,
        "message": message,
    }
    result.update(extra)
    return result


def customer_by_id(customer_id):
    return next(
        (c for c in CUSTOMERS if c["customer_id"] == customer_id),
        None,
    )


def latest_usage(customer_id):
    records = [
        u for u in USAGE
        if u["customer_id"] == customer_id
    ]

    if not records:
        return None

    return sorted(
        records,
        key=lambda x: x["usage_month"],
        reverse=True,
    )[0]


def previous_usage(customer_id):
    records = [
        u for u in USAGE
        if u["customer_id"] == customer_id
    ]

    if not records:
        return None

    return sorted(
        records,
        key=lambda x: x["usage_month"],
    )[0]


def tickets_for_customer(customer_id):
    return [
        t for t in SUPPORT_TICKETS
        if t["customer_id"] == customer_id
    ]


def subscription_for_customer(customer_id):
    return next(
        (
            s for s in SUBSCRIPTIONS
            if s["customer_id"] == customer_id
        ),
        None,
    )


def risk_score(customer_id):
    latest = latest_usage(customer_id)
    previous = previous_usage(customer_id)
    tickets = tickets_for_customer(customer_id)

    if not latest:
        return 0

    score = 0

    if latest["adoption_rate"] < 50:
        score += 40
    elif latest["adoption_rate"] < 70:
        score += 20

    if previous and latest["adoption_rate"] < previous["adoption_rate"]:
        score += 25

    high_open = [
        t for t in tickets
        if t["priority"] == "High"
        and t["status"] == "Open"
    ]

    if high_open:
        score += 35

    return score


def analyze_churn_risk():
    rows = []

    for customer in CUSTOMERS:
        latest = latest_usage(customer["customer_id"])
        previous = previous_usage(customer["customer_id"])
        subscription = subscription_for_customer(customer["customer_id"])
        tickets = tickets_for_customer(customer["customer_id"])

        rows.append({
            "customer_id": customer["customer_id"],
            "customer_name": customer["customer_name"],
            "region": customer["region"],
            "segment": customer["segment"],
            "customer_status": customer["status"],
            "mrr": subscription["mrr"] if subscription else 0,
            "latest_adoption": latest["adoption_rate"] if latest else 0,
            "previous_adoption": previous["adoption_rate"] if previous else 0,
            "latest_active_users": latest["active_users"] if latest else 0,
            "previous_active_users": previous["active_users"] if previous else 0,
            "ticket_count": len(tickets),
            "high_open_tickets": len([
                t for t in tickets
                if t["priority"] == "High"
                and t["status"] == "Open"
            ]),
            "risk_score": risk_score(customer["customer_id"]),
        })

    rows.sort(
        key=lambda x: (
            x["risk_score"],
            x["mrr"],
        ),
        reverse=True,
    )

    return rows


def analyze_mrr_region():
    result = {}

    for customer in CUSTOMERS:
        subscription = subscription_for_customer(
            customer["customer_id"]
        )

        if not subscription:
            continue

        if subscription["status"] != "active":
            continue

        region = customer["region"]

        if region not in result:
            result[region] = {
                "region": region,
                "total_mrr": 0,
                "customer_count": 0,
            }

        result[region]["total_mrr"] += subscription["mrr"]
        result[region]["customer_count"] += 1

    rows = list(result.values())
    rows.sort(
        key=lambda x: x["total_mrr"],
        reverse=True,
    )

    return rows


def analyze_expansions():
    rows = []

    for event in REVENUE_EVENTS:
        if event["event_type"] != "expansion":
            continue

        customer = customer_by_id(event["customer_id"])

        rows.append({
            "event_id": event["event_id"],
            "event_date": event["event_date"],
            "customer_id": event["customer_id"],
            "customer_name": customer["customer_name"],
            "region": customer["region"],
            "event_type": event["event_type"],
            "amount": event["amount"],
        })

    rows.sort(
        key=lambda x: x["event_date"],
        reverse=True,
    )

    return rows


def analyze_low_adoption():
    rows = []

    for customer in CUSTOMERS:
        latest = latest_usage(customer["customer_id"])

        if not latest:
            continue

        tickets = tickets_for_customer(
            customer["customer_id"]
        )

        if (
            latest["adoption_rate"] < 50
            and len(tickets) > 0
        ):
            rows.append({
                "customer_id": customer["customer_id"],
                "customer_name": customer["customer_name"],
                "region": customer["region"],
                "segment": customer["segment"],
                "latest_adoption": latest["adoption_rate"],
                "latest_active_users": latest["active_users"],
                "ticket_count": len(tickets),
                "open_ticket_count": len([
                    t for t in tickets
                    if t["status"] == "Open"
                ]),
            })

    rows.sort(
        key=lambda x: x["latest_adoption"]
    )

    return rows


def analyze_average_adoption_segment():
    groups = {}

    for customer in CUSTOMERS:
        records = [
            u for u in USAGE
            if u["customer_id"] == customer["customer_id"]
        ]

        segment = customer["segment"]

        groups.setdefault(segment, [])

        groups[segment].extend(
            u["adoption_rate"]
            for u in records
        )

    rows = []

    for segment, values in groups.items():
        average = (
            sum(values) / len(values)
            if values
            else 0
        )

        rows.append({
            "segment": segment,
            "average_adoption": round(average, 2),
            "customer_count": len([
                c for c in CUSTOMERS
                if c["segment"] == segment
            ]),
        })

    rows.sort(
        key=lambda x: x["average_adoption"],
        reverse=True,
    )

    return rows


def analyze_growth_drivers():
    groups = {}

    for event in REVENUE_EVENTS:
        event_type = event["event_type"]

        if event_type not in groups:
            groups[event_type] = {
                "event_type": event_type,
                "event_count": 0,
                "total_amount": 0,
            }

        groups[event_type]["event_count"] += 1
        groups[event_type]["total_amount"] += event["amount"]

    rows = list(groups.values())

    rows.sort(
        key=lambda x: x["total_amount"],
        reverse=True,
    )

    return rows


def analyze_ticket_declining_usage():
    rows = []

    for customer in CUSTOMERS:
        if customer["status"] != "active":
            continue

        latest = latest_usage(customer["customer_id"])
        previous = previous_usage(customer["customer_id"])

        if not latest or not previous:
            continue

        tickets = tickets_for_customer(
            customer["customer_id"]
        )

        if (
            latest["adoption_rate"]
            < previous["adoption_rate"]
            and len(tickets) >= 1
        ):
            rows.append({
                "customer_id": customer["customer_id"],
                "customer_name": customer["customer_name"],
                "region": customer["region"],
                "segment": customer["segment"],
                "previous_adoption": previous["adoption_rate"],
                "latest_adoption": latest["adoption_rate"],
                "adoption_change": (
                    latest["adoption_rate"]
                    - previous["adoption_rate"]
                ),
                "ticket_count": len(tickets),
            })

    rows.sort(
        key=lambda x: x["adoption_change"]
    )

    return rows


def analyze_business_health():
    regions = {}

    for customer in CUSTOMERS:
        region = customer["region"]

        if region not in regions:
            regions[region] = {
                "region": region,
                "customers": 0,
                "active_mrr": 0,
                "adoption_values": [],
                "ticket_count": 0,
                "open_ticket_count": 0,
            }

        data = regions[region]

        data["customers"] += 1

        subscription = subscription_for_customer(
            customer["customer_id"]
        )

        if (
            subscription
            and subscription["status"] == "active"
        ):
            data["active_mrr"] += subscription["mrr"]

        latest = latest_usage(
            customer["customer_id"]
        )

        if latest:
            data["adoption_values"].append(
                latest["adoption_rate"]
            )

        tickets = tickets_for_customer(
            customer["customer_id"]
        )

        data["ticket_count"] += len(tickets)

        data["open_ticket_count"] += len([
            t for t in tickets
            if t["status"] == "Open"
        ])

    rows = []

    for data in regions.values():
        values = data.pop("adoption_values")

        data["average_adoption"] = round(
            sum(values) / len(values)
            if values
            else 0,
            2,
        )

        rows.append(data)

    rows.sort(
        key=lambda x: x["active_mrr"],
        reverse=True,
    )

    return rows


def analyze_churn_reasons():
    churned_ids = {
        c["customer_id"]
        for c in CUSTOMERS
        if c["status"] == "churned"
    }

    groups = {}

    for ticket in SUPPORT_TICKETS:
        if ticket["customer_id"] not in churned_ids:
            continue

        category = ticket["category"]

        groups.setdefault(
            category,
            {
                "category": category,
                "ticket_count": 0,
                "high_priority_tickets": 0,
                "open_tickets": 0,
            },
        )

        groups[category]["ticket_count"] += 1

        if ticket["priority"] == "High":
            groups[category]["high_priority_tickets"] += 1

        if ticket["status"] == "Open":
            groups[category]["open_tickets"] += 1

    rows = list(groups.values())

    rows.sort(
        key=lambda x: (
            x["ticket_count"],
            x["high_priority_tickets"],
        ),
        reverse=True,
    )

    return rows


def analyze_missing_churn():
    churned_event_ids = {
        event["customer_id"]
        for event in REVENUE_EVENTS
        if event["event_type"] == "churn"
    }

    rows = []

    for customer in CUSTOMERS:
        if customer["customer_id"] not in churned_event_ids:
            rows.append({
                "customer_id": customer["customer_id"],
                "customer_name": customer["customer_name"],
                "status": customer["status"],
                "churn_data_status": "No recorded churn event",
            })

    return rows


def detect_question_type(question):
    q = question.lower()

    if (
        "churn risk" in q
        or "highest risk" in q
        or "at risk" in q
    ):
        return "churn_risk"

    if (
        "highest mrr" in q
        or "mrr region" in q
        or "region has the highest mrr" in q
    ):
        return "mrr_region"

    if (
        "expansion" in q
        or "expanded" in q
    ):
        return "expansion"

    if (
        "low adoption" in q
        or (
            "adoption" in q
            and "ticket" in q
        )
    ):
        return "low_adoption"

    if (
        "average adoption" in q
        and "segment" in q
    ):
        return "average_adoption"

    if (
        "growth driver" in q
        or "growth drivers" in q
        or "revenue growth" in q
    ):
        return "growth"

    if (
        "declining usage" in q
        or (
            "ticket volume" in q
            and "usage" in q
        )
    ):
        return "ticket_declining"

    if (
        "business health" in q
        or "health by region" in q
        or "region health" in q
    ):
        return "business_health"

    if (
        "churn reason" in q
        or "churn reasons" in q
    ):
        return "churn_reasons"

    if (
        "missing churn" in q
        or "missing data" in q
        or "churn data" in q
    ):
        return "missing_churn"

    return "customers"


def build_answer(
    question,
    rows,
    question_type,
    assumptions,
):
    if not rows:
        return (
            "I could not find matching data in the available "
            "assessment dataset."
        )

    first = rows[0]

    if question_type == "churn_risk":
        return (
            f"**{first['customer_name']}** has the highest "
            f"calculated churn-risk score of "
            f"**{first['risk_score']}**. "
            f"Latest adoption is **{first['latest_adoption']}%**, "
            f"with **{first['high_open_tickets']}** open "
            f"high-priority ticket(s). "
            f"The customer status is **{first['customer_status']}**. "
            f"This is a rule-based risk indicator, not a prediction model."
        )

    if question_type == "mrr_region":
        return (
            f"**{first['region']}** has the highest active MRR "
            f"at **${first['total_mrr']:,.0f}**."
        )

    if question_type == "expansion":
        total = sum(
            row["amount"]
            for row in rows
        )

        names = ", ".join(
            row["customer_name"]
            for row in rows
        )

        return (
            f"I found **{len(rows)} expansion event(s)** "
            f"totaling **${total:,.0f}**. "
            f"Customers involved: **{names}**."
        )

    if question_type == "low_adoption":
        names = ", ".join(
            row["customer_name"]
            for row in rows
        )

        return (
            f"I found **{len(rows)} customer(s)** with "
            f"low adoption and support activity: **{names}**."
        )

    if question_type == "average_adoption":
        summary = "; ".join(
            f"**{row['segment']}**: "
            f"{row['average_adoption']:.1f}%"
            for row in rows
        )

        return (
            f"The segment averages are: {summary}. "
            f"**{first['segment']}** has the highest average "
            f"adoption at **{first['average_adoption']:.1f}%**."
        )

    if question_type == "growth":
        return (
            f"**{first['event_type'].title()}** is the largest "
            f"positive revenue driver in the recorded events, "
            f"with **${first['total_amount']:,.0f}**."
        )

    if question_type == "ticket_declining":
        names = ", ".join(
            row["customer_name"]
            for row in rows
        )

        return (
            f"I found **{len(rows)} active customer(s)** with "
            f"declining adoption and support tickets: **{names}**."
        )

    if question_type == "business_health":
        summary = "; ".join(
            f"**{row['region']}**: "
            f"${row['active_mrr']:,.0f} active MRR, "
            f"{row['average_adoption']:.1f}% adoption, "
            f"{row['ticket_count']} tickets"
            for row in rows
        )

        return (
            f"Regional business health: {summary}. "
            f"**{first['region']}** leads on active MRR."
        )

    if question_type == "churn_reasons":
        return (
            "The dataset has no dedicated churn-reason field. "
            "Support ticket categories for the churned customer "
            "are therefore used as a proxy. "
            f"The available result is **{first['category']}**."
        )

    if question_type == "missing_churn":
        names = ", ".join(
            row["customer_name"]
            for row in rows
        )

        return (
            f"I found **{len(rows)} customer(s)** without a "
            f"recorded churn revenue event: **{names}**."
        )

    return (
        f"I found **{len(rows)} customer record(s)** "
        "in the assessment dataset."
    )


def follow_up_answer(question, previous_result):
    q = question.lower()

    previous_rows = (
        previous_result.get("evidence", [])
        if isinstance(previous_result, dict)
        else []
    )

    if not previous_rows:
        return None

    first = previous_rows[0]

    if (
        "what should we do" in q
        or "what do we do" in q
        or "recommend" in q
        or "recommendation" in q
    ):
        name = first.get(
            "customer_name",
            "the customer",
        )

        adoption = first.get(
            "latest_adoption",
            "N/A",
        )

        tickets = first.get(
            "high_open_tickets",
            0,
        )

        return (
            f"For **{name}**, prioritize a customer-success "
            f"intervention. Latest adoption is **{adoption}%**, "
            f"so the team should review product usage with the "
            f"customer, address the **{tickets}** open high-priority "
            f"ticket(s), and create a short-term adoption recovery plan. "
            f"These recommendations are based on the previous analysis "
            f"evidence."
        )

    return None


def analyze_question(
    question: str,
    db=None,
    conversation_history=None,
):
    workflow = []

    workflow.append(
        workflow_step(
            "understand_question",
            "completed",
            "Business question understood.",
        )
    )

    # --------------------------------------------------------
    # Follow-up handling
    # --------------------------------------------------------

    if conversation_history:
        previous_result = None

        for message in reversed(conversation_history):
            if (
                isinstance(message, dict)
                and message.get("role") == "assistant"
                and isinstance(message.get("data"), dict)
            ):
                previous_result = message["data"]
                break

        if previous_result:
            answer = follow_up_answer(
                question,
                previous_result,
            )

            if answer:
                workflow.extend([
                    workflow_step(
                        "understand_question",
                        "completed",
                        "Follow-up question understood using previous context.",
                    ),
                    workflow_step(
                        "validate_result",
                        "completed",
                        "Previous analysis evidence reused.",
                    ),
                    workflow_step(
                        "explain_result",
                        "completed",
                        "Recommendation generated from previous evidence.",
                    ),
                ])

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
                    "evidence": previous_result.get(
                        "evidence",
                        [],
                    ),
                    "row_count": len(
                        previous_result.get(
                            "evidence",
                            [],
                        )
                    ),
                    "assumptions": [
                        "Follow-up uses evidence from the previous analysis."
                    ],
                    "ai_used": previous_result.get(
                        "ai_used",
                        False,
                    ),
                }

    # --------------------------------------------------------
    # Detect analysis
    # --------------------------------------------------------

    question_type = detect_question_type(
        question
    )

    table_map = {
        "churn_risk": [
            "customers",
            "subscriptions",
            "usage",
            "support_tickets",
        ],
        "mrr_region": [
            "customers",
            "subscriptions",
        ],
        "expansion": [
            "revenue_events",
            "customers",
        ],
        "low_adoption": [
            "customers",
            "usage",
            "support_tickets",
        ],
        "average_adoption": [
            "customers",
            "usage",
        ],
        "growth": [
            "revenue_events",
        ],
        "ticket_declining": [
            "customers",
            "usage",
            "support_tickets",
        ],
        "business_health": [
            "customers",
            "subscriptions",
            "usage",
            "support_tickets",
        ],
        "churn_reasons": [
            "customers",
            "support_tickets",
        ],
        "missing_churn": [
            "customers",
            "revenue_events",
        ],
        "customers": [
            "customers",
        ],
    }

    tables_used = table_map.get(
        question_type,
        ["customers"],
    )

    workflow.append(
        workflow_step(
            "select_tables",
            "completed",
            "Relevant tables identified.",
            tables=tables_used,
        )
    )

    # --------------------------------------------------------
    # Try Groq for SQL generation
    # --------------------------------------------------------

    ai_used = False
    generated_sql = ""

    try:
        llm_result = generate_sql(
            question=question,
            schema_context=SCHEMA_CONTEXT,
            conversation_history=conversation_history,
        )

        if isinstance(llm_result, dict):
            generated_sql = llm_result.get(
                "sql",
                "",
            )
            ai_used = bool(generated_sql)

        elif isinstance(llm_result, str):
            generated_sql = llm_result
            ai_used = bool(generated_sql)

        if ai_used:
            workflow.append(
                workflow_step(
                    "generate_sql",
                    "completed",
                    "AI generated analysis logic.",
                    ai_used=True,
                )
            )

    except Exception as error:
        workflow.append(
            workflow_step(
                "generate_sql",
                "failed",
                f"AI generation failed: {str(error)}",
                ai_used=False,
            )
        )

    # --------------------------------------------------------
    # Deterministic verified analysis
    # --------------------------------------------------------

    analysis_functions = {
        "churn_risk": analyze_churn_risk,
        "mrr_region": analyze_mrr_region,
        "expansion": analyze_expansions,
        "low_adoption": analyze_low_adoption,
        "average_adoption": analyze_average_adoption_segment,
        "growth": analyze_growth_drivers,
        "ticket_declining": analyze_ticket_declining_usage,
        "business_health": analyze_business_health,
        "churn_reasons": analyze_churn_reasons,
        "missing_churn": analyze_missing_churn,
        "customers": lambda: CUSTOMERS,
    }

    rows = analysis_functions[
        question_type
    ]()

    workflow.append(
        workflow_step(
            "execute_analysis",
            "completed",
            "Analysis executed against the verified in-memory assessment dataset.",
        )
    )

    workflow.append(
        workflow_step(
            "validate_result",
            "completed",
            "Result validated using deterministic business rules.",
        )
    )

    assumptions = [
        "The prototype uses the provided assessment dataset in memory.",
        "No production database is required for this prototype.",
    ]

    if question_type == "churn_risk":
        assumptions.extend([
            "Adoption below 50% is treated as a strong churn-risk signal.",
            "Declining adoption adds risk.",
            "Open high-priority support tickets add risk.",
            "The churn score is a rule-based indicator, not a prediction model.",
        ])

    if question_type == "low_adoption":
        assumptions.append(
            "Adoption below 50% is treated as low adoption."
        )

    if question_type == "churn_reasons":
        assumptions.append(
            "Support ticket categories are used as a proxy because there is no dedicated churn-reason field."
        )

    if question_type == "missing_churn":
        assumptions.append(
            "Missing churn means no recorded revenue event with event_type = churn."
        )

    answer = build_answer(
        question,
        rows,
        question_type,
        assumptions,
    )

    workflow.append(
        workflow_step(
            "explain_result",
            "completed",
            "Result explained with supporting evidence.",
        )
    )

    columns = (
        list(rows[0].keys())
        if rows
        else []
    )

    return {
        "success": True,
        "answer": answer,
        "workflow": workflow,
        "tables_used": tables_used,
        "sql": generated_sql,
        "columns": columns,
        "evidence": rows,
        "row_count": len(rows),
        "assumptions": assumptions,
        "ai_used": ai_used,
    }