import os.path
import re

import click

from delta.cli.utils import Utils, API

RUN_STATUS = "Status"
RUN_DATE = "Creation Date"
RUN_ID = "Id"
RUN_AUTHOR = "Author"
RUN_MESSAGE = "Message"


@click.command(
    name='download',
    short_help='Download the output of a run execution')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.option(
    '--file',
    '-F',
    type=str,
    default=None,
    help='Path of the file to save output. By default '
         'it is the basename of output in current directory')
@click.argument('run_id')
@click.argument('output-name')
@click.help_option("--help", "-h")
def download_deltatwin_execution(
        conf, run_id,
        output_name: str, file: str):
    """This command allows to download the outputs of a run execution.

    RUN_ID: the id of the run to retrieve [MANDATORY]


    OUTPUT_NAME: name of the output to download [MANDATORY]

    Example:

    deltatwin run download 5e8f6a4f-3a83-4f41-ae28-99ce831a9861
    out
    """
    resp = API.download_run(conf, run_id, output_name)

    if file is None:
        d = resp.headers['content-disposition']
        file = re.findall("filename=(.+)", d)[0]
    elif os.path.isdir(file):
        d = resp.headers['content-disposition']
        file = os.path.join(file, re.findall("filename=(.+)", d)[0])

    try:
        with open(file, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    except IsADirectoryError:
        click.BadParameter(
            f"{Utils.log_error} The path {file} "
            f"to download the output seems wrong")

    click.echo(f"{Utils.log_info} Output \"{output_name}\" successfully "
               f"downloaded in \"{file}\"")
