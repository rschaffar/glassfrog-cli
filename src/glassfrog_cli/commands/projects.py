"""Project commands."""

import click

from glassfrog_cli.client import GlassFrogClient
from glassfrog_cli.config import resolve_token
from glassfrog_cli.formatters import print_json, projects_table
from glassfrog_cli.models import parse_response


@click.group()
def projects():
    """Browse projects."""
    pass


@projects.command("list")
@click.option("--circle", "circle_id", type=int, default=None, help="Filter by circle ID.")
@click.pass_context
def projects_list(ctx, circle_id):
    """List projects, optionally filtered by circle."""
    token = resolve_token(ctx.obj.get("token"))
    output = ctx.obj.get("output", "table")
    no_color = ctx.obj.get("no_color", False)

    with GlassFrogClient(token=token) as client:
        if circle_id is not None:
            data = client.get_nested("circles", circle_id, "projects")
        else:
            # Fetch projects across all circles
            circle_data = client.get("circles")
            all_projects: list[dict] = []
            seen_ids: set[int] = set()
            for circle in circle_data.get("circles", []):
                cid = circle["id"]
                proj_data = client.get_nested("circles", cid, "projects")
                for p in proj_data.get("projects", []):
                    if p["id"] not in seen_ids:
                        all_projects.append(p)
                        seen_ids.add(p["id"])
            data = {"projects": all_projects}

        items, _ = parse_response("projects", data)

    if output == "json":
        print_json(items, no_color=no_color)
    else:
        projects_table(items, no_color=no_color)
