"""Tests for config module."""

import os
from unittest.mock import patch

import click
import pytest

from glassfrog_cli.config import resolve_token


class TestResolveToken:
    def test_cli_flag_takes_precedence(self, monkeypatch):
        monkeypatch.setenv("GLASSFROG_API_TOKEN", "env-token")
        assert resolve_token("cli-token") == "cli-token"

    def test_env_var_used_when_no_flag(self, monkeypatch):
        monkeypatch.setenv("GLASSFROG_API_TOKEN", "env-token")
        assert resolve_token(None) == "env-token"

    def test_config_file_used_when_no_flag_or_env(self, monkeypatch, tmp_path):
        monkeypatch.delenv("GLASSFROG_API_TOKEN", raising=False)

        config_file = tmp_path / "config.toml"
        config_file.write_text('[auth]\ntoken = "file-token"\n')

        with patch("glassfrog_cli.config.CONFIG_FILE", config_file):
            assert resolve_token(None) == "file-token"

    def test_raises_when_no_token_found(self, monkeypatch, tmp_path):
        monkeypatch.delenv("GLASSFROG_API_TOKEN", raising=False)

        config_file = tmp_path / "nonexistent.toml"
        with patch("glassfrog_cli.config.CONFIG_FILE", config_file):
            with pytest.raises(click.UsageError, match="No API token found"):
                resolve_token(None)

    def test_empty_env_var_falls_through(self, monkeypatch, tmp_path):
        monkeypatch.setenv("GLASSFROG_API_TOKEN", "")

        config_file = tmp_path / "config.toml"
        config_file.write_text('[auth]\ntoken = "file-token"\n')

        with patch("glassfrog_cli.config.CONFIG_FILE", config_file):
            # Empty string is falsy, should fall through to config file
            assert resolve_token(None) == "file-token"

    def test_malformed_config_file_falls_through(self, monkeypatch, tmp_path):
        monkeypatch.delenv("GLASSFROG_API_TOKEN", raising=False)

        config_file = tmp_path / "config.toml"
        config_file.write_text("this is not valid toml {{{{")

        with patch("glassfrog_cli.config.CONFIG_FILE", config_file):
            with pytest.raises(click.UsageError, match="No API token found"):
                resolve_token(None)
