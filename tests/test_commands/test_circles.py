"""Tests for circle commands."""

import json

import httpx
import pytest
import respx
from click.testing import CliRunner

from glassfrog_cli.main import cli

BASE_URL = "https://api.glassfrog.com/api/v3"

CIRCLES_RESPONSE = {
    "circles": [
        {
            "id": 1,
            "name": "General Company",
            "short_name": "GCC",
            "strategy": "Focus on product",
            "organization_id": 100,
            "links": {
                "roles": [10, 11],
                "policies": [],
                "domain": [],
                "supported_role": 10,
            },
        },
        {
            "id": 2,
            "name": "Engineering",
            "short_name": "Eng",
            "strategy": None,
            "organization_id": 100,
            "links": {
                "roles": [12],
                "policies": [],
                "domain": [],
                "supported_role": 12,
            },
        },
    ],
    "linked": {
        "roles": [
            {"id": 10, "name": "Lead Link", "is_core": True, "links": {"circle": 1}},
            {"id": 11, "name": "Secretary", "is_core": True, "links": {"circle": 1}},
            {"id": 12, "name": "Lead Link", "is_core": True, "links": {"circle": 2}},
        ],
        "policies": [],
        "domains": [],
    },
}

CIRCLE_DETAIL_RESPONSE = {
    "circles": [
        {
            "id": 1,
            "name": "General Company",
            "short_name": "GCC",
            "strategy": "Focus on product",
            "organization_id": 100,
            "links": {
                "roles": [10, 11],
                "policies": [20],
                "domain": [30],
                "supported_role": 10,
            },
        }
    ],
    "linked": {
        "roles": [
            {"id": 10, "name": "Lead Link", "is_core": True},
            {"id": 11, "name": "Secretary", "is_core": True},
        ],
        "policies": [{"id": 20, "title": "Code Review", "body": "All code reviewed"}],
        "domains": [{"id": 30, "description": "Product roadmap"}],
    },
}

ROLES_RESPONSE = {
    "roles": [
        {
            "id": 10,
            "name": "Lead Link",
            "is_core": True,
            "links": {"circle": 1, "supporting_circle": None},
        },
        {
            "id": 11,
            "name": "Secretary",
            "is_core": True,
            "links": {"circle": 1, "supporting_circle": None},
        },
        {
            "id": 12,
            "name": "Engineering Lead",
            "is_core": False,
            "links": {"circle": 1, "supporting_circle": 2},
        },
    ]
}


@pytest.fixture
def runner():
    return CliRunner()


class TestCirclesList:
    @respx.mock
    def test_list_table(self, runner):
        respx.get(f"{BASE_URL}/circles").mock(
            return_value=httpx.Response(200, json=CIRCLES_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "circles", "list"])

        assert result.exit_code == 0
        assert "General Company" in result.output
        assert "Engineering" in result.output

    @respx.mock
    def test_list_json(self, runner):
        respx.get(f"{BASE_URL}/circles").mock(
            return_value=httpx.Response(200, json=CIRCLES_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "-o", "json", "circles", "list"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        assert data[0]["name"] == "General Company"


class TestCirclesShow:
    @respx.mock
    def test_show_table(self, runner):
        respx.get(f"{BASE_URL}/circles/1").mock(
            return_value=httpx.Response(200, json=CIRCLE_DETAIL_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "circles", "show", "1"])

        assert result.exit_code == 0
        assert "General Company" in result.output
        assert "Lead Link" in result.output
        assert "Code Review" in result.output
        assert "Product roadmap" in result.output

    @respx.mock
    def test_show_json(self, runner):
        respx.get(f"{BASE_URL}/circles/1").mock(
            return_value=httpx.Response(200, json=CIRCLE_DETAIL_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "-o", "json", "circles", "show", "1"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "General Company"

    @respx.mock
    def test_show_not_found(self, runner):
        respx.get(f"{BASE_URL}/circles/999").mock(
            return_value=httpx.Response(200, json={"circles": []})
        )

        result = runner.invoke(cli, ["--token", "test", "circles", "show", "999"])

        assert result.exit_code != 0
        assert "not found" in result.output


class TestCirclesTree:
    @respx.mock
    def test_tree(self, runner):
        respx.get(f"{BASE_URL}/circles").mock(
            return_value=httpx.Response(200, json=CIRCLES_RESPONSE)
        )
        respx.get(f"{BASE_URL}/roles").mock(
            return_value=httpx.Response(200, json=ROLES_RESPONSE)
        )

        result = runner.invoke(cli, ["--token", "test", "circles", "tree"])

        assert result.exit_code == 0
        assert "Organization" in result.output
        assert "General Company" in result.output
