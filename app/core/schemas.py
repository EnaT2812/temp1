"""
app/core/schemas.py

Pydantic schemas for all request/response objects and intermediate node outputs.
Keeping them in one place ensures a consistent contract across the entire pipeline.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


# ── Enumerations ──────────────────────────────────────────────────────────────


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RoutingAction(str, Enum):
    SEND_REPLY = "send_reply"
    ASK_MORE_INFO = "ask_more_info"
    ESCALATE = "escalate"


# ── Top-level API schemas ──────────────────────────────────────────────────────


class CustomerRequest(BaseModel):
    """Input schema for a single customer support request."""

    message: str = Field(..., description="The raw customer message.")
    customer_id: Optional[str] = Field(
        default=None, description="Optional customer identifier for logging."
    )
    channel: Optional[str] = Field(
        default="api",
        description="Channel the request came from (e.g. 'web', 'mobile', 'api').",
    )


class AgentResponse(BaseModel):
    """Top-level API response returned to the caller."""

    customer_id: Optional[str] = None
    intent: str
    priority: Priority
    policy_snippet: str
    draft_reply: str
    validation_passed: bool
    routing_action: RoutingAction
    final_reply: str
    trace: List[TraceEntry]


# ── Per-node result schemas ────────────────────────────────────────────────────


class IntentResult(BaseModel):
    """Output of the Intent Detection Node."""

    intent: str = Field(..., description="Detected banking intent label.")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the predicted intent (0-1).",
    )
    raw_scores: Optional[dict[str, float]] = Field(
        default=None,
        description="Full label→score mapping if available.",
    )


class PriorityResult(BaseModel):
    """Output of the Priority/Risk Detection Node."""

    priority: Priority
    reason: str = Field(..., description="Short human-readable reason for the priority level.")
    triggered_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords that triggered the priority classification.",
    )


class PolicyResult(BaseModel):
    """Output of the Policy Retrieval Node."""

    intent: str
    policy_title: str
    policy_body: str
    source: str = Field(default="policies.py", description="Where the policy came from.")


class DraftResult(BaseModel):
    """Output of the Response Drafting Node."""

    draft_reply: str
    missing_info: List[str] = Field(
        default_factory=list,
        description="List of missing pieces of information that could improve the response.",
    )
    suggested_next_action: str = Field(
        default="validate",
        description="Next step recommended by the drafting node.",
    )


class ValidationResult(BaseModel):
    """Output of the Validation Node."""

    passed: bool
    issues: List[str] = Field(
        default_factory=list,
        description="List of validation issues found (empty when passed=True).",
    )
    confidence_ok: bool = Field(
        default=True,
        description="Whether the intent confidence meets the threshold.",
    )
    length_ok: bool = Field(
        default=True,
        description="Whether the draft reply has sufficient length.",
    )


class RouterResult(BaseModel):
    """Output of the Routing/Escalation Node."""

    action: RoutingAction
    reason: str
    final_reply: str


# ── Trace ─────────────────────────────────────────────────────────────────────


class TraceEntry(BaseModel):
    """A single step in the workflow trace."""

    node: str
    output: Any


# Allow forward-reference resolution
AgentResponse.model_rebuild()
