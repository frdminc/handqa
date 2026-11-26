"""Environment and profile configuration for handqa.

Prefers `HANDQA_*` variables and falls back to legacy `PLEKTRA_QA_*` names when
set, so existing Plektra `.env` files continue to work without breaking.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from handqa.profiles import plektra as plektra_profile


def env_get(
    name: str,
    *,
    legacy: str | None = None,
    default: str = "",
    env: Mapping[str, str] | None = None,
) -> str:
    """Read `HANDQA_<name>`, falling back to `PLEKTRA_QA_<legacy>` then `default`."""
    source = os.environ if env is None else env
    value = source.get(f"HANDQA_{name}", "").strip()
    if value:
        return value
    if legacy:
        old = source.get(f"PLEKTRA_QA_{legacy}", "").strip()
        if old:
            return old
    return default


def active_profile(env: Mapping[str, str] | None = None) -> str:
    """Active project profile name: explicit `HANDQA_PROFILE`, or inferred from package."""
    source = os.environ if env is None else env
    explicit = source.get("HANDQA_PROFILE", "").strip().lower()
    if explicit:
        return "" if explicit in ("none", "generic", "default") else explicit
    pkg = env_get("PACKAGE", legacy="PACKAGE", env=source)
    if pkg.startswith("rocks.pkb.plektra") or source.get("PLEKTRA_QA_PACKAGE", "").strip():
        return "plektra"
    return ""


def is_plektra_package(package: str, env: Mapping[str, str] | None = None) -> bool:
    """True when the target keyboard package uses the Plektra profile hooks."""
    if package.startswith("rocks.pkb.plektra"):
        return True
    return active_profile(env) == "plektra"


def keyboard_package(env: Mapping[str, str] | None = None) -> str:
    """Configured keyboard package ID, or Plektra's upstream ID when profile=plektra."""
    pkg = env_get("PACKAGE", legacy="PACKAGE", env=env)
    if pkg:
        return pkg
    if active_profile(env) == "plektra":
        return plektra_profile.DEFAULT_PACKAGE
    return ""


def default_keymap_profile() -> Path:
    return plektra_profile.DEFAULT_KEYMAP_PROFILE
