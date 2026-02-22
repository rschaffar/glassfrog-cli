"""Role commands."""

import click

from glassfrog_cli.client import GlassFrogClient
from glassfrog_cli.config import resolve_token
from glassfrog_cli.formatters import print_json, role_detail, roles_table
from glassfrog_cli.models import parse_response


@click.group()
def roles():
    """Browse roles in the organization."""
    pass


@roles.command("list")
@click.option("--circle", "circle_id", type=int, default=None, help="Filter by circle ID.")
@click.pass_context
def roles_list(ctx, circle_id):
    """List all roles, optionally filtered by circle."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get("roles")
        items, _ = parse_response("roles", data)

    if circle_id is not None:
        items = [r for r in items if r.links.circle == circle_id]

    if output == "json":
        print_json(items, no_color=no_color)
    else:
        roles_table(items, no_color=no_color)


@roles.command("show")
@click.argument("role_id", type=int)
@click.pass_context
def roles_show(ctx, role_id):
    """Show details for a specific role."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get("roles", resource_id=role_id)
        items, linked = parse_response("roles", data)

    if not items:
        raise click.ClickException(f"Role {role_id} not found.")

    if output == "json":
        print_json(items[0], no_color=no_color)
    else:
        role_detail(items[0], linked=linked, no_color=no_color)
