"""
app/nodes/intent_node.py

Intent Detection Node — the core classifier of the banking agentic workflow.

This node is designed as a wrapper that can operate in two modes:

1. **Fine-tuned model mode** (preferred):
   Loads the BERT / DistilBERT checkpoint produced in Lab 2 and runs
   inference locally.  Set INTENT_MODEL_PATH in settings.py (or .env) to
   the path of your saved model directory.

2. **Rule-based fallback mode**:
   When the fine-tuned checkpoint is not available (path doesn't exist or
   torch/transformers are not installed), the node falls back to a simple
   keyword-matching classifier so that the rest of the pipeline still works
   during development and testing.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

from app.core.schemas import IntentResult
from app.core.settings import settings

logger = logging.getLogger(__name__)


# ── Keyword-based fallback rules ──────────────────────────────────────────────
# Each entry: (intent_label, [keyword list])
# The node picks the first matching rule (order matters for priority).

KEYWORD_RULES: List[Tuple[str, List[str]]] = [
    ("fraud_report",         ["fraud", "unauthorized", "unauthorised", "scam", "stolen money", "hacked", "suspicious transaction", "chargeback"]),
    ("lost_or_stolen_card",  ["lost card", "stolen card", "card stolen", "card lost", "missing card"]),
    ("card_blocked",         ["card blocked", "card is blocked", "blocked card", "card declined", "card rejected"]),
    ("card_not_received",    ["card not received", "haven't received my card", "card not arrived", "card delivery", "new card"]),
    ("account_blocked",      ["account blocked", "account suspended", "account frozen", "account locked", "cannot access account"]),
    ("transfer_failure",     ["transfer failed", "transfer not completed", "transaction failed", "payment failed", "money not received", "transfer pending"]),
    ("wrong_transfer",       ["wrong account", "wrong transfer", "sent to wrong", "incorrect account", "mistaken transfer"]),
    ("bill_payment_issue",   ["bill payment", "utility bill", "bill not processed", "duplicate payment", "bill failed"]),
    ("loan_repayment_issue", ["loan overdue", "emi failed", "missed emi", "loan payment", "loan installment"]),
    ("loan_inquiry",         ["loan", "borrow", "credit", "mortgage", "home loan", "auto loan", "personal loan", "interest rate on loan"]),
    ("deposit_issue",        ["deposit not credited", "cash not credited", "cheque not cleared", "atm deposit"]),
    ("interest_rate_inquiry",["interest rate", "fd rate", "fixed deposit", "savings rate", "rate of interest"]),
    ("otp_issue",            ["otp", "one-time password", "otp not received", "verification code"]),
    ("login_issue",          ["cannot login", "can't login", "password reset", "forgot password", "login problem", "unable to login"]),
    ("kyc_update",           ["kyc", "know your customer", "id proof", "document update", "address proof"]),
    ("refund_request",       ["refund", "money back", "reimburse", "reimbursement", "cashback"]),
]

FALLBACK_INTENT = "general_inquiry"


# ── Attempt to load the fine-tuned Lab 2 model ───────────────────────────────

def _try_load_finetuned_pipeline():
    """
    Try to build a HuggingFace text-classification pipeline from the
    fine-tuned checkpoint specified in settings.intent_model_path.
    Returns None if unavailable (missing package or path).
    """
    model_path = Path(settings.intent_model_path)
    if not model_path.exists():
        logger.info(
            "Fine-tuned intent model path '%s' not found. "
            "Using keyword-based fallback.",
            settings.intent_model_path,
        )
        return None

    try:
        from transformers import pipeline  # type: ignore
        clf = pipeline(
            "text-classification",
            model=str(model_path),
            tokenizer=str(model_path),
            truncation=True,
            max_length=128,
        )
        logger.info("Loaded fine-tuned intent model from '%s'.", model_path)
        return clf
    except ImportError:
        logger.warning(
            "`transformers` package not installed. "
            "Install it with: pip install transformers torch\n"
            "Falling back to keyword-based intent detection."
        )
        return None
    except Exception as exc:
        logger.warning("Failed to load fine-tuned model: %s. Using fallback.", exc)
        return None


# Eagerly attempt to load; None → fallback
_finetuned_pipeline = _try_load_finetuned_pipeline()


# ── Node implementation ───────────────────────────────────────────────────────

class IntentNode:
    """
    Identifies the banking intent expressed in a customer message.

    If a fine-tuned HuggingFace checkpoint is available it is used;
    otherwise a keyword-matching heuristic is applied.
    """

    def __init__(self) -> None:
        self._pipeline = _finetuned_pipeline

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _classify_with_model(self, message: str) -> IntentResult:
        results = self._pipeline(message, top_k=None)
        # HuggingFace returns a list of {"label": ..., "score": ...}
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
        top = sorted_results[0]
        raw_scores = {r["label"]: round(r["score"], 4) for r in sorted_results}
        return IntentResult(
            intent=top["label"],
            confidence=round(top["score"], 4),
            raw_scores=raw_scores,
        )

    def _classify_with_keywords(self, message: str) -> IntentResult:
        text = message.lower()
        for intent, keywords in KEYWORD_RULES:
            for kw in keywords:
                if kw.lower() in text:
                    logger.debug("Keyword match: '%s' → intent '%s'", kw, intent)
                    return IntentResult(
                        intent=intent,
                        confidence=0.75,   # heuristic confidence
                        raw_scores=None,
                    )
        logger.debug("No keyword matched. Falling back to '%s'.", FALLBACK_INTENT)
        return IntentResult(
            intent=FALLBACK_INTENT,
            confidence=0.50,
            raw_scores=None,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, message: str) -> IntentResult:
        """
        Classify the customer *message* and return an IntentResult.

        Parameters
        ----------
        message : str
            The raw customer message.

        Returns
        -------
        IntentResult
            Detected intent label and confidence score.
        """
        logger.info("IntentNode: classifying message (len=%d)", len(message))

        if self._pipeline is not None:
            try:
                return self._classify_with_model(message)
            except Exception as exc:
                logger.warning("Fine-tuned model inference failed (%s). Using fallback.", exc)

        return self._classify_with_keywords(message)
