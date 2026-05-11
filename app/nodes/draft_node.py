"""
app/nodes/draft_node.py

Response Drafting Node.

Calls the Ollama LLM (gpt-oss:20b) to compose a customer-facing draft
reply that is:
  - Grounded in the retrieved policy snippet.
  - Appropriately toned for the detected priority level.
  - Concise and professional.

If Ollama is unreachable the node degrades gracefully to a template-based
fallback so that the rest of the pipeline can still produce a response.
"""

import logging
from typing import List

from app.clients.ollama_client import OllamaClient
from app.core.schemas import DraftResult, Priority
from app.core.settings import settings

logger = logging.getLogger(__name__)

# ── Shared Ollama client (created once at import time) ────────────────────────
_ollama = OllamaClient(
    base_url=settings.ollama_base_url,
    model=settings.llm_model,
    timeout=settings.llm_timeout,
)

# ── Prompt templates ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a professional and empathetic banking customer support assistant. "
    "Your replies must be:\n"
    "- Polite, concise, and in English.\n"
    "- Grounded strictly in the provided policy information — do NOT invent facts.\n"
    "- Appropriately urgent when the priority is HIGH.\n"
    "- Structured: start with empathy, then action steps, then a closing.\n"
    "Keep the response under 200 words."
)

USER_PROMPT_TEMPLATE = """Customer message:
\"\"\"{message}\"\"\"

Detected intent: {intent}
Priority level: {priority}

Relevant policy:
\"\"\"{policy}\"\"\"

Please draft a reply to the customer addressing their concern.
If any critical information is missing from their message that you need
to help them (e.g. transaction ID, account number), mention it politely.
"""


class DraftNode:
    """
    Generates a draft customer reply using the Ollama LLM.

    Falls back to a deterministic template when Ollama is unreachable.
    """

    def _build_prompt(
        self,
        message: str,
        intent: str,
        priority: Priority,
        policy_body: str,
    ) -> str:
        return USER_PROMPT_TEMPLATE.format(
            message=message,
            intent=intent,
            priority=priority.value,
            policy=policy_body,
        )

    def _template_fallback(
        self,
        message: str,
        intent: str,
        priority: Priority,
        policy_title: str,
        policy_body: str,
    ) -> str:
        """Simple template-based reply when LLM is unavailable."""
        urgency = (
            "We understand this is an urgent matter and will prioritise it. "
            if priority == Priority.HIGH
            else ""
        )
        return (
            f"Thank you for reaching out to us.\n\n"
            f"{urgency}"
            f"We have received your inquiry regarding **{intent.replace('_', ' ').title()}**.\n\n"
            f"According to our policy on '{policy_title}':\n"
            f"{policy_body[:300]}...\n\n"
            "Please contact our 24/7 support line or visit a branch for further assistance. "
            "We apologise for any inconvenience caused."
        )

    def _detect_missing_info(self, message: str, intent: str) -> List[str]:
        """
        Heuristic: flag commonly required pieces of information that are
        absent from the customer message.
        """
        missing: List[str] = []
        text = message.lower()

        needs_txn_id = intent in {
            "transfer_failure", "wrong_transfer", "refund_request",
            "bill_payment_issue", "deposit_issue",
        }
        needs_card_info = intent in {
            "card_blocked", "card_not_received", "lost_or_stolen_card",
        }
        needs_account = intent in {"account_blocked", "loan_repayment_issue"}

        if needs_txn_id and not any(w in text for w in ["reference", "txn", "transaction id", "ref no", "order"]):
            missing.append("Transaction reference number / ID")
        if needs_card_info and not any(w in text for w in ["last 4", "card number", "ending in"]):
            missing.append("Last 4 digits or card number")
        if needs_account and not any(w in text for w in ["account number", "account no"]):
            missing.append("Account number")

        return missing

    def run(
        self,
        message: str,
        intent: str,
        priority: Priority,
        policy_title: str,
        policy_body: str,
    ) -> DraftResult:
        """
        Draft a reply for the customer.

        Parameters
        ----------
        message : str     – raw customer message
        intent : str      – detected intent
        priority : Priority – risk/priority level
        policy_title : str  – title of the retrieved policy
        policy_body : str   – body text of the retrieved policy

        Returns
        -------
        DraftResult
            Draft reply text, missing-info list, and suggested next action.
        """
        logger.info("DraftNode: generating reply via Ollama for intent='%s'", intent)

        missing = self._detect_missing_info(message, intent)

        # ── Try LLM ───────────────────────────────────────────────────────────
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": self._build_prompt(message, intent, priority, policy_body)},
            ]
            draft = _ollama.chat(messages, temperature=0.3, max_tokens=400)

            if not draft or len(draft.strip()) < 20:
                raise ValueError("LLM returned an empty or too-short response.")

            logger.info("DraftNode: LLM reply generated (%d chars).", len(draft))

        except Exception as exc:
            logger.warning("DraftNode: LLM unavailable (%s). Using template fallback.", exc)
            draft = self._template_fallback(message, intent, priority, policy_title, policy_body)

        return DraftResult(
            draft_reply=draft,
            missing_info=missing,
            suggested_next_action="validate",
        )
