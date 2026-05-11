"""
app/main.py

FastAPI application factory.
Registers all routes and configures the server object.
"""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agent.orchestrator import BankingOrchestrator
from app.core.schemas import AgentResponse, CustomerRequest
from app.core.settings import settings

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Banking AI-Agents API",
    description=(
        "An agentic pipeline for banking customer support. "
        "Processes customer messages through intent detection, priority "
        "classification, policy retrieval, LLM-based response drafting, "
        "validation, and escalation routing."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Singleton orchestrator (shared across requests) ───────────────────────────
orchestrator = BankingOrchestrator()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health check / welcome endpoint."""
    return {
        "status": "ok",
        "service": "Banking AI-Agents",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    """Detailed health check."""
    from app.clients.ollama_client import OllamaClient
    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.llm_model,
    )
    ollama_ok = client.health_check()
    return {
        "status": "ok",
        "ollama_reachable": ollama_ok,
        "ollama_url": settings.ollama_base_url,
        "llm_model": settings.llm_model,
    }


@app.post("/process", response_model=AgentResponse, tags=["Pipeline"])
def process_request(request: CustomerRequest) -> AgentResponse:
    """
    Process a customer support message through the complete agentic pipeline.

    Returns the detected intent, priority, policy snippet, draft reply,
    validation result, routing action, final reply, and full workflow trace.
    """
    logger.info(
        "POST /process  customer_id=%s  message_len=%d",
        request.customer_id,
        len(request.message),
    )
    try:
        response = orchestrator.run(request)
        return response
    except Exception as exc:
        logger.exception("Unhandled error in pipeline: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/intents", tags=["Info"])
def list_intents():
    """List all supported intent labels and their policy titles."""
    from app.data.policies import POLICIES
    return {
        "supported_intents": [
            {"intent": k, "policy_title": v["title"]} for k, v in POLICIES.items()
        ]
    }
