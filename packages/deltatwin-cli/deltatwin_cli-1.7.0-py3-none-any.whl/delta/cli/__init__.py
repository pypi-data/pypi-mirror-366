import click

from delta.cli.components import component
from delta.cli.schedule import schedule
from delta.cli.drive import drive
from delta.cli.run import run

from delta.cli.version import version
from delta.cli.login import delta_login
from delta.cli.metrics import metrics_deltatwins

from delta.cli.utils import Utils


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    short_help="DeltaTwin® is the full environment used to "
    "manage a DeltaTwin® component.",
    help="GAEL Systems is developing a dedicated service, "
    "named ""DeltaTwin® Service"" to facilitate modelling activities "
    "of digital twins. "
    "It aims to offer a collaborative environment for "
    "building and running multi-scale and composable workflows, "
    "leveraging the numerous available data sources, sharing results, "
    "and easing interoperability with other digital twin standards "
    "and system dynamics models. "
    "The DeltaTwin® is the central element for the management of "
    "workflows, resources and their results. "
    "They follow a precise structure folder to ensure they are "
    "handled by the ""DeltaTwin® service"". "
    "The service includes the “drive” element in charge of handling "
    "Delta component storage, their configuration and versioning. "
    "The “run“ element is in charge of the models executions "
    "and their monitoring. "
    "The artifact element aims to store and publish data generated "
    "by DeltaTwin's components with metadata so that it can be reused "
    "and shared."
    "The DeltaTwin® command line allows user to control the management of the "
    "later modules. It allows user to either work online and perform all "
    "actions in a cloud environment or locally using your computer's "
    "resources. "
    "DeltaTwin® service also provides a web application to graphically "
    "manages your DeltaTwins and their execution.",
)
def delta_cli():
    pass


# DeltaTwin API
delta_cli.add_command(version)
delta_cli.add_command(delta_login)
delta_cli.add_command(metrics_deltatwins)

# DeltaTwin Drive API
delta_cli.add_command(drive)

# DeltaTwin Run API
delta_cli.add_command(run)

# DeltaTwin Schedule API
delta_cli.add_command(schedule)

# DeltaTwin Component API
delta_cli.add_command(component)

__all__ = [
    'run',
    'drive',
    'Utils',
]
