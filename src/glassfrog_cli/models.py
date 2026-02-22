"""Pydantic models for GlassFrog API v3 responses."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


# --- Link containers ---


class CircleLinks(BaseModel):
    roles: list[int] = Field(default_factory=list)
    policies: list[int] = Field(default_factory=list)
    domain: list[int] = Field(default_factory=list)
    supported_role: int | None = None


class RoleLinks(BaseModel):
    circle: int | None = None
    supporting_circle: int | None = None
    domains: list[int] = Field(default_factory=list)
    accountabilities: list[int] = Field(default_factory=list)
    people: list[int] = Field(default_factory=list)


class PersonLinks(BaseModel):
    organizations: list[int] = Field(default_factory=list)
    circles: list[int] = Field(default_factory=list)


class AssignmentLinks(BaseModel):
    person: int | None = None
    role: int | None = None


class ProjectLinks(BaseModel):
    circle: int | None = None
    person: int | None = None
    role: int | None = None
    accountability: int | None = None


class ChecklistItemLinks(BaseModel):
    circle: int | None = None
    role: int | None = None


class MetricLinks(BaseModel):
    circle: int | None = None
    role: int | None = None


class ActionLinks(BaseModel):
    circle: int | None = None
    person: int | None = None
    role: int | None = None
    project: int | None = None


# --- Resource models ---


class Circle(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    name: str = ""
    short_name: str = ""
    strategy: str | None = None
    organization_id: int | None = None
    links: CircleLinks = Field(default_factory=CircleLinks)


class Role(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    name: str = ""
    short_name: str = ""
    name_with_circle_for_core_roles: str = ""
    is_core: bool = False
    purpose: str | None = None
    elected_until: date | None = None
    organization_id: int | None = None
    tag_names: list[str] = Field(default_factory=list)
    links: RoleLinks = Field(default_factory=RoleLinks)


class Person(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    name: str = ""
    email: str = ""
    external_id: str | None = None
    tag_names: list[str] = Field(default_factory=list)
    links: PersonLinks = Field(default_factory=PersonLinks)


class Assignment(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    focus: str | None = None
    election: date | None = None
    exclude_from_meetings: bool = False
    links: AssignmentLinks = Field(default_factory=AssignmentLinks)


class Project(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    description: str = ""
    status: str | None = None
    created_at: datetime | None = None
    archived_at: datetime | None = None
    waiting_on_who: str | None = None
    waiting_on_what: str | None = None
    value: str | None = None
    effort: str | None = None
    roi: str | None = None
    private_to_circle: bool = False
    link: str | None = None
    note: str | None = None
    links: ProjectLinks = Field(default_factory=ProjectLinks)


class Accountability(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    description: str = ""


class Domain(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    description: str = ""


class Policy(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    title: str = ""
    body: str = ""


class ChecklistItem(BaseModel):
    model_config = {"populate_by_name": True, "extra": "allow"}

    id: int
    description: str = ""
    frequency: str = ""
    global_item: bool = Field(default=False, alias="global")
    link: str | None = None
    links: ChecklistItemLinks = Field(default_factory=ChecklistItemLinks)


class Metric(BaseModel):
    model_config = {"populate_by_name": True, "extra": "allow"}

    id: int
    description: str = ""
    frequency: str = ""
    global_item: bool = Field(default=False, alias="global")
    link: str | None = None
    links: MetricLinks = Field(default_factory=MetricLinks)


class Action(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    description: str = ""
    status: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | str | None = None
    note: str | None = None
    private_to_circle: bool = False
    trigger: bool = False
    links: ActionLinks = Field(default_factory=ActionLinks)


# --- Linked data container ---


class LinkedData(BaseModel):
    """Container for 'linked' data in API responses."""

    model_config = {"extra": "allow"}

    roles: list[Role] = Field(default_factory=list)
    circles: list[Circle] = Field(default_factory=list)
    people: list[Person] = Field(default_factory=list)
    policies: list[Policy] = Field(default_factory=list)
    domains: list[Domain] = Field(default_factory=list)
    accountabilities: list[Accountability] = Field(default_factory=list)


# --- Response parsing ---


def parse_response(resource_name: str, data: dict[str, Any]) -> tuple[list[Any], LinkedData | None]:
    """Parse a GlassFrog API response into typed models.

    Args:
        resource_name: The top-level resource key (e.g. 'circles', 'roles').
        data: Raw JSON response dict.

    Returns:
        Tuple of (list of parsed resource models, optional LinkedData).
    """
    model_map: dict[str, type[BaseModel]] = {
        "circles": Circle,
        "roles": Role,
        "people": Person,
        "assignments": Assignment,
        "projects": Project,
        "checklist_items": ChecklistItem,
        "metrics": Metric,
        "actions": Action,
    }

    model_cls = model_map.get(resource_name)
    if model_cls is None:
        raise ValueError(f"Unknown resource: {resource_name}")

    items_data = data.get(resource_name, [])
    items = [model_cls.model_validate(item) for item in items_data]

    linked = None
    if "linked" in data:
        # The API sometimes includes empty dicts {} or items without 'id' in
        # linked arrays; filter them out to avoid validation errors
        cleaned_linked = {}
        for key, value in data["linked"].items():
            if isinstance(value, list):
                cleaned_linked[key] = [
                    item for item in value if isinstance(item, dict) and item.get("id")
                ]
            else:
                cleaned_linked[key] = value
        linked = LinkedData.model_validate(cleaned_linked)

    return items, linked
