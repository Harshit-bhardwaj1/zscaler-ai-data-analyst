from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router


app = FastAPI(
    title="AI Data Analyst",
    description="Zscaler AI Product Builder Assessment Prototype",
    version="1.0.0",
)


# Allow the deployed Vercel frontend and local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "AI Data Analyst API is running",
        "status": "healthy",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/api/tables")
def get_tables():
    return {
        "tables": [
            {
                "name": "customers",
                "description": "Customer accounts and segmentation.",
            },
            {
                "name": "subscriptions",
                "description": "Subscription plans and MRR.",
            },
            {
                "name": "usage",
                "description": "Product usage and adoption metrics.",
            },
            {
                "name": "support_tickets",
                "description": "Customer support activity.",
            },
            {
                "name": "revenue_events",
                "description": "New, expansion, contraction and churn events.",
            },
        ]
    }