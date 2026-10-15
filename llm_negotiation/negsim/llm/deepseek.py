"""DeepSeek client.

DeepSeek's API is OpenAI-compatible, and its docs show the ``openai`` package. This client
talks to the one endpoint it needs, ``POST {base_url}/chat/completions``, with the standard
library instead: there is then no SDK version to pin, and nothing but this file ever
handles the request headers, which carry the API key.

Facts about the API used here were taken from https://api-docs.deepseek.com on 2026-10-13
and are recorded, with the pages they came from, in ``docs/llm-backend.md``.

The key is read from ``DEEPSEEK_API_KEY`` (environment, else the repository's ``.env``).
It is held in a private attribute, sent only in the ``Authorization`` header, and removed
from any error text before that text can reach a log.
"""

from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from .base import LLMClient, LLMFatalError, LLMRequest, LLMResponse, LLMTransientError, Usage
from .env import get_setting

API_KEY_ENV = "DEEPSEEK_API_KEY"
BASE_URL_ENV = "DEEPSEEK_BASE_URL"
DEFAULT_BASE_URL = "https://api.deepseek.com"

# "429 - Rate Limit Reached", "500 - Server Error", "503 - Server Overloaded": the docs say
# to retry these after a wait (api-docs.deepseek.com/quick_start/error_codes).
RETRYABLE_STATUS = (429, 500, 503)

# (url, headers, body, timeout seconds) -> (HTTP status, response body)
Transport = Callable[[str, Mapping[str, str], bytes, float], tuple[int, bytes]]


def _urllib_transport(
    url: str, headers: Mapping[str, str], body: bytes, timeout: float
) -> tuple[int, bytes]:
    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


class DeepSeekClient(LLMClient):
    name = "deepseek"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout_s: float = 60.0,
        max_retries: int = 2,
        retry_wait_s: float = 2.0,
        transport: Optional[Transport] = None,
        sleep: Callable[[float], None] = time.sleep,
    ):
        if not api_key:
            raise LLMFatalError(f"no API key: set {API_KEY_ENV} in the environment or in .env")
        self._api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.max_attempts = max_retries + 1
        self.retry_wait_s = retry_wait_s
        self._transport = transport or _urllib_transport
        self._sleep = sleep

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None, **kwargs: Any) -> "DeepSeekClient":
        api_key = get_setting(API_KEY_ENV, env_file)
        if not api_key:
            raise LLMFatalError(
                f"{API_KEY_ENV} is not set. Put it in the repository's .env file "
                "(see .env.example) or export it in the shell."
            )
        base_url = get_setting(BASE_URL_ENV, env_file) or DEFAULT_BASE_URL
        return cls(api_key, base_url=base_url, **kwargs)

    def __repr__(self) -> str:
        return f"DeepSeekClient(base_url={self.base_url!r}, api_key=<hidden>)"

    def describe(self) -> dict[str, Any]:
        return {
            "client": self.name,
            "base_url": self.base_url,
            "timeout_s": self.timeout_s,
            "max_retries": self.max_retries,
        }

    @staticmethod
    def build_payload(request: LLMRequest) -> dict[str, Any]:
        """The JSON body of the request.

        Thinking mode is on by default at DeepSeek and "temperature ... has no effect in
        thinking mode", so it is switched off explicitly unless the request asks for it.
        """
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [dict(message) for message in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": False,
            "thinking": {"type": "enabled" if request.thinking else "disabled"},
        }
        if request.json_mode:
            payload["response_format"] = {"type": "json_object"}
        return payload

    def complete(self, request: LLMRequest) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        body = json.dumps(self.build_payload(request)).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        started_utc = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        clock_start = time.perf_counter()
        failure = "no attempt was made"
        for attempt in range(self.max_attempts):
            if attempt:
                self._sleep(self.retry_wait_s * attempt)
            try:
                status, raw = self._transport(url, headers, body, self.timeout_s)
            except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as exc:
                failure = self._scrub(f"network error: {type(exc).__name__}: {exc}")
                continue
            if status == 200:
                latency = time.perf_counter() - clock_start
                return self._parse(raw, request, started_utc, latency, failed_attempts=attempt)
            failure = self._scrub(f"HTTP {status}: {_error_message(raw)}")
            if status not in RETRYABLE_STATUS:
                raise LLMFatalError(failure)
        raise LLMTransientError(
            f"{failure} (after {self.max_attempts} attempts)", attempts=self.max_attempts
        )

    def _parse(
        self,
        raw: bytes,
        request: LLMRequest,
        started_utc: str,
        latency_s: float,
        failed_attempts: int,
    ) -> LLMResponse:
        try:
            data = json.loads(raw.decode("utf-8"))
            choice = data["choices"][0]
            content = choice["message"].get("content")
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
            # The request was served, so it was billed even though the reply is unusable.
            raise LLMTransientError(
                self._scrub(f"unreadable response body: {type(exc).__name__}: {exc}"),
                attempts=failed_attempts + 1,
            ) from exc
        usage = data.get("usage") or {}
        details = usage.get("completion_tokens_details") or {}
        return LLMResponse(
            content=content,
            finish_reason=choice.get("finish_reason"),
            usage=Usage(
                prompt_tokens=int(usage.get("prompt_tokens", 0)),
                completion_tokens=int(usage.get("completion_tokens", 0)),
                cache_hit_tokens=int(usage.get("prompt_cache_hit_tokens", 0)),
                cache_miss_tokens=int(usage.get("prompt_cache_miss_tokens", 0)),
                reasoning_tokens=int(details.get("reasoning_tokens", 0)),
            ),
            model=str(data.get("model", request.model)),
            latency_s=latency_s,
            started_utc=started_utc,
            response_id=data.get("id"),
            system_fingerprint=data.get("system_fingerprint"),
            failed_attempts=failed_attempts,
        )

    def _scrub(self, text: str) -> str:
        """Remove the API key from ``text``, in case an error message ever echoes it."""
        return text.replace(self._api_key, "<redacted>")


def _error_message(raw: bytes, limit: int = 300) -> str:
    """The provider's error message from a response body, shortened."""
    text = raw.decode("utf-8", errors="replace")
    try:
        message = json.loads(text)["error"]["message"]
        text = message if isinstance(message, str) else text
    except (ValueError, KeyError, TypeError):
        pass
    return " ".join(text.split())[:limit]
