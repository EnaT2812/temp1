"""
app/agent/orchestrator.py

Main workflow controller — ties all nodes together into the complete
Banking AI-Agents pipeline.

Execution order
---------------
1. Intent Detection      (IntentNode)
2. Priority Detection    (PriorityNode)
3. Policy Retrieval      (PolicyNode)
4. Response Drafting     (DraftNode)      ← calls Ollama LLM
5. Validation            (ValidationNode)
6. Routing / Escalation  (RouterNode)

The orchestrator also collects a full workflow *trace* (list of
TraceEntry objects) so that callers can observe each intermediate result.
"""

import logging
import time
from typing import Optional

from app.core.schemas import (
    AgentResponse,
    CustomerRequest,
    TraceEntry,
)
from app.nodes.draft_node import DraftNode
from app.nodes.intent_node import IntentNode
from app.nodes.policy_node import PolicyNode
from app.nodes.priority_node import PriorityNode
from app.nodes.router_node import RouterNode
from app.nodes.validation_node import ValidationNode

logger = logging.getLogger(__name__)


class BankingOrchestrator:
    """
    Orchestrates the complete banking customer-support agentic pipeline.

    Each node is instantiated once at orchestrator creation time for
    efficiency (shared state / model loading).
    """

    def __init__(self) -> None:
        logger.info("Initialising BankingOrchestrator…")
        self.intent_node = IntentNode()
        self.priority_node = PriorityNode()
        self.policy_node = PolicyNode()
        self.draft_node = DraftNode()
        self.validation_node = ValidationNode()
        self.router_node = RouterNode()
        logger.info("BankingOrchestrator ready.")

    # ── Public method ─────────────────────────────────────────────────────────

    def run(self, request: CustomerRequest) -> AgentResponse:
        """
        Process a customer support request through the full pipeline.

        Parameters
        ----------
        request : CustomerRequest
            The incoming customer message (+ optional metadata).

        Returns
        -------
        AgentResponse
            Complete pipeline result including the final reply and trace.
        """
        start = time.perf_counter()
        trace: list[TraceEntry] = []

        customer_id = request.customer_id
        message = request.message.strip()

        logger.info(
            "--- Pipeline START | customer_id=%s | channel=%s ---",
            customer_id,
            request.channel,
        )

        # ── Step 1: Intent Detection ──────────────────────────────────────────
        logger.info("[1/6] IntentNode")
        intent_result = self.intent_node.run(message)
        trace.append(TraceEntry(node="intent_detection", output=intent_result.model_dump()))
        logger.info(
            "  → intent='%s'  confidence=%.2f",
            intent_result.intent,
            intent_result.confidence,
        )

        # ── Step 2: Priority Detection ────────────────────────────────────────
        logger.info("[2/6] PriorityNode")
        priority_result = self.priority_node.run(message, intent_result.intent)
        trace.append(TraceEntry(node="priority_detection", output=priority_result.model_dump()))
        logger.info("  → priority='%s'", priority_result.priority.value)

        # ── Step 3: Policy Retrieval ──────────────────────────────────────────
        logger.info("[3/6] PolicyNode")
        policy_result = self.policy_node.run(intent_result.intent)
        trace.append(TraceEntry(node="policy_retrieval", output=policy_result.model_dump()))
        logger.info("  → policy='%s'", policy_result.policy_title)

        # ── Step 4: Response Drafting ─────────────────────────────────────────
        logger.info("[4/6] DraftNode")
        draft_result = self.draft_node.run(
            message=message,
            intent=intent_result.intent,
            priority=priority_result.priority,
            policy_title=policy_result.policy_title,
            policy_body=policy_result.policy_body,
        )
        trace.append(TraceEntry(node="response_drafting", output=draft_result.model_dump()))
        logger.info(
            "  → draft len=%d, missing=%s",
            len(draft_result.draft_reply),
            draft_result.missing_info,
        )

        # ── Step 5: Validation ────────────────────────────────────────────────
        logger.info("[5/6] ValidationNode")
        validation_result = self.validation_node.run(
            draft=draft_result.draft_reply,
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            priority=priority_result.priority,
            missing_info=draft_result.missing_info,
        )
        trace.append(TraceEntry(node="validation", output=validation_result.model_dump()))
        logger.info(
            "  → passed=%s, issues=%s",
            validation_result.passed,
            validation_result.issues,
        )

        # ── Step 6: Routing ───────────────────────────────────────────────────
        logger.info("[6/6] RouterNode")
        router_result = self.router_node.run(
            draft_reply=draft_result.draft_reply,
            validation=validation_result,
            priority=priority_result.priority,
            missing_info=draft_result.missing_info,
        )
        trace.append(TraceEntry(node="routing", output=router_result.model_dump()))
        logger.info("  → action='%s'", router_result.action.value)

        elapsed = time.perf_counter() - start
        logger.info(
            "--- Pipeline END | elapsed=%.2fs | action=%s ---",
            elapsed,
            router_result.action.value,
        )

        # ── Assemble final response ───────────────────────────────────────────
        return AgentResponse(
            customer_id=customer_id,
            intent=intent_result.intent,
            priority=priority_result.priority,
            policy_snippet=f"[{policy_result.policy_title}] {policy_result.policy_body[:200]}…",
            draft_reply=draft_result.draft_reply,
            validation_passed=validation_result.passed,
            routing_action=router_result.action,
            final_reply=router_result.final_reply,
            trace=trace,
        )
