from fastapi import APIRouter


router = APIRouter(
    prefix="/api/tables",
    tags=["Tables"],
)


TABLE_SCHEMAS = {
    "customers": {
        "description": "Customer and company information",
        "columns": [
            "customer_id",
            "customer_name",
            "region",
            "segment",
            "industry",
            "status",
            "created_at",
        ],
    },
    "subscriptions": {
        "description": "Customer subscription and MRR information",
        "columns": [
            "subscription_id",
            "customer_id",
            "plan",
            "mrr",
            "start_date",
            "end_date",
            "status",
        ],
    },
    "usage": {
        "description": "Monthly product usage and feature adoption",
        "columns": [
            "usage_id",
            "customer_id",
            "usage_month",
            "active_users",
            "licensed_users",
            "adoption_rate",
        ],
    },
    "support_tickets": {
        "description": "Customer support tickets and issues",
        "columns": [
            "ticket_id",
            "customer_id",
            "created_at",
            "category",
            "priority",
            "status",
        ],
    },
    "revenue_events": {
        "description": "Revenue changes and revenue events",
        "columns": [
            "event_id",
            "customer_id",
            "event_date",
            "event_type",
            "amount",
        ],
    },
}


@router.get("")
def list_tables():
    return {
        "success": True,
        "tables": [
            {
                "name": name,
                **details,
            }
            for name, details in TABLE_SCHEMAS.items()
        ],
    }


@router.get("/{table_name}")
def describe_table(table_name: str):

    table_name = table_name.lower()

    if table_name not in TABLE_SCHEMAS:
        return {
            "success": False,
            "error": f"Table '{table_name}' does not exist.",
        }

    return {
        "success": True,
        "table": table_name,
        **TABLE_SCHEMAS[table_name],
    }