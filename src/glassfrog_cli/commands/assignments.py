"""Assignment commands."""

import click

from glassfrog_cli.client import GlassFrogClient
from glassfrog_cli.config import resolve_token
from glassfrog_cli.formatters import assignments_table, print_json
from glassfrog_cli.models import parse_response


@click.group()
def assignments():
    """Browse role assignments."""
    pass


@assignments.command("list")
@click.option("--role", "role_id", type=int, default=None, help="Filter by role ID.")
@click.option("--person", "person_id", type=int, default=None, help="Filter by person ID.")
@click.pass_context
def assignments_list(ctx, role_id, person_id):
    """List assignments, optionally filtered by role or person."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get("assignments")
        items, _ = parse_response("assignments", data)

    if role_id is not None:
        items = [a for a in items if a.links.role == role_id]
    if person_id is not None:
        items = [a for a in items if a.links.person == person_id]

    if output == "json":
        print_json(items, no_color=no_color)
    else:
        assignments_table(items, no_color=no_color)
