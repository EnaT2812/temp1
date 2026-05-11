"""
run.py

Entry point for the Banking AI-Agents FastAPI server.
Starts Uvicorn with settings sourced from app/core/settings.py.

Usage:
    python run.py
"""

import uvicorn
from app.core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
