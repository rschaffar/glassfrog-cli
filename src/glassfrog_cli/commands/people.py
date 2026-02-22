"""People commands."""

import click

from glassfrog_cli.client import GlassFrogClient
from glassfrog_cli.config import resolve_token
from glassfrog_cli.formatters import people_table, person_detail, print_json
from glassfrog_cli.models import parse_response


@click.group()
def people():
    """Browse people in the organization."""
    pass


@people.command("list")
@click.pass_context
def people_list(ctx):
    """List all people."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get("people")
        items, _ = parse_response("people", data)

    if output == "json":
        print_json(items, no_color=no_color)
    else:
        people_table(items, no_color=no_color)


@people.command("show")
@click.argument("person_id", type=int)
@click.pass_context
def people_show(ctx, person_id):
    """Show details for a specific person."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        data = client.get("people", resource_id=person_id)
        items, _ = parse_response("people", data)

    if not items:
        raise click.ClickException(f"Person {person_id} not found.")

    if output == "json":
        print_json(items[0], no_color=no_color)
    else:
        person_detail(items[0], no_color=no_color)
