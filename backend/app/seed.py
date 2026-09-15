from datetime import date, datetime
from decimal import Decimal

from app.database import Base, SessionLocal, engine
from app.models import (
    Customer,
    Subscription,
    Usage,
    SupportTicket,
    RevenueEvent,
)


def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Prevent duplicate seed data
        if db.query(Customer).first():
            print("Database already contains data.")
            return

        # -------------------------
        # CUSTOMERS
        # -------------------------
        customers = [
            Customer(
                customer_id="C001",
                customer_name="Acme Corp",
                region="North America",
                segment="Enterprise",
                industry="Technology",
                status="active",
                created_at=date(2023, 1, 15),
            ),
            Customer(
                customer_id="C002",
                customer_name="NovaTech",
                region="EMEA",
                segment="Mid-Market",
                industry="Technology",
                status="active",
                created_at=date(2023, 3, 22),
            ),
            Customer(
                customer_id="C003",
                customer_name="BluePeak",
                region="APAC",
                segment="SMB",
                industry="Technology",
                status="churned",
                created_at=date(2023, 5, 10),
            ),
            Customer(
                customer_id="C004",
                customer_name="GreenLeaf",
                region="North America",
                segment="Enterprise",
                industry="Technology",
                status="active",
                created_at=date(2023, 6, 18),
            ),
            Customer(
                customer_id="C005",
                customer_name="OrbitAI",
                region="APAC",
                segment="Mid-Market",
                industry="Technology",
                status="active",
                created_at=date(2023, 9, 1),
            ),
        ]

        db.add_all(customers)

        # -------------------------
        # SUBSCRIPTIONS
        # -------------------------
        subscriptions = [
            Subscription(
                subscription_id="S001",
                customer_id="C001",
                plan="Enterprise",
                mrr=Decimal("12000"),
                start_date=date(2023, 1, 15),
                end_date=None,
                status="active",
            ),
            Subscription(
                subscription_id="S002",
                customer_id="C002",
                plan="Growth",
                mrr=Decimal("4500"),
                start_date=date(2023, 3, 22),
                end_date=None,
                status="active",
            ),
            Subscription(
                subscription_id="S003",
                customer_id="C003",
                plan="Starter",
                mrr=Decimal("900"),
                start_date=date(2023, 5, 10),
                end_date=None,
                status="churned",
            ),
            Subscription(
                subscription_id="S004",
                customer_id="C004",
                plan="Enterprise",
                mrr=Decimal("15000"),
                start_date=date(2023, 6, 18),
                end_date=None,
                status="active",
            ),
            Subscription(
                subscription_id="S005",
                customer_id="C005",
                plan="Growth",
                mrr=Decimal("5200"),
                start_date=date(2023, 9, 1),
                end_date=None,
                status="active",
            ),
        ]

        db.add_all(subscriptions)

        # -------------------------
        # USAGE
        # -------------------------
        usage_records = [
            Usage(
                usage_id="U001",
                customer_id="C001",
                usage_month=date(2024, 1, 1),
                active_users=120,
                licensed_users=0,
                adoption_rate=Decimal("82"),
            ),
            Usage(
                usage_id="U002",
                customer_id="C001",
                usage_month=date(2024, 2, 1),
                active_users=118,
                licensed_users=0,
                adoption_rate=Decimal("80"),
            ),
            Usage(
                usage_id="U003",
                customer_id="C002",
                usage_month=date(2024, 1, 1),
                active_users=75,
                licensed_users=0,
                adoption_rate=Decimal("61"),
            ),
            Usage(
                usage_id="U004",
                customer_id="C002",
                usage_month=date(2024, 2, 1),
                active_users=60,
                licensed_users=0,
                adoption_rate=Decimal("52"),
            ),
            Usage(
                usage_id="U005",
                customer_id="C003",
                usage_month=date(2024, 1, 1),
                active_users=25,
                licensed_users=0,
                adoption_rate=Decimal("35"),
            ),
            Usage(
                usage_id="U006",
                customer_id="C003",
                usage_month=date(2024, 2, 1),
                active_users=10,
                licensed_users=0,
                adoption_rate=Decimal("20"),
            ),
            Usage(
                usage_id="U007",
                customer_id="C004",
                usage_month=date(2024, 1, 1),
                active_users=150,
                licensed_users=0,
                adoption_rate=Decimal("88"),
            ),
            Usage(
                usage_id="U008",
                customer_id="C004",
                usage_month=date(2024, 2, 1),
                active_users=165,
                licensed_users=0,
                adoption_rate=Decimal("91"),
            ),
            Usage(
                usage_id="U009",
                customer_id="C005",
                usage_month=date(2024, 1, 1),
                active_users=80,
                licensed_users=0,
                adoption_rate=Decimal("67"),
            ),
            Usage(
                usage_id="U010",
                customer_id="C005",
                usage_month=date(2024, 2, 1),
                active_users=76,
                licensed_users=0,
                adoption_rate=Decimal("60"),
            ),
        ]

        db.add_all(usage_records)

        # -------------------------
        # SUPPORT TICKETS
        # -------------------------
        tickets = [
            SupportTicket(
                ticket_id="T001",
                customer_id="C001",
                created_at=datetime(2024, 2, 1),
                category="Billing",
                priority="Medium",
                status="Closed",
            ),
            SupportTicket(
                ticket_id="T002",
                customer_id="C003",
                created_at=datetime(2024, 2, 10),
                category="Reliability",
                priority="High",
                status="Open",
            ),
            SupportTicket(
                ticket_id="T003",
                customer_id="C002",
                created_at=datetime(2024, 2, 12),
                category="Onboarding",
                priority="Medium",
                status="Open",
            ),
            SupportTicket(
                ticket_id="T004",
                customer_id="C005",
                created_at=datetime(2024, 2, 15),
                category="Product Bug",
                priority="High",
                status="Open",
            ),
            SupportTicket(
                ticket_id="T005",
                customer_id="C004",
                created_at=datetime(2024, 2, 20),
                category="Question",
                priority="Low",
                status="Closed",
            ),
        ]

        db.add_all(tickets)

        # -------------------------
        # REVENUE EVENTS
        # -------------------------
        revenue_events = [
            RevenueEvent(
                event_id="R001",
                customer_id="C001",
                event_date=date(2024, 1, 1),
                event_type="new",
                amount=Decimal("12000"),
            ),
            RevenueEvent(
                event_id="R002",
                customer_id="C002",
                event_date=date(2024, 3, 1),
                event_type="expansion",
                amount=Decimal("1500"),
            ),
            RevenueEvent(
                event_id="R003",
                customer_id="C003",
                event_date=date(2024, 4, 1),
                event_type="churn",
                amount=Decimal("-900"),
            ),
            RevenueEvent(
                event_id="R004",
                customer_id="C004",
                event_date=date(2024, 2, 1),
                event_type="expansion",
                amount=Decimal("3000"),
            ),
            RevenueEvent(
                event_id="R005",
                customer_id="C005",
                event_date=date(2024, 3, 15),
                event_type="contraction",
                amount=Decimal("-700"),
            ),
        ]

        db.add_all(revenue_events)

        db.commit()

        print("✅ Database seeded successfully!")
        print("✅ 5 customers")
        print("✅ 5 subscriptions")
        print("✅ 10 usage records")
        print("✅ 5 support tickets")
        print("✅ 5 revenue events")

    except Exception as e:
        db.rollback()
        print("❌ Error while seeding database:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()