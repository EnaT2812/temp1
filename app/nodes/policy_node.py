"""
app/nodes/policy_node.py

Policy Retrieval Node.

Given a detected intent, this node fetches the relevant FAQ / policy entry
from the policy store (app/data/policies.py) and returns it in a structured
format so that the Response Drafting Node can ground its reply in verified
support knowledge.
"""

import logging

from app.core.schemas import PolicyResult
from app.data.policies import get_policy, list_supported_intents

logger = logging.getLogger(__name__)


class PolicyNode:
    """
    Retrieves the banking policy or FAQ entry that corresponds to the
    detected customer intent.

    The lookup is an exact-match dictionary lookup against the POLICIES
    dictionary in app/data/policies.py.  Unknown intents fall back to the
    'general_inquiry' policy automatically.
    """

    def run(self, intent: str) -> PolicyResult:
        """
        Retrieve the policy for the given *intent*.

        Parameters
        ----------
        intent : str
            The intent label returned by the IntentNode.

        Returns
        -------
        PolicyResult
            The matched policy title, body text, and source metadata.
        """
        logger.info("PolicyNode: retrieving policy for intent='%s'", intent)

        supported = list_supported_intents()
        if intent not in supported:
            logger.warning(
                "Intent '%s' not found in policy store. Using 'general_inquiry' fallback.",
                intent,
            )

        policy_entry = get_policy(intent)

        result = PolicyResult(
            intent=intent,
            policy_title=policy_entry["title"],
            policy_body=policy_entry["body"],
            source="app/data/policies.py",
        )

        logger.debug(
            "PolicyNode: matched policy '%s' (len=%d chars)",
            result.policy_title,
            len(result.policy_body),
        )
        return result
