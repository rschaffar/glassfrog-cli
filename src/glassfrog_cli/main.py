import click

from glassfrog_cli.commands.assignments import assignments
from glassfrog_cli.commands.circles import circles
from glassfrog_cli.commands.meetings import meetings
from glassfrog_cli.commands.people import people
from glassfrog_cli.commands.projects import projects
from glassfrog_cli.commands.roles import roles


@click.group()
@click.option("--token", "-t", envvar="GLASSFROG_API_TOKEN", help="GlassFrog API token.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format.",
)
@click.option("--no-color", is_flag=True, help="Disable colored output.")
@click.pass_context
def cli(ctx, token, output, no_color):
    """GlassFrog CLI - read-only access to the GlassFrog API."""
    ctx.ensure_object(dict)
    ctx.obj["token"] = token
    ctx.obj["output"] = output
    ctx.obj["no_color"] = no_color


cli.add_command(circles)
cli.add_command(roles)
cli.add_command(people)
cli.add_command(projects)
cli.add_command(assignments)
cli.add_command(meetings)


if __name__ == "__main__":
    cli()
