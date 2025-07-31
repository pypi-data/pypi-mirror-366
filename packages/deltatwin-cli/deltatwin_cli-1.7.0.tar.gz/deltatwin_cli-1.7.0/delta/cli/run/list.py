import json

import click

from rich.console import Console
from rich.table import Table

from delta.cli.utils import (
    Utils, API,
    RUN_STATUS, RUN_AUTHOR, RUN_DATE, RUN_ID, DELTATWIN
)

DEFAULT_LIMIT = 15


def format_runs(runs: list):
    new_runs = []
    for run in runs:
        new_runs.append(
            {
                'id': run['run_id'],
                'deltatwin': f"{run['dtwin_id']}:{run['dtwin_version']}",
                'generation_date': Utils.format_date(run['generation_date']),
                'author': run['author'],
                'status': run['status']
            }
        )
    return new_runs


@click.command(
    name='list',
    short_help='List run history')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.option(
    '--format-output',
    '-f',
    type=str,
    default=None,
    help='Format of the output (json/text). Default is text')
@click.option(
    '--limit',
    '-l',
    type=int,
    help='Maximum number of run entries returned. '
         f'By default: {DEFAULT_LIMIT}',
    default=DEFAULT_LIMIT)
@click.option(
    '--offset',
    '-o',
    type=click.IntRange(min=0),
    help='Number of runs entries to "skip" default 0 (no offset)',
    default=0)
@click.option(
    '--status',
    '-s',
    type=str,
    help='Filter runs by a status: '
         '"created", "running", "success", "error", "pending"')
@click.option(
    '--twin-name',
    '-t',
    type=str,
    default=None,
    help='Name of the DeltaTwin® to retrieve all run execution')
@click.help_option("--help", "-h")
def list_deltatwin_executions(conf, twin_name, format_output: str,
                              limit: int, offset: int,
                              status: str = None) -> None:
    """List DeltaTwin® component run history.

    By default, only the last 15 runs are displayed.
    Use -l to change the limit.

    TWIN_NAME : Name of the DeltaTwin® component [NOT MANDATORY]
    """
    if twin_name:
        runs = API.list_runs_dt(conf, twin_name, status, limit, offset)
    else:
        runs = API.list_runs(conf, status, limit, offset)

    runs = format_runs(runs)

    if Utils.output_as_json(format_output, runs):
        click.echo(json.dumps(runs, indent=4))
        return

    if isinstance(runs, list):
        if len(runs) == 0:
            click.echo(f"{Utils.log_info} No run found.")
            return
        table = Table()
        table.add_column(RUN_ID, no_wrap=True)
        table.add_column(DELTATWIN)
        table.add_column(RUN_DATE)
        table.add_column(RUN_AUTHOR)
        table.add_column(RUN_STATUS)

        # final_data = data[~np.isnan(data).any(axis=1), :]
        final_data = runs
        for run in final_data:
            status = run['status']
            run_id = run['id']

            color = Utils.get_status_color(status)

            table.add_row(
                str(run_id), run['deltatwin'], run['generation_date'],
                run['author'],
                f"[{color}]{status}[/{color}]")

        console = Console()
        console.print(table)
