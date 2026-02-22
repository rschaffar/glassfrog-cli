"""Tests for Pydantic models and response parsing."""

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from glassfrog_cli.models import (
    Action,
    Assignment,
    ChecklistItem,
    Circle,
    LinkedData,
    Metric,
    Person,
    Project,
    Role,
    parse_response,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


class TestCircleModel:
    def test_parse_circles(self):
        data = load_fixture("circles.json")
        circles, linked = parse_response("circles", data)

        assert len(circles) == 2
        assert circles[0].name == "General Company Circle"
        assert circles[0].short_name == "GCC"
        assert circles[0].strategy == "Focus on core product"
        assert circles[0].links.supported_role == 10
        assert circles[0].links.roles == [10, 11, 12]

    def test_circle_with_null_strategy(self):
        data = load_fixture("circles.json")
        circles, _ = parse_response("circles", data)

        assert circles[1].strategy is None

    def test_linked_data_parsed(self):
        data = load_fixture("circles.json")
        _, linked = parse_response("circles", data)

        assert linked is not None
        assert len(linked.roles) == 5
        assert linked.roles[0].name == "Lead Link"
        assert linked.policies[0].title == "Code Review Policy"
        assert linked.domains[0].description == "Product roadmap"


class TestRoleModel:
    def test_parse_roles(self):
        data = load_fixture("roles.json")
        roles, linked = parse_response("roles", data)

        assert len(roles) == 2
        assert roles[0].name == "Lead Link"
        assert roles[0].is_core is True
        assert roles[0].purpose == "Lead the circle"
        assert roles[0].elected_until is None

    def test_role_with_elected_until(self):
        data = load_fixture("roles.json")
        roles, _ = parse_response("roles", data)

        assert roles[1].elected_until == date(2026, 6, 30)

    def test_role_links(self):
        data = load_fixture("roles.json")
        roles, _ = parse_response("roles", data)

        assert roles[0].links.circle == 1
        assert roles[0].links.domains == [30]
        assert roles[0].links.accountabilities == [40, 41]
        assert roles[0].links.people == [50]

    def test_linked_accountabilities(self):
        data = load_fixture("roles.json")
        _, linked = parse_response("roles", data)

        assert linked is not None
        assert len(linked.accountabilities) == 3
        assert linked.accountabilities[0].description == "Allocating resources"


class TestPersonModel:
    def test_parse_people(self):
        data = load_fixture("people.json")
        people, linked = parse_response("people", data)

        assert len(people) == 2
        assert people[0].name == "Alice Smith"
        assert people[0].email == "alice@example.com"
        assert people[0].links.circles == [1, 2]

    def test_no_linked_data(self):
        data = load_fixture("people.json")
        _, linked = parse_response("people", data)

        assert linked is None


class TestAssignmentModel:
    def test_parse_assignments(self):
        data = load_fixture("assignments.json")
        assignments, _ = parse_response("assignments", data)

        assert len(assignments) == 2
        assert assignments[0].focus == "Backend systems"
        assert assignments[0].election == date(2026, 1, 1)
        assert assignments[0].exclude_from_meetings is False

    def test_assignment_null_fields(self):
        data = load_fixture("assignments.json")
        assignments, _ = parse_response("assignments", data)

        assert assignments[1].focus is None
        assert assignments[1].election is None
        assert assignments[1].exclude_from_meetings is True


class TestProjectModel:
    def test_parse_projects(self):
        data = load_fixture("projects.json")
        projects, _ = parse_response("projects", data)

        assert len(projects) == 2
        assert projects[0].description == "Build GlassFrog CLI"
        assert projects[0].status == "Current"
        assert projects[0].created_at == datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        assert projects[0].archived_at is None
        assert projects[0].private_to_circle is False

    def test_project_waiting_fields(self):
        data = load_fixture("projects.json")
        projects, _ = parse_response("projects", data)

        assert projects[1].waiting_on_who == "Bob"
        assert projects[1].waiting_on_what == "Review"

    def test_project_links(self):
        data = load_fixture("projects.json")
        projects, _ = parse_response("projects", data)

        assert projects[0].links.circle == 2
        assert projects[0].links.person == 50
        assert projects[0].links.role == 12


class TestChecklistItemModel:
    def test_parse_checklist_item(self):
        item = ChecklistItem.model_validate(
            {"id": 1, "description": "Review PRs", "frequency": "Weekly", "global": False}
        )
        assert item.description == "Review PRs"
        assert item.frequency == "Weekly"
        assert item.global_item is False

    def test_global_alias(self):
        item = ChecklistItem.model_validate(
            {"id": 2, "description": "Check metrics", "frequency": "Monthly", "global": True}
        )
        assert item.global_item is True


class TestMetricModel:
    def test_parse_metric(self):
        metric = Metric.model_validate(
            {"id": 1, "description": "Revenue", "frequency": "Weekly", "global": False}
        )
        assert metric.description == "Revenue"
        assert metric.frequency == "Weekly"


class TestActionModel:
    def test_parse_action(self):
        action = Action.model_validate(
            {
                "id": 1,
                "description": "Fix the bug",
                "created_at": "2026-02-20T14:30:00Z",
                "links": {"circle": 1, "person": 50},
            }
        )
        assert action.description == "Fix the bug"
        assert action.links.circle == 1
        assert action.links.person == 50


class TestParseResponse:
    def test_unknown_resource_raises(self):
        with pytest.raises(ValueError, match="Unknown resource"):
            parse_response("unknown", {})

    def test_empty_response(self):
        items, linked = parse_response("circles", {"circles": []})
        assert items == []
        assert linked is None

    def test_minimal_item(self):
        items, _ = parse_response("circles", {"circles": [{"id": 99}]})
        assert len(items) == 1
        assert items[0].id == 99
        assert items[0].name == ""
