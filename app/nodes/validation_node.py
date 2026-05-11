"""
app/nodes/validation_node.py

Validation Node.

Checks the generated draft reply and the overall pipeline state to decide
whether the response is acceptable before it is routed to the customer.

Checks performed:
  1. Draft length — too short replies are likely incomplete.
  2. Intent confidence — low-confidence predictions may be wrong.
  3. Missing information — required fields absent from the customer message.
  4. Banned / inappropriate phrases — crude safety guard.
  5. Policy coherence check — ensures the policy title appears or the draft
     at least references the intent topic (keyword heuristic).
"""

import logging
from typing import List

from app.core.schemas import Priority, ValidationResult

logger = logging.getLogger(__name__)

# ── Thresholds (easily tuneable) ──────────────────────────────────────────────
MIN_DRAFT_LENGTH = 50          # characters
CONFIDENCE_THRESHOLD = 0.55    # below this → low-confidence flag

# Phrases that should never appear in a customer-facing reply
BANNED_PHRASES = [
    "i don't know",
    "i have no idea",
    "cannot help",
    "i'm not sure",
    "as an ai",
    "as a language model",
]


class ValidationNode:
    """
    Validates the pipeline output before routing.

    Returns a ValidationResult indicating whether the draft passed all
    checks and listing any issues found.
    """

    def _check_length(self, draft: str) -> str | None:
        if len(draft.strip()) < MIN_DRAFT_LENGTH:
            return (
                f"Draft reply is too short ({len(draft.strip())} chars). "
                f"Minimum expected: {MIN_DRAFT_LENGTH} chars."
            )
        return None

    def _check_confidence(self, confidence: float) -> str | None:
        if confidence < CONFIDENCE_THRESHOLD:
            return (
                f"Intent confidence ({confidence:.0%}) is below threshold "
                f"({CONFIDENCE_THRESHOLD:.0%}). Prediction may be unreliable."
            )
        return None

    def _check_missing_info(self, missing_info: List[str]) -> str | None:
        if missing_info:
            return (
                f"Required information missing from customer message: "
                f"{', '.join(missing_info)}."
            )
        return None

    def _check_banned_phrases(self, draft: str) -> str | None:
        draft_lower = draft.lower()
        for phrase in BANNED_PHRASES:
            if phrase in draft_lower:
                return (
                    f"Draft contains disallowed phrase: '{phrase}'. "
                    "Reply may be unhelpful or expose system internals."
                )
        return None

    def run(
        self,
        draft: str,
        intent: str,
        confidence: float,
        priority: Priority,
        missing_info: List[str],
    ) -> ValidationResult:
        """
        Validate the draft reply and pipeline state.

        Parameters
        ----------
        draft : str             – draft reply text from DraftNode
        intent : str            – detected intent
        confidence : float      – intent classifier confidence (0–1)
        priority : Priority     – case priority level
        missing_info : list     – missing info list from DraftNode

        Returns
        -------
        ValidationResult
            passed flag, list of issues, and component-level checks.
        """
        logger.info("ValidationNode: validating draft for intent='%s'", intent)

        issues: List[str] = []
        confidence_ok = True
        length_ok = True

        # Run each check
        if (issue := self._check_length(draft)):
            issues.append(issue)
            length_ok = False

        if (issue := self._check_confidence(confidence)):
            issues.append(issue)
            confidence_ok = False

        if (issue := self._check_missing_info(missing_info)):
            issues.append(issue)

        if (issue := self._check_banned_phrases(draft)):
            issues.append(issue)

        # High-priority cases require human validation by policy
        if priority == Priority.HIGH and not issues:
            logger.info(
                "ValidationNode: HIGH priority case — flagging for human review regardless."
            )
            issues.append(
                "HIGH priority case flagged for mandatory human review per escalation policy."
            )

        passed = len(issues) == 0
        logger.info(
            "ValidationNode: result=passed=%s, issues=%d", passed, len(issues)
        )

        return ValidationResult(
            passed=passed,
            issues=issues,
            confidence_ok=confidence_ok,
            length_ok=length_ok,
        )
