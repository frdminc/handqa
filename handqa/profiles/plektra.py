"""Plektra keyboard profile for handqa.

Encapsulates the two Plektra-specific integrations:
1. Reading active `key-remap-v2` boolean preferences from `shared_prefs/plektra_prefs.xml`.
2. Toggling software-keyboard mode via Plektra's `SoftwareKeyboardModeActionActivity`
   and clearing its runtime override via `KeyboardBarTestReceiver`.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

DEFAULT_PACKAGE = "rocks.pkb.plektra"
PREFS_PATH = "shared_prefs/plektra_prefs.xml"
MODE_OVERRIDE = "software_keyboard_mode_runtime_override"
TOGGLE_ACTION = "rocks.pkb.plektra.action.TOGGLE_SOFTWARE_KEYBOARD_MODE"
TOGGLE_ACTIVITY_CLASS = "rocks.pkb.plektra.SoftwareKeyboardModeActionActivity"
TEST_RECEIVER_CLASS = "rocks.pkb.plektra.KeyboardBarTestReceiver"
DEFAULT_KEYMAP_PROFILE = (
    Path(__file__).resolve().parents[2] / "profiles" / "plektra" / "keymaps" / "titan2-elite-baseline.yaml"
)

KEY_REMAP_PREFIX = "key_remap_"
# Matches HardwareKeyRemapRegistry.allOptions in Plektra's key-remap-v2.
# Tuple entries are (unsupported_profiles, ((match, scan, key, to), ...)).
KEY_REMAP_OPTIONS: dict[str, tuple[frozenset[str], tuple[tuple[str, int | None, int | None, int], ...]]] = {
    "swap_shift_right_enter": (
        frozenset({"q25"}),
        (
            ("scan", 54, 60, 66),
            ("key", None, 66, 60),
        ),
    ),
}

Runner = Callable[[Sequence[str]], Any]


def _run(cmd: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(cmd), capture_output=True, text=True, timeout=20, check=False)


def raw_rules_from_prefs(xml: str, remap_profile: str) -> tuple[tuple[str, int | None, int | None, int], ...] | None:
    """Plektra's active key-remap-v2 rules from its prefs XML; None when unreadable.

    Plektra reads boolean preferences named `key_remap_<option_id>` (see
    `SettingsManager.getEnabledKeyRemaps` and `HardwareKeyRemapRegistry`). Any
    leftover v1 `hardware_key_remaps` JSON string is ignored by the app and
    therefore ignored here too.
    """
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return None
    if root.tag != "map":
        return None
    profile = remap_profile.lower()
    rules: list[tuple[str, int | None, int | None, int]] = []
    for elem in root.findall("boolean"):
        name = elem.attrib.get("name", "")
        if not name.startswith(KEY_REMAP_PREFIX):
            continue
        if elem.attrib.get("value", "").lower() != "true":
            continue
        option_id = name[len(KEY_REMAP_PREFIX):]
        option = KEY_REMAP_OPTIONS.get(option_id)
        if option is None:
            return None  # an enabled option this harness does not know how to resolve
        unsupported, option_rules = option
        if profile not in unsupported:
            rules.extend(option_rules)
    return tuple(rules)


def read_plektra_raw_rules(
    serial: str,
    remap_profile: str,
    package: str = DEFAULT_PACKAGE,
    run: Runner = _run,
) -> tuple[tuple[str, int | None, int | None, int], ...] | str:
    """The raw remap tuples, or the reason they could not be read (debuggable build needed)."""
    result = run(["adb", "-s", serial, "exec-out", "run-as", package, "cat", PREFS_PATH])
    if result.returncode != 0 or "<map" not in result.stdout:
        return (result.stderr.strip() or result.stdout.strip() or "no output")[:120]
    rules = raw_rules_from_prefs(result.stdout, remap_profile)
    return rules if rules is not None else "the stored remap rules could not be parsed"
