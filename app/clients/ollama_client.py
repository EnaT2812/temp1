"""
app/clients/ollama_client.py

Concrete LLM client that communicates with an Ollama server.
Supports both /api/generate (single prompt) and /api/chat (message list).
The server can be either local (http://localhost:11434) or a public Pinggy
tunnel URL configured in settings.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from app.clients.base import BaseLLMClient

logger = logging.getLogger(__name__)


class OllamaClient(BaseLLMClient):
    """
    Client for the Ollama inference server.

    Usage
    -----
    client = OllamaClient(
        base_url="http://localhost:11434",   # or Pinggy URL
        model="gpt-oss:20b",
        timeout=120,
    )
    reply = client.generate("Summarise the following policy: ...")
    """

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        logger.debug("OllamaClient POST %s  model=%s", url, self.model)
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError as exc:
            logger.error("Cannot reach Ollama at %s: %s", self.base_url, exc)
            raise ConnectionError(
                f"Cannot connect to Ollama server at {self.base_url}. "
                "Make sure Ollama is running (or the Pinggy tunnel is active)."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            logger.error("Ollama HTTP error: %s", exc)
            raise

    # ── Public interface ──────────────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 512,
        **kwargs: Any,
    ) -> str:
        """Call /api/generate with a single prompt string."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        data = self._post("/api/generate", payload)
        return data.get("response", "").strip()

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 512,
        **kwargs: Any,
    ) -> str:
        """Call /api/chat with an OpenAI-style message list."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs,
            },
        }
        data = self._post("/api/chat", payload)
        return data.get("message", {}).get("content", "").strip()

    def health_check(self) -> bool:
        """Return True if the Ollama server is reachable."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
