import click

from delta.cli.utils import API


@click.command(name="update", short_help="Update metadata of a Drive data")
@click.argument("drive_data_id", type=str)
@click.option(
    "-t", "--topics",
    type=str,
    multiple=True,
    help="list of topics. "
         "This option can be used multiple times.",
)
@click.option(
    "-v", "--visibility",
    nargs=1,
    type=click.Choice(choices=["public", "private"]),
    help='Change drive data visibility. '
    'The public visibility requires to contact the DESP service support',
)
@click.option(
    "--remove-all-topics",
    is_flag=True,
    help="Remove all topics"
)
@click.option("-d", "--description", type=str)
@click.option(
    "--conf", "-c", type=str, default=None, help="Path to the conf file"
)
@click.help_option("--help", "-h")
def update(
        drive_data_id: str,
        topics: tuple[str] = None,
        visibility: str = None,
        remove_all_topics: bool = False,
        description: str = None,
        conf: str = None
) -> None:
    ctx = click.get_current_context()
    group_command = ctx.parent.command
    if group_command.name == "artifact":
        kind = "artifacts"
    elif group_command.name == "resource":
        kind = "resources"
    else:
        raise click.UsageError(
            f"{ctx.command.name} should be called 'artifact' or 'resource'")

    params = {}
    if topics:
        params['Topics'] = topics
    if visibility:
        params['Visibility'] = visibility
    if remove_all_topics:
        params['Topics'] = []
    if description:
        params['Description'] = description

    if len(params.keys()) > 0:
        API.update_drive_data(conf, kind, drive_data_id, params)
    else:
        raise click.UsageError(
            f"{ctx.command.name} should be "
            f"use to update some field of drive data.")
