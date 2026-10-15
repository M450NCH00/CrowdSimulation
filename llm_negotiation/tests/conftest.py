"""Shared fixtures. Every test runs with the network blocked and the real ``.env`` out of reach."""

from __future__ import annotations

import urllib.request

import pytest

import negsim.llm.env as env_module


@pytest.fixture(autouse=True)
def no_network_no_secrets(monkeypatch):
    """Guarantee zero spend: no test can reach the network or read the real API key."""

    def refuse(*args, **kwargs):
        raise AssertionError("a test tried to open a network connection")

    monkeypatch.setattr(urllib.request, "urlopen", refuse)
    monkeypatch.setattr(env_module, "ENV_FILE_CANDIDATES", ())
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_BASE_URL", raising=False)
