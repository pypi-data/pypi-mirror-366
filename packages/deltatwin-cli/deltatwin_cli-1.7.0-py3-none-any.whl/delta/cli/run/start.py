import json

import click

from delta.cli.utils import Utils, API


def format_run(run: dict):
    return {
        'run_id': run['run_id'],
        'author': run['author'],
        'dtwin_id': run.get('dtwin_id', None),
        'dtwin_version': run.get('dtwin_version', None),
        'generation_date': Utils.format_date(
            run['generation_date'],
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        'status': run['status'],
        'inputs': run['inputs'],
        'outputs': run['outputs'],
        'message': run.get('message', None)
    }


@click.command(
    'start',
    short_help='Start the DeltaTwin component execution')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.option(
    '--input-file',
    '-i',
    type=str,
    default=None,
    help="Inputs of run in json format, example: /mypath/inputs.json "
         "the json is defined like "
         "{'angle': {'type': 'integer','value': 42},"
         "'image': {'type': 'Data','url': 'https://url_to_data'}}")
@click.option(
    '--format-output',
    '-f',
    type=str,
    default=None,
    help='format of the output json/text default is text')
@click.help_option("--help", "-h")
@click.option('--version', '-v', type=str, default=None,
              help='Specify the version of the DeltaTwin® component, if '
                   'none is given the latest version will be started.'
              )
@click.argument('twin_name')
def start(conf, twin_name, input_file, format_output, version):
    """Start the DeltaTwin® component execution with the expected inputs.

    TWIN_NAME : Name of the DeltaTwin® component [MANDATORY]
    """

    run = API.start_run(conf, twin_name, input_file, version)
    run = format_run(run)
    run['node_status'] = [
        {
            'name': item['name'],
            'status': item['status'],
            'workflow_node_id': item['workflow_node_id']
        }
        for item in API.get_run_nodes(conf, run['run_id'])
    ]
    if Utils.output_as_json(format_output, run):
        click.echo(json.dumps(run, indent=4))
    else:
        Utils.display_run_detailed(run)
