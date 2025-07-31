import json

import click

from delta.cli.utils import API, Utils

types = {
    's3': 'Drive',
    'harbor': 'DeltaTwin Component',
    'run': 'Runs',
    'cron': 'Schedules',
}


def filter_data(data, input_date):
    filtered_data = []
    for entry in data:
        metric_date = entry['metric_date'].split('T')[0]
        if Utils.date_matches(metric_date, input_date):
            filtered_data.append(entry)
    return filtered_data


@click.command('metrics', short_help='List all the metrics available.')
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
    default='text',
    help='Format of the output json/text default is text')
@click.option(
    '--category',
    '-C',
    required=False,
    default=None,
    help='Type of metrics to be shown (schedules, runs, Deltatwins components '
         'or drive).')
# @click.option(
#     '--date',
#     '-d',
#     required=False,
#     default=None,
#     help='Give a date to retrieve the metric from.')
@click.help_option("--help", "-h")
def metrics_deltatwins(
        conf,
        category,
        format_output,
):
    """
    This command allows the user to check his consumption in the service,
    including the storage used.
    """
    """
    if date is not None:
        metric = API.get_metric_history(conf)

        data = Utils.retrieve_history_s3(filter_data(metric, date))

        if format_output is not None and format_output.lower() == 'text':
            Utils.format_output_text_history_s3(data)
        elif format_output is not None and format_output.lower() == 'json':
            Utils.format_output_json(data)
        return
    """
    metric = API.get_metric(conf)

    metics_names = set([types[t['type']] for t in metric])
    if category is None:
        click.echo(
            f"{Utils.log_info} Here are the available metric type "
            f"to be shown: "
            f"{', '.join(metics_names)}")

    if ((category is None or category.lower() == 'drive')
            and 'Drive' in metics_names):
        data = Utils.retrieve_metric_s3(metric)
        if format_output is not None and format_output.lower() == 'json':
            Utils.format_output_json(data)
        elif format_output is not None and format_output.lower() == 'text':
            click.echo(click.style("Drive:", underline=True, bold=True))
            Utils.format_output_text_s3(data)

    if ((category is None or category.lower() == 'runs')
            and 'Runs' in metics_names):
        data = next(filter(lambda x: x["type"] == "run", metric), None)
        if format_output is not None and format_output.lower() == 'json':
            data['type'] = 'runs'
            Utils.format_output_json(data)
        elif format_output is not None and format_output.lower() == 'text':
            click.echo(click.style("Runs:", underline=True, bold=True))
            Utils.format_output_text_runs(data)

    if ((category is None or category.lower() == 'schedules')
            and 'Schedules' in metics_names):
        data = next(filter(lambda x: x["type"] == "cron", metric), None)
        if format_output is not None and format_output.lower() == 'json':
            data['type'] = 'schedules'
            Utils.format_output_json(data)
        elif format_output is not None and format_output.lower() == 'text':
            click.echo(click.style("Schedules:", underline=True, bold=True))
            Utils.format_output_text_schedules(data)

    if category is None or category.lower() == 'deltatwins':
        datas = Utils.retrieve_metric_harbor(metric)
        if format_output is not None and format_output.lower() == 'graph':
            Utils.format_output_graph_harbor(datas)
        elif format_output is not None and format_output.lower() == 'json':
            Utils.format_output_json_harbor(datas)
        elif format_output is not None and format_output.lower() == 'text':
            click.echo(click.style("DeltaTwin Component:",
                                   underline=True, bold=True))
            Utils.format_output_text_harbor(datas)
