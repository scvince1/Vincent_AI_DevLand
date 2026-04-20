"""
FastAPI application factory.

Registers all routers, configures CORS for the frontend dev server,
and exposes a health check endpoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import alerts, mentions, overview, platforms, products, simulate, topics

app = FastAPI(
    title="SharkNinja Consumer Sentiment Dashboard",
    description=(
        "Consumer-electronics-aware NLP pipeline for social listening. "
        "Handles sarcasm, comparative sentiment, ABSA, and CE domain terminology."
    ),
    version="1.0.0",
)

# CORS — allow the Vite frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(mentions.router)
app.include_router(overview.router)
app.include_router(products.router)
app.include_router(platforms.router)
app.include_router(topics.router)
app.include_router(alerts.router)
app.include_router(simulate.router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Smoke-test endpoint."""
    return {"status": "ok"}
