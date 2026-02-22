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
    organization_ids: list[int] = Field(default_factory=list)
    circles: list[int] = Field(default_factory=list)


class AssignmentLinks(BaseModel):
    person: int | None = None
    role: int | None = None


class ProjectLinks(BaseModel):
    circle: int | None = None
    person: int | None = None
    role: int | None = None


class ChecklistItemLinks(BaseModel):
    circle: int | None = None
    role: int | None = None


class MetricLinks(BaseModel):
    circle: int | None = None
    role: int | None = None


class ActionLinks(BaseModel):
    circle: int | None = None
    person: int | None = None


# --- Resource models ---


class Circle(BaseModel):
    id: int
    name: str = ""
    short_name: str = ""
    strategy: str | None = None
    organization_id: int | None = None
    links: CircleLinks = Field(default_factory=CircleLinks)


class Role(BaseModel):
    id: int
    name: str = ""
    short_name: str = ""
    is_core: bool = False
    purpose: str | None = None
    elected_until: date | None = None
    organization_id: int | None = None
    links: RoleLinks = Field(default_factory=RoleLinks)


class Person(BaseModel):
    id: int
    name: str = ""
    email: str = ""
    links: PersonLinks = Field(default_factory=PersonLinks)


class Assignment(BaseModel):
    id: int
    focus: str | None = None
    election: date | None = None
    exclude_from_meetings: bool = False
    links: AssignmentLinks = Field(default_factory=AssignmentLinks)


class Project(BaseModel):
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
    links: ProjectLinks = Field(default_factory=ProjectLinks)


class Accountability(BaseModel):
    id: int
    description: str = ""


class Domain(BaseModel):
    id: int
    description: str = ""


class Policy(BaseModel):
    id: int
    title: str = ""
    body: str = ""


class ChecklistItem(BaseModel):
    id: int
    description: str = ""
    frequency: str = ""
    global_item: bool = Field(default=False, alias="global")
    links: ChecklistItemLinks = Field(default_factory=ChecklistItemLinks)

    model_config = {"populate_by_name": True}


class Metric(BaseModel):
    id: int
    description: str = ""
    frequency: str = ""
    global_item: bool = Field(default=False, alias="global")
    links: MetricLinks = Field(default_factory=MetricLinks)

    model_config = {"populate_by_name": True}


class Action(BaseModel):
    id: int
    description: str = ""
    created_at: datetime | None = None
    links: ActionLinks = Field(default_factory=ActionLinks)


# --- Linked data container ---


class LinkedData(BaseModel):
    """Container for 'linked' data in API responses."""

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
        linked = LinkedData.model_validate(data["linked"])

    return items, linked
