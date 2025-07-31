import click

from delta.cli.run.delete import delete_deltatwin_execution
from delta.cli.run.download import download_deltatwin_execution
from delta.cli.run.monitor import monitor
from delta.cli.run.start import start
from delta.cli.run.stop import stop
from delta.cli.run.resume import resume
from delta.cli.run.list import list_deltatwin_executions
from delta.cli.run.get import get_deltatwin_execution
from delta.cli.run.local import run_local


@click.group(
    help='DeltaTwin® run uses models stored into Delta component repository. '
         'The objective of this service is to allow edition and '
         'run of the models stored into the Delta component.'
)
def run():
    pass


# Manage run
run.add_command(start)
run.add_command(delete_deltatwin_execution)
run.add_command(run_local)
# Monitor runs
run.add_command(list_deltatwin_executions)
run.add_command(get_deltatwin_execution)
run.add_command(download_deltatwin_execution)
run.add_command(monitor)
