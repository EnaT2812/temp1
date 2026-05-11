"""
app/nodes/priority_node.py

Priority / Risk Detection Node.

Classifies each customer case as LOW, MEDIUM, or HIGH priority based on
intent label and keyword signals in the customer message.
Rule-based logic is intentionally transparent so that it can be audited
and extended without retraining a model.
"""

import logging
import re
from typing import List, Tuple

from app.core.schemas import Priority, PriorityResult

logger = logging.getLogger(__name__)


# ── Risk configuration ────────────────────────────────────────────────────────

# Intents that are unconditionally HIGH priority
HIGH_PRIORITY_INTENTS = {
    "fraud_report",
    "lost_or_stolen_card",
    "account_blocked",
    "transfer_failure",       # may involve stuck funds
    "wrong_transfer",
}

# Intents that are unconditionally MEDIUM priority
MEDIUM_PRIORITY_INTENTS = {
    "card_blocked",
    "login_issue",
    "otp_issue",
    "loan_repayment_issue",
    "deposit_issue",
    "bill_payment_issue",
}

# Keyword patterns that bump ANY case to HIGH priority
HIGH_PRIORITY_KEYWORDS: List[str] = [
    "urgent",
    "immediately",
    "emergency",
    "money gone",
    "lost all",
    "fraud",
    "scam",
    "hacked",
    "blocked",
    "suspicious",
    "cannot access",
    "large amount",
    "huge amount",
]

# Keyword patterns that bump a LOW case to MEDIUM
MEDIUM_PRIORITY_KEYWORDS: List[str] = [
    "important",
    "soon",
    "please help",
    "not working",
    "failed",
    "error",
    "issue",
    "problem",
    "missing",
]


class PriorityNode:
    """
    Determines the priority level of a customer support case.

    Rules (evaluated in order):
    1. If a HIGH_PRIORITY_KEYWORD is found → HIGH
    2. If the intent is in HIGH_PRIORITY_INTENTS → HIGH
    3. If the intent is in MEDIUM_PRIORITY_INTENTS → MEDIUM
    4. If a MEDIUM_PRIORITY_KEYWORD is found → MEDIUM
    5. Otherwise → LOW
    """

    def _find_keywords(self, text: str, keywords: List[str]) -> List[str]:
        text_lower = text.lower()
        return [kw for kw in keywords if kw.lower() in text_lower]

    def run(self, message: str, intent: str) -> PriorityResult:
        """
        Classify the case priority.

        Parameters
        ----------
        message : str
            The customer's raw message.
        intent : str
            The detected intent from the IntentNode.

        Returns
        -------
        PriorityResult
            Priority level, human-readable reason, and triggered keywords.
        """
        logger.info("PriorityNode: evaluating intent='%s'", intent)

        high_kws = self._find_keywords(message, HIGH_PRIORITY_KEYWORDS)
        medium_kws = self._find_keywords(message, MEDIUM_PRIORITY_KEYWORDS)

        # Rule 1 – keyword escalation takes precedence
        if high_kws:
            return PriorityResult(
                priority=Priority.HIGH,
                reason=(
                    f"High-severity keywords detected in the message: {high_kws}. "
                    "Immediate attention required."
                ),
                triggered_keywords=high_kws,
            )

        # Rule 2 – intent-based HIGH
        if intent in HIGH_PRIORITY_INTENTS:
            return PriorityResult(
                priority=Priority.HIGH,
                reason=(
                    f"Intent '{intent}' is classified as high-priority by policy "
                    "(involves potential financial loss or account access)."
                ),
                triggered_keywords=[],
            )

        # Rule 3 – intent-based MEDIUM
        if intent in MEDIUM_PRIORITY_INTENTS:
            return PriorityResult(
                priority=Priority.MEDIUM,
                reason=(
                    f"Intent '{intent}' requires timely follow-up but is not an "
                    "immediate emergency."
                ),
                triggered_keywords=medium_kws,
            )

        # Rule 4 – keyword-based MEDIUM
        if medium_kws:
            return PriorityResult(
                priority=Priority.MEDIUM,
                reason=(
                    f"Medium-concern keywords found: {medium_kws}. "
                    "Treated as medium priority."
                ),
                triggered_keywords=medium_kws,
            )

        # Rule 5 – default LOW
        return PriorityResult(
            priority=Priority.LOW,
            reason=(
                f"Intent '{intent}' is a routine inquiry with no urgent signals detected."
            ),
            triggered_keywords=[],
        )
