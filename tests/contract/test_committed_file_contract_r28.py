"""Offline contract checks over committed files only (R28).

Every assertion reads a tracked file from this repository and uses the Python
standard library only. There are no network calls, credentials, .env reads,
service actions, index writes or model loads. No project module is imported,
so running this file cannot start a voice/LLM stack.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SENSITIVE_KEY_RE = re.compile(
    r"(?i)(api[_.-]?key|access[_.-]?key|token|secret|password|passwd|credential|bearer)"
)
CREDENTIAL_VALUE_RE = re.compile(r"sk-[A-Za-z0-9]{8,}|gh[pousr]_[A-Za-z0-9]{8,}")
URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://([^/:?#]+)")
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _committed_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_env_example_is_loopback_and_credential_free() -> None:
    """The tracked example defines loopback-only settings and no secrets."""
    seen: set[str] = set()
    for raw in _committed_text(".env.example").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        assert "=" in line, "malformed example setting line"
        key, value = line.split("=", 1)
        key = key.strip()
        assert re.fullmatch(r"[A-Z][A-Z0-9_]*", key), f"unexpected example key shape: {key}"
        assert key not in seen, f"duplicate example key: {key}"
        seen.add(key)
        assert not SENSITIVE_KEY_RE.search(key), f"sensitive example key: {key}"
        # Assertion messages name keys only; values are never printed.
        assert not CREDENTIAL_VALUE_RE.search(value), f"credential-shaped value for {key}"
        for candidate in re.findall(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s]+", value):
            match = URL_RE.match(candidate)
            assert match and match.group(1) in LOOPBACK_HOSTS, f"non-loopback URL for {key}"
    assert {"STT_WS_URL", "TASK_DB_PATH", "RALPH_MODEL_ROUTING_PATH"} <= seen


def test_routing_json_is_well_formed_and_loopback_only() -> None:
    """Committed routing configuration has closed fields and loopback endpoints."""
    data = json.loads(_committed_text("routing.json"))
    assert set(data) == {"routes"}
    routes = data["routes"]
    assert isinstance(routes, list) and routes
    required = {
        "name",
        "provider",
        "base_url",
        "model",
        "max_context",
        "use_cases",
        "latency_weight",
        "quality_weight",
    }
    names: set[str] = set()
    for route in routes:
        assert required <= set(route), "route missing a required field"
        assert not any(SENSITIVE_KEY_RE.search(str(k)) for k in route), "sensitive route field"
        assert route["name"] not in names, "duplicate route name"
        names.add(route["name"])
        assert isinstance(route["max_context"], int) and route["max_context"] > 0
        assert isinstance(route["use_cases"], list) and route["use_cases"]
        for weight in ("latency_weight", "quality_weight"):
            assert isinstance(route[weight], (int, float)) and route[weight] > 0
        match = URL_RE.match(route["base_url"])
        assert match and match.group(1) in LOOPBACK_HOSTS, "non-loopback route endpoint"
    assert {"planner-fast", "reasoner-quality"} <= names


def test_prompts_yaml_declares_no_local_model_artifacts() -> None:
    """Tracked prompt settings carry no absolute model/voice paths."""
    text = _committed_text("prompts.yaml")
    for key in ("sample_rate:", "temperature:", "top_p:", "max_duration_s:", "styles:", "prompts:"):
        assert key in text, f"missing prompt setting: {key}"
    for key in ("model_name", "model_path", "speaker_wav"):
        assert re.search(rf"(?m)^{key}:\s*null\s*$", text), f"{key} must stay unresolved"
    assert not re.search(
        r"(?m)^(model_path|speaker_wav):\s*(/|~|[A-Za-z]:[\\/])", text
    ), "absolute model/voice artifact path committed"


def test_example_payloads_are_closed_v3_events() -> None:
    """Tracked v3 event examples parse and carry no credential-shaped fields."""
    payloads = json.loads(_committed_text("examples/payloads/v3_events.json"))
    assert isinstance(payloads, dict) and payloads
    for name, payload in payloads.items():
        assert isinstance(payload, dict)
        assert payload.get("schema_version") == "3.0", f"{name}: wrong schema version"
        assert payload.get("event_type"), f"{name}: missing event type"
        assert not any(SENSITIVE_KEY_RE.search(str(k)) for k in payload), f"{name}: sensitive field"


def test_committed_entrypoint_files_exist() -> None:
    """README-advertised entrypoints and config files are committed."""
    for rel in (
        "README.md",
        "pyproject.toml",
        "requirements.txt",
        "routing.json",
        "prompts.yaml",
        ".env.example",
        "tests/contract/test_voicebus_contract.py",
    ):
        assert (ROOT / rel).is_file(), f"missing committed file: {rel}"
    assert "tts-agent run" in _committed_text("README.md")
