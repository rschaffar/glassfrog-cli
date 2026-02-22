"""Circle commands."""

import click

from glassfrog_cli.client import GlassFrogClient
from glassfrog_cli.config import resolve_token
from glassfrog_cli.formatters import circle_detail, circles_table, circles_tree, print_json
from glassfrog_cli.models import parse_response


@click.group()
def circles():
    """Browse circles in the organization."""
    pass


@circles.command("list")
@click.pass_context
def circles_list(ctx):
    """List all circles."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get("circles")
        items, _ = parse_response("circles", data)

    if output == "json":
        print_json(items, no_color=no_color)
    else:
        circles_table(items, no_color=no_color)


@circles.command("show")
@click.argument("circle_id", type=int)
@click.pass_context
def circles_show(ctx, circle_id):
    """Show details for a specific circle."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get("circles", resource_id=circle_id)
        items, linked = parse_response("circles", data)

    if not items:
        raise click.ClickException(f"Circle {circle_id} not found.")

    if output == "json":
        print_json(items[0], no_color=no_color)
    else:
        circle_detail(items[0], linked=linked, no_color=no_color)


@circles.command("tree")
@click.pass_context
def circles_tree_cmd(ctx):
    """Show circle hierarchy as a tree."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        circle_data = client.get("circles")
        role_data = client.get("roles")

        circle_items, _ = parse_response("circles", circle_data)
        role_items, _ = parse_response("roles", role_data)

    if output == "json":
        print_json(circle_items, no_color=no_color)
    else:
        circles_tree(circle_items, role_items, no_color=no_color)
