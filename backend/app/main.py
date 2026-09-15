from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app import models

from app.routes.tables import router as tables_router
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router


app = FastAPI(
    title="Zscaler AI Data Analyst",
    description="AI-powered multi-table business data analyst",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(tables_router)
app.include_router(chat_router)
app.include_router(conversations_router)


@app.get("/")
def root():
    return {
        "message": "Zscaler AI Data Analyst API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }