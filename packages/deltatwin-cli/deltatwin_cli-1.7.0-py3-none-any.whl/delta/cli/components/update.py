import click

from delta.cli.utils import API


@click.command()
@click.argument(
    "dt_name",
    type=str
)
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
    help="Change drive data visibility.",
)
@click.option(
    '--remove-all-topics',
    is_flag=True,
    help="Remove all topics.",
)
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.help_option("--help", "-h")
def update(
        dt_name,
        topics: tuple[str] = None,
        visibility: str = None,
        remove_all_topics: bool = False,
        conf: str = None
) -> None:
    """It allows to update the topics or visibility of a DeltaTwin® component.
    """
    data = {}
    if topics:
        data["topics"] = list(topics)
    if remove_all_topics:
        data['topics'] = []
    if visibility is not None:
        data["visibility"] = visibility

    API.update_dt(conf, dt_name, data)
