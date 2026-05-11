"""
app/clients/base.py

Abstract base class / interface for all model-calling clients.
All concrete clients (Ollama, OpenAI-compatible, etc.) must inherit from
BaseLLMClient and implement the `generate` method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseLLMClient(ABC):
    """
    Minimal interface for LLM clients used in the banking agentic pipeline.
    
    Attributes
    ----------
    base_url : str
        The base URL of the model-serving endpoint.
    model : str
        The model tag / identifier to call.
    timeout : int
        Request timeout in seconds.
    """

    def __init__(self, base_url: str, model: str, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Send *prompt* to the model and return the raw text response.

        Parameters
        ----------
        prompt : str
            The user-facing prompt / instruction.
        system_prompt : str, optional
            An optional system instruction prepended to the conversation.
        **kwargs
            Additional model parameters (temperature, max_tokens, etc.).

        Returns
        -------
        str
            The model's text output.
        """

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """
        Send a list of chat messages and return the assistant's reply.

        Parameters
        ----------
        messages : list of dict
            OpenAI-style message list, e.g. [{"role": "user", "content": "..."}].
        **kwargs
            Additional model parameters.

        Returns
        -------
        str
            The assistant's text reply.
        """

    def health_check(self) -> bool:
        """
        Optional: verify that the model server is reachable.
        Override in subclasses for a real health check.
        """
        return True
