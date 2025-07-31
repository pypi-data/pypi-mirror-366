import json

import click
from rich.table import Table
from rich.console import Console

from delta.cli.exception import DeltaTwinServiceError
from delta.cli.utils import API, Utils

# TODO Add the option to specify the version of the DeltaTwin to be retrieved
DELTA_TWIN_NAME = "Name"
DELTA_TWIN_DESCRIPTION = "Description"
DELTA_TWIN_TOPICS = "Topics"
DELTA_TWIN_VERSION = "Version"
DELTA_TWIN__AVAILABLE_VERSION = "Available Version"
DELTA_TWIN_OWNER = "Owner"
DELTA_TWIN_PUBLICATION_DATE = "Publication Date"
DELTA_TWIN_LICENSE = "License"
DELTA_TWIN_VISIBILITY = "Visibility"
DELTA_TWIN_INPUTS = "Inputs"
DELTA_TWIN_OUTPUTS = "Outputs"


@click.command('get',
               short_help='Get the information of a DeltaTwin® component.')
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
    help='Format of the output json/text default is text')
@click.argument('dt_name')
@click.option('--version', '-v', type=str, default=None)
@click.help_option("--help", "-h")
def get_deltatwin_info(
        conf,
        format_output,
        dt_name,
        version):
    """Get information about a DeltaTwin® component by
    specifying its name. By default, the command returns information
    for the latest version of the DeltaTwin® component. To get information
    about a previous version, you must specify it with the --version option
    'deltatwin get [deltatwin_name] --version x.y.z'.

    MANDATORY ARGUMENT:

    DT_NAME : DeltaTwin® component name.

    This command will show the DeltaTwin® component information,
    before using this command the user must be logged in.
    """

    param = {}

    if version is not None:
        param = {'version': version}

    version_info = API.get_dt_version(conf, dt_name)
    version = [(e['name'], e['changelog']) for e in version_info]
    dt_info = API.get_dt(conf, dt_name, param)

    if len(dt_info) == 0 and len(version) == 0:
        click.echo(f"{Utils.log_info} No DeltaTwin found.")
        return

    try:
        data = {
            'name': dt_info['name'],
            'description': dt_info['description'],
            'topics': dt_info['topics'],
            'version': dt_info['version'],
            'available_version': version,
            'owner': dt_info['owner'],
            'publication_date':
                next(item["publication_date"] for item in version_info
                     if item["name"] == dt_info['version']),
            'inputs': dt_info.get('inputs', []),
            'outputs': dt_info.get('outputs', []),
            'visibility': dt_info.get('visibility', 'private'),
            'license': dt_info['license']['name']
        }
    except KeyError:
        raise DeltaTwinServiceError(
            f"{Utils.log_error} The response "
            f"does not respect the DeltaTwin format.")

    if format_output is not None and format_output.lower() == 'json':
        click.echo(json.dumps(data, indent=4))
    else:
        # input_table = Table(show_header=True)
        #
        # # Add columns to the inner table
        # input_table.add_column("Name")
        # input_table.add_column("Type")
        # input_table.add_column("Default")
        # input_table.add_column("Description")

        # output_table = Table(show_header=True)
        #
        # # Add columns to the inner table
        # output_table.add_column("Name")
        # output_table.add_column("Type")
        # output_table.add_column("Default")
        # output_table.add_column("Description")

        table = Table()
        table.add_column(DELTA_TWIN_NAME)
        table.add_column(DELTA_TWIN_DESCRIPTION)
        table.add_column(DELTA_TWIN_TOPICS)
        table.add_column(DELTA_TWIN_VERSION)
        table.add_column(DELTA_TWIN__AVAILABLE_VERSION)
        table.add_column(DELTA_TWIN_OWNER)
        table.add_column(DELTA_TWIN_PUBLICATION_DATE)
        table.add_column(DELTA_TWIN_LICENSE)
        table.add_column(DELTA_TWIN_VISIBILITY)
        table.add_column(DELTA_TWIN_INPUTS)
        table.add_column(DELTA_TWIN_OUTPUTS)

        # Create the inner table

        # for input in data['inputs']:
        #     input_table.add_row(
        #         input['name'],
        #         input['type'],
        #         input['default_value'],
        #         input['description'])

        # for output in data['outputs']:
        #     output_table.add_row(
        #         output['name'],
        #         output['type'],
        #         output['default_value'],
        #         output['description'])

        table.add_row(data['name'],
                      data['description'],
                      str(', '.join(data['topics'])),
                      data['version'],
                      "\n".join(f"{version}: {changelog}" if changelog
                                else version for version, changelog in
                                data['available_version']),
                      data['owner'],
                      Utils.format_date(
                          data['publication_date'],
                          '%Y-%m-%dT%H:%M:%S.%fZ'),
                      data['license'],
                      data['visibility'],
                      json.dumps(data['inputs'], indent=2),
                      json.dumps(data['outputs'], indent=2)
                      )

        console = Console()
        console.print(table)
