"""Tests for generic vs Plektra profile configuration and legacy env fallbacks."""

from __future__ import annotations

import pytest

from handqa.config import active_profile, env_get, is_plektra_package, keyboard_package
from handqa.ledger import BuildError, require_keyboard_build
from handqa.screen_gate import ScreenGate


def test_generic_mode_accepts_any_installed_keyboard():
    assert active_profile({}) == ""
    assert keyboard_package({}) == ""
    assert not is_plektra_package("com.google.android.inputmethod.latin", {})
    build = "com.google.android.inputmethod.latin versionName=14"
    assert require_keyboard_build(build, "") == build
    with pytest.raises(BuildError):
        require_keyboard_build("", "")


def test_plektra_profile_defaults_to_upstream_package():
    env = {"HANDQA_PROFILE": "plektra"}
    assert active_profile(env) == "plektra"
    assert keyboard_package(env) == "rocks.pkb.plektra"
    assert is_plektra_package("rocks.pkb.plektra", env)


def test_handqa_env_wins_over_legacy_plektra_qa_env():
    env = {
        "HANDQA_PACKAGE": "com.example.ime",
        "PLEKTRA_QA_PACKAGE": "rocks.pkb.plektra.djb",
    }
    assert env_get("PACKAGE", legacy="PACKAGE", env=env) == "com.example.ime"
    assert keyboard_package(env) == "com.example.ime"
    # Legacy fallback still works when HANDQA_* is absent.
    legacy_only = {"PLEKTRA_QA_PACKAGE": "rocks.pkb.plektra.djb"}
    assert keyboard_package(legacy_only) == "rocks.pkb.plektra.djb"
    assert active_profile(legacy_only) == "plektra"


def test_generic_screen_gate_watcher_has_no_plektra_dependency():
    gate = ScreenGate("SERIAL", shell=lambda args: "")
    gate._saved_heads = "1"
    gate._saved_timeout = "120000"
    gate._saved_stay = "0"
    watcher = gate._watcher_text()
    assert "restore_qa_keyboard_after_stop" not in watcher
    assert "SoftwareKeyboardModeActionActivity" not in watcher
    with pytest.raises(RuntimeError, match="HANDQA_PROFILE=plektra"):
        gate.keyboard_state()
