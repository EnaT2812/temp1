"""
app/nodes/router_node.py

Routing / Escalation Node — the final decision node of the workflow.

Based on the accumulated outputs of all previous nodes, decides one of three
routing actions:

  ESCALATE        – transfer to a human agent
  ASK_MORE_INFO   – send a clarifying question to the customer
  SEND_REPLY      – deliver the draft reply directly

Decision logic (evaluated in order):
  1. Validation failed with a confidence or banned-phrase issue → ESCALATE
  2. Priority is HIGH → ESCALATE
  3. Missing required information → ASK_MORE_INFO
  4. Draft reply is too short → ESCALATE (cannot send a bad reply)
  5. Validation passed → SEND_REPLY
"""

import logging
from typing import List

from app.core.schemas import Priority, RouterResult, RoutingAction, ValidationResult

logger = logging.getLogger(__name__)

# ── Clarifying-question templates ─────────────────────────────────────────────
_MISSING_INFO_TEMPLATE = (
    "Thank you for contacting us. To assist you more effectively, "
    "could you please provide the following information?\n\n"
    "{items}\n\n"
    "Once we have this information, we will be able to resolve your "
    "issue as quickly as possible."
)

_ESCALATION_NOTICE = (
    "Thank you for reaching out. Your case has been escalated to a "
    "dedicated support specialist who will contact you within {sla}. "
    "We apologise for any inconvenience and appreciate your patience."
)

SLA_BY_PRIORITY = {
    Priority.HIGH: "1 business hour",
    Priority.MEDIUM: "4 business hours",
    Priority.LOW: "1 business day",
}


class RouterNode:
    """
    Final routing node that decides the action and builds the final reply.
    """

    def run(
        self,
        draft_reply: str,
        validation: ValidationResult,
        priority: Priority,
        missing_info: List[str],
    ) -> RouterResult:
        """
        Determine the routing action and compose the final customer-facing reply.

        Parameters
        ----------
        draft_reply : str        – draft from DraftNode
        validation : ValidationResult – output from ValidationNode
        priority : Priority      – case priority level
        missing_info : list      – missing info list from DraftNode

        Returns
        -------
        RouterResult
            Routing action, reason, and final reply text.
        """
        logger.info("RouterNode: deciding action. priority=%s, passed=%s", priority, validation.passed)

        # Rule 1 – critical validation failure → escalate
        if not validation.confidence_ok:
            reason = "Intent confidence too low; escalating to avoid incorrect information."
            return RouterResult(
                action=RoutingAction.ESCALATE,
                reason=reason,
                final_reply=_ESCALATION_NOTICE.format(sla=SLA_BY_PRIORITY[priority]),
            )

        # Rule 2 – high priority → always escalate
        if priority == Priority.HIGH:
            reason = "HIGH priority case; routing to human specialist per escalation policy."
            return RouterResult(
                action=RoutingAction.ESCALATE,
                reason=reason,
                final_reply=_ESCALATION_NOTICE.format(sla=SLA_BY_PRIORITY[priority]),
            )

        # Rule 3 – missing required info → ask customer
        if missing_info:
            items_text = "\n".join(f"  • {item}" for item in missing_info)
            reason = f"Required information missing: {missing_info}. Asking customer."
            return RouterResult(
                action=RoutingAction.ASK_MORE_INFO,
                reason=reason,
                final_reply=_MISSING_INFO_TEMPLATE.format(items=items_text),
            )

        # Rule 4 – draft too short despite passing other checks → escalate
        if not validation.length_ok:
            reason = "Draft reply too short; escalating to avoid incomplete response."
            return RouterResult(
                action=RoutingAction.ESCALATE,
                reason=reason,
                final_reply=_ESCALATION_NOTICE.format(sla=SLA_BY_PRIORITY[priority]),
            )

        # Rule 5 – all checks passed → send the draft
        reason = "Validation passed; sending auto-generated reply to customer."
        logger.info("RouterNode: SEND_REPLY")
        return RouterResult(
            action=RoutingAction.SEND_REPLY,
            reason=reason,
            final_reply=draft_reply,
        )
