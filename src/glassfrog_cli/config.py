"""Configuration loading for GlassFrog CLI.

Token resolution order:
  1. --token CLI flag (passed via click context)
  2. GLASSFROG_API_TOKEN environment variable
  3. ~/.config/glassfrog/config.toml [auth] token field
"""

from __future__ import annotations

import os
from pathlib import Path

import click

CONFIG_DIR = Path.home() / ".config" / "glassfrog"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def _load_token_from_config_file() -> str | None:
    """Read the API token from ~/.config/glassfrog/config.toml."""
    if not CONFIG_FILE.exists():
        return None

    try:
        import tomli

        with open(CONFIG_FILE, "rb") as f:
            data = tomli.load(f)
        return data.get("auth", {}).get("token")
    except Exception:
        return None


def resolve_token(ctx_token: str | None = None) -> str:
    """Resolve the API token from CLI flag, env var, or config file.

    Raises click.UsageError if no token is found.
    """
    # 1. CLI flag
    if ctx_token:
        return ctx_token

    # 2. Environment variable
    env_token = os.environ.get("GLASSFROG_API_TOKEN")
    if env_token:
        return env_token

    # 3. Config file
    file_token = _load_token_from_config_file()
    if file_token:
        return file_token

    raise click.UsageError(
        "No API token found. Provide one via:\n"
        "  --token flag\n"
        "  GLASSFROG_API_TOKEN environment variable\n"
        f"  {CONFIG_FILE} with [auth] token = '...'"
    )
