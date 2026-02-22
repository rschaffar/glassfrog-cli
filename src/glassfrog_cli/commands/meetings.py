"""Meeting-related commands (checklist items, metrics, actions)."""

import click

from glassfrog_cli.client import GlassFrogClient
from glassfrog_cli.config import resolve_token
from glassfrog_cli.formatters import actions_table, checklist_table, metrics_table, print_json
from glassfrog_cli.models import parse_response


@click.group()
def meetings():
    """Browse meeting-related data (checklists, metrics, actions)."""
    pass


@meetings.command("checklist")
@click.option("--circle", "circle_id", type=int, required=True, help="Circle ID.")
@click.pass_context
def meetings_checklist(ctx, circle_id):
    """List checklist items for a circle."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get_nested("circles", circle_id, "checklist_items")
        items, _ = parse_response("checklist_items", data)

    if output == "json":
        print_json(items, no_color=no_color)
    else:
        checklist_table(items, no_color=no_color)


@meetings.command("metrics")
@click.option("--circle", "circle_id", type=int, required=True, help="Circle ID.")
@click.pass_context
def meetings_metrics(ctx, circle_id):
    """List metrics for a circle."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get_nested("circles", circle_id, "metrics")
        items, _ = parse_response("metrics", data)

    if output == "json":
        print_json(items, no_color=no_color)
    else:
        metrics_table(items, no_color=no_color)


@meetings.command("actions")
@click.option("--circle", "circle_id", type=int, default=None, help="Filter by circle ID.")
@click.pass_context
def meetings_actions(ctx, circle_id):
    """List actions (next-actions / todos)."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get("actions")
        items, _ = parse_response("actions", data)

    if circle_id is not None:
        items = [a for a in items if a.links.circle == circle_id]

    if output == "json":
        print_json(items, no_color=no_color)
    else:
        actions_table(items, no_color=no_color)
