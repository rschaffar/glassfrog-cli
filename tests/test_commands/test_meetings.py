"""Tests for meeting commands."""

import json

import httpx
import pytest
import respx
from click.testing import CliRunner

from glassfrog_cli.main import cli

BASE_URL = "https://api.glassfrog.com/api/v3"


@pytest.fixture
def runner():
    return CliRunner()


class TestMeetingsChecklist:
    @respx.mock
    def test_checklist_table(self, runner):
        respx.get(f"{BASE_URL}/circles/1/checklist_items").mock(
            return_value=httpx.Response(
                200,
                json={
                    "checklist_items": [
                        {
                            "id": 1,
                            "description": "Review PRs",
                            "frequency": "Weekly",
                            "global": False,
                            "links": {"circle": 1, "role": 10},
                        }
                    ]
                },
            )
        )

        result = runner.invoke(cli, ["--token", "test", "meetings", "checklist", "--circle", "1"])

        assert result.exit_code == 0
        assert "Review PRs" in result.output
        assert "Weekly" in result.output


class TestMeetingsMetrics:
    @respx.mock
    def test_metrics_table(self, runner):
        respx.get(f"{BASE_URL}/circles/1/metrics").mock(
            return_value=httpx.Response(
                200,
                json={
                    "metrics": [
                        {
                            "id": 1,
                            "description": "Revenue",
                            "frequency": "Monthly",
                            "global": False,
                            "links": {"circle": 1, "role": None},
                        }
                    ]
                },
            )
        )

        result = runner.invoke(cli, ["--token", "test", "meetings", "metrics", "--circle", "1"])

        assert result.exit_code == 0
        assert "Revenue" in result.output
        assert "Monthly" in result.output


class TestMeetingsActions:
    @respx.mock
    def test_actions_table(self, runner):
        respx.get(f"{BASE_URL}/actions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "actions": [
                        {
                            "id": 1,
                            "description": "Fix the bug",
                            "created_at": "2026-02-20T14:30:00Z",
                            "links": {"circle": 1, "person": 50},
                        },
                        {
                            "id": 2,
                            "description": "Write tests",
                            "created_at": "2026-02-21T09:00:00Z",
                            "links": {"circle": 2, "person": 51},
                        },
                    ]
                },
            )
        )

        result = runner.invoke(cli, ["--token", "test", "meetings", "actions"])

        assert result.exit_code == 0
        assert "Fix the bug" in result.output
        assert "Write tests" in result.output

    @respx.mock
    def test_actions_filter_by_circle(self, runner):
        respx.get(f"{BASE_URL}/actions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "actions": [
                        {
                            "id": 1,
                            "description": "Fix the bug",
                            "created_at": "2026-02-20T14:30:00Z",
                            "links": {"circle": 1, "person": 50},
                        },
                        {
                            "id": 2,
                            "description": "Write tests",
                            "created_at": "2026-02-21T09:00:00Z",
                            "links": {"circle": 2, "person": 51},
                        },
                    ]
                },
            )
        )

        result = runner.invoke(cli, ["--token", "test", "meetings", "actions", "--circle", "1"])

        assert result.exit_code == 0
        assert "Fix the bug" in result.output
        assert "Write tests" not in result.output

    @respx.mock
    def test_actions_json(self, runner):
        respx.get(f"{BASE_URL}/actions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "actions": [
                        {
                            "id": 1,
                            "description": "Fix the bug",
                            "created_at": "2026-02-20T14:30:00Z",
                            "links": {"circle": 1, "person": 50},
                        }
                    ]
                },
            )
        )

        result = runner.invoke(cli, ["--token", "test", "-o", "json", "meetings", "actions"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["description"] == "Fix the bug"
