import click


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


if __name__ == "__main__":
    cli()
