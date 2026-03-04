"""Rich output formatters for GlassFrog CLI."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

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
)


def get_console(no_color: bool = False) -> Console:
    return Console(no_color=no_color)


def print_json(data: Any, no_color: bool = False) -> None:
    """Print data as formatted JSON."""
    console = get_console(no_color)
    if hasattr(data, "model_dump"):
        output = data.model_dump(mode="json")
    elif isinstance(data, list) and data and hasattr(data[0], "model_dump"):
        output = [item.model_dump(mode="json") for item in data]
    else:
        output = data
    console.print_json(json.dumps(output, indent=2, default=str))


# --- Circle formatters ---


def circles_table(circles: list[Circle], no_color: bool = False) -> None:
    console = get_console(no_color)
    table = Table(title="Circles")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Short Name")
    table.add_column("Strategy")
    table.add_column("Roles", justify="right")

    for c in circles:
        table.add_row(
            str(c.id),
            c.name,
            c.short_name,
            c.strategy or "",
            str(len(c.links.roles)),
        )

    console.print(table)


def circle_detail(
    circle: Circle,
    linked: LinkedData | None = None,
    no_color: bool = False,
) -> None:
    console = get_console(no_color)

    console.print(Panel(f"[bold]{circle.name}[/bold]  (ID: {circle.id})", title="Circle"))
    if circle.strategy:
        console.print(f"  Strategy: {circle.strategy}")

    if linked and linked.roles:
        role_map = {r.id: r for r in linked.roles}
        console.print("\n  [bold]Roles:[/bold]")
        for role_id in circle.links.roles:
            role = role_map.get(role_id)
            if role:
                core = " [dim](core)[/dim]" if role.is_core else ""
                console.print(f"    - {role.name}{core}")
            else:
                console.print(f"    - Role #{role_id}")

    if linked and linked.policies:
        policy_map = {p.id: p for p in linked.policies}
        console.print("\n  [bold]Policies:[/bold]")
        for pid in circle.links.policies:
            policy = policy_map.get(pid)
            if policy:
                console.print(f"    - {policy.title}")

    if linked and linked.domains:
        domain_map = {d.id: d for d in linked.domains}
        console.print("\n  [bold]Domains:[/bold]")
        for did in circle.links.domain:
            domain = domain_map.get(did)
            if domain:
                console.print(f"    - {domain.description}")


def circles_tree(
    circles: list[Circle],
    roles: list[Role],
    no_color: bool = False,
) -> None:
    """Build a tree showing circles with their sub-circles and roles."""
    console = get_console(no_color)

    # Build a map: role_id -> Role and circle_id -> Circle
    role_map = {r.id: r for r in roles}
    circle_map = {c.id: c for c in circles}

    # Find circles that are supporting circles of a role
    # A circle's supported_role links it to its parent circle
    parent_map: dict[int, int] = {}  # child_circle_id -> parent_circle_id
    for c in circles:
        if c.links.supported_role:
            role = role_map.get(c.links.supported_role)
            if role and role.links.circle and role.links.circle != c.id:
                parent_map[c.id] = role.links.circle

    # Find root circles (no parent)
    root_ids = [c.id for c in circles if c.id not in parent_map]

    tree = Tree("[bold]Organization[/bold]")

    def add_circle_branch(parent_tree: Tree, circle_id: int) -> None:
        circle = circle_map.get(circle_id)
        if not circle:
            return

        branch = parent_tree.add(f"[bold cyan]{circle.name}[/bold cyan]  [dim]({circle.id})[/dim]")

        # Add roles in this circle
        for role_id in circle.links.roles:
            role = role_map.get(role_id)
            if role:
                # Skip roles that are supported by a sub-circle (they'll appear as circles)
                if role.links.supporting_circle:
                    continue
                core_tag = " [dim](core)[/dim]" if role.is_core else ""
                branch.add(f"{role.name}{core_tag}")

        # Add sub-circles
        child_ids = [cid for cid, pid in parent_map.items() if pid == circle_id]
        for child_id in child_ids:
            add_circle_branch(branch, child_id)

    for root_id in root_ids:
        add_circle_branch(tree, root_id)

    console.print(tree)


# --- Role formatters ---


def roles_table(roles: list[Role], no_color: bool = False) -> None:
    console = get_console(no_color)
    table = Table(title="Roles")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Purpose")
    table.add_column("Core", justify="center")
    table.add_column("Circle", justify="right")
    table.add_column("People", justify="right")

    for r in roles:
        table.add_row(
            str(r.id),
            r.name,
            (r.purpose or "")[:60],
            "Y" if r.is_core else "",
            str(r.links.circle or ""),
            str(len(r.links.people)),
        )

    console.print(table)


def role_detail(
    role: Role,
    linked: LinkedData | None = None,
    no_color: bool = False,
) -> None:
    console = get_console(no_color)

    core_tag = " (core)" if role.is_core else ""
    console.print(Panel(f"[bold]{role.name}[/bold]{core_tag}  (ID: {role.id})", title="Role"))

    if role.purpose:
        console.print(f"  Purpose: {role.purpose}")
    if role.elected_until:
        console.print(f"  Elected until: {role.elected_until}")
    if role.links.circle:
        console.print(f"  Circle: #{role.links.circle}")

    if linked and linked.accountabilities:
        acc_map = {a.id: a for a in linked.accountabilities}
        console.print("\n  [bold]Accountabilities:[/bold]")
        for aid in role.links.accountabilities:
            acc = acc_map.get(aid)
            if acc:
                console.print(f"    - {acc.description}")

    if linked and linked.domains:
        domain_map = {d.id: d for d in linked.domains}
        console.print("\n  [bold]Domains:[/bold]")
        for did in role.links.domains:
            domain = domain_map.get(did)
            if domain:
                console.print(f"    - {domain.description}")

    if linked and linked.people:
        person_map = {p.id: p for p in linked.people}
        console.print("\n  [bold]People:[/bold]")
        for pid in role.links.people:
            person = person_map.get(pid)
            if person:
                console.print(f"    - {person.name} ({person.email})")


# --- People formatters ---


def people_table(people: list[Person], no_color: bool = False) -> None:
    console = get_console(no_color)
    table = Table(title="People")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Email")
    table.add_column("Circles", justify="right")

    for p in people:
        table.add_row(
            str(p.id),
            p.name,
            p.email,
            str(len(p.links.circles)),
        )

    console.print(table)


def person_detail(person: Person, no_color: bool = False) -> None:
    console = get_console(no_color)

    console.print(Panel(f"[bold]{person.name}[/bold]  (ID: {person.id})", title="Person"))
    console.print(f"  Email: {person.email}")
    if person.links.circles:
        console.print(f"  Circles: {', '.join(str(c) for c in person.links.circles)}")


# --- Project formatters ---


def projects_table(projects: list[Project], no_color: bool = False) -> None:
    console = get_console(no_color)
    table = Table(title="Projects")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Description", style="bold")
    table.add_column("Status")
    table.add_column("Circle", justify="right")
    table.add_column("Person", justify="right")
    table.add_column("Value")

    for p in projects:
        table.add_row(
            str(p.id),
            (p.description or "")[:50],
            p.status or "",
            str(p.links.circle or ""),
            str(p.links.person or ""),
            p.value or "",
        )

    console.print(table)


# --- Assignment formatters ---


def assignments_table(assignments: list[Assignment], no_color: bool = False) -> None:
    console = get_console(no_color)
    table = Table(title="Assignments")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Role", justify="right")
    table.add_column("Person", justify="right")
    table.add_column("Focus")
    table.add_column("Election")
    table.add_column("Excl. Meetings", justify="center")

    for a in assignments:
        table.add_row(
            str(a.id),
            str(a.links.role or ""),
            str(a.links.person or ""),
            a.focus or "",
            str(a.election) if a.election else "",
            "Y" if a.exclude_from_meetings else "",
        )

    console.print(table)


# --- Meeting-related formatters ---


def checklist_table(items: list[ChecklistItem], no_color: bool = False) -> None:
    console = get_console(no_color)
    table = Table(title="Checklist Items")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Description", style="bold")
    table.add_column("Frequency")
    table.add_column("Global", justify="center")
    table.add_column("Role", justify="right")

    for item in items:
        table.add_row(
            str(item.id),
            item.description,
            item.frequency,
            "Y" if item.global_item else "",
            str(item.links.role or ""),
        )

    console.print(table)


def metrics_table(metrics: list[Metric], no_color: bool = False) -> None:
    console = get_console(no_color)
    table = Table(title="Metrics")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Description", style="bold")
    table.add_column("Frequency")
    table.add_column("Global", justify="center")
    table.add_column("Role", justify="right")

    for m in metrics:
        table.add_row(
            str(m.id),
            m.description,
            m.frequency,
            "Y" if m.global_item else "",
            str(m.links.role or ""),
        )

    console.print(table)


def actions_table(actions: list[Action], no_color: bool = False) -> None:
    console = get_console(no_color)
    table = Table(title="Actions")
    table.add_column("ID", style="dim", justify="right")
    table.add_column("Description", style="bold")
    table.add_column("Circle", justify="right")
    table.add_column("Person", justify="right")
    table.add_column("Created")

    for a in actions:
        table.add_row(
            str(a.id),
            a.description,
            str(a.links.circle or ""),
            str(a.links.person or ""),
            str(a.created_at.date()) if a.created_at else "",
        )

    console.print(table)
