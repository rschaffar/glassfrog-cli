import sys
from importlib.metadata import PackageNotFoundError, version

import click
import httpx

from glassfrog_cli.commands.assignments import assignments
from glassfrog_cli.commands.circles import circles
from glassfrog_cli.commands.meetings import meetings
from glassfrog_cli.commands.people import people
from glassfrog_cli.commands.projects import projects
from glassfrog_cli.commands.roles import roles

try:
    __version__ = version("glassfrog-cli")
except PackageNotFoundError:
    __version__ = "dev"


class GlassFrogCLI(click.Group):
    """Click group with friendly error handling for API errors."""

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 401:
                raise click.ClickException("Authentication failed. Check your API token.") from e
            elif status == 403:
                raise click.ClickException(
                    "Access denied. Your API token may lack required permissions."
                ) from e
            elif status == 404:
                raise click.ClickException("Resource not found.") from e
            elif status == 429:
                raise click.ClickException(
                    "Rate limited by GlassFrog API. Try again shortly."
                ) from e
            else:
                raise click.ClickException(
                    f"API error (HTTP {status}): {e.response.text[:200]}"
                ) from e
        except httpx.ConnectError as e:
            raise click.ClickException(
                "Cannot connect to GlassFrog API. Check your network connection."
            ) from e
        except httpx.TimeoutException as e:
            raise click.ClickException("Request to GlassFrog API timed out. Try again.") from e


@click.group(cls=GlassFrogCLI)
@click.option("--token", "-t", envvar="GLASSFROG_API_TOKEN", help="GlassFrog API token.")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format.",
)
@click.option("--no-color", is_flag=True, help="Disable colored output.")
@click.version_option(version=__version__, prog_name="glassfrog-cli")
@click.pass_context
def cli(ctx, token, output, no_color):
    """GlassFrog CLI - read-only access to the GlassFrog API.

    Browse your organization's circles, roles, people, projects, and
    meeting data from the command line.

    Configure your API token via:

    \b
      --token flag
      GLASSFROG_API_TOKEN environment variable
      ~/.config/glassfrog/config.toml with [auth] token = '...'
    """
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
