import configparser
import hashlib
import json
import mimetypes
import os
import re
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Callable, Literal, Union

import click
import plotext as plt
import requests
import rich.box as box
from humanize import naturalsize, precisedelta
from packaging.version import InvalidVersion, parse
from requests.exceptions import ConnectionError, InvalidSchema, JSONDecodeError
from rich.console import Console
from rich.padding import Padding
from rich.table import Table

from delta.cli.exception import (
    DeltaTwinResourceNotFound,
    DeltaTwinServiceError,
    DeltaTwinServiceNotFound,
    DeltaTwinUnauthorized,
)

RUN_STATUS = "Status"
RUN_DATE = "Creation Date"
RUN_DATE_END = "Ending Date"
DELTATWIN = "DeltaTwin"
RUN_ID = "Id"
RUN_AUTHOR = "Author"
RUN_MESSAGE = "Message"


class Utils:
    log_info = click.style('INFO:', fg='green')
    log_error = click.style('ERROR:', fg='red')

    @staticmethod
    def is_valid_url(url: str):
        pattern = r'^(http|https):\/\/([\w.-]+)(\.[\w.-]+)+([\/\w\.-]*)*\/?$'
        return bool(re.match(pattern, url))

    @staticmethod
    def retrieve_conf(conf):
        if conf is None:
            conf = os.path.expanduser('~') + '/.deltatwin/conf.ini'

        return conf

    @staticmethod
    def retrieve_token(conf):
        try:
            token = Utils.get_token(conf)
        except KeyError:
            API.refresh_token(conf)
            token = Utils.get_token(conf)
        return token

    @staticmethod
    def get_error_msg(response):
        try:
            msg = response.json()
        except JSONDecodeError:
            return None
        if 'error' in msg:
            if 'message' in msg['error']:
                msg = msg['error']['message']
            else:
                msg = msg['error']
        elif 'detail' in msg:
            msg = msg['detail']
        elif 'message' in msg:
            msg = msg['message']
        return msg

    @staticmethod
    def check_status(response):
        if 400 > response.status_code >= 300:
            msg = Utils.get_error_msg(response)
            if msg is not None:
                message = (f"{response.reason} at "
                           f"{response.request.url}, {msg}.")
            else:
                message = (f"{response.reason} at "
                           f"{response.request.url}")
            raise DeltaTwinResourceNotFound(message=message)
        if 500 > response.status_code >= 400:
            msg = Utils.get_error_msg(response)
            if msg is not None:
                message = (f"{response.reason} at "
                           f"{response.request.url}, {msg}.")
            else:
                message = f"{response.reason} at {response.request.url}"
            raise DeltaTwinUnauthorized(message=message)
        if response.status_code >= 500:
            message = f"{response.reason} at {response.request.url}."
            raise DeltaTwinServiceError(message=message)

    @staticmethod
    def output_as_json(output_format, data):
        if output_format is not None and output_format.lower() == 'json':
            try:
                json.loads(json.dumps(data))
            except ValueError:
                return False
            return True
        return False

    @staticmethod
    def read_config(path: str, context: str = None):
        cfg = configparser.ConfigParser()

        if os.path.isfile(path):
            cfg.read(path)

        if context is not None:
            return dict(cfg[context])
        return cfg

    @staticmethod
    def save_config(path: str, context: str, config: dict):
        cfg = configparser.ConfigParser()
        cfg[context] = config

        with open(path, 'w') as configfile:  # save
            cfg.write(configfile)

    @staticmethod
    def get_token(path: str):
        return Utils.read_config(path, 'SERVICES')['token']

    @staticmethod
    def get_service(path: str):
        url = Utils.read_config(path, 'SERVICES')['api']
        return url[:-1] if url.endswith('/') else url

    @staticmethod
    def datetime_from_utc_to_local(utc_datetime):
        now_timestamp = time.time()
        offset = (datetime.fromtimestamp(now_timestamp)
                  - datetime.utcfromtimestamp(now_timestamp))
        return utc_datetime + offset

    @staticmethod
    def format_date(date: Union[str, datetime],
                    format: str = "%Y-%m-%dT%H:%M:%SZ"
                    ) -> str:
        # Parse la chaîne de date dans un objet datetime
        if type(date) is str:
            date = Utils.datetime_from_utc_to_local(datetime.strptime(
                date, format)
            )
        if date is None:
            return date

        # Formater l'objet datetime dans le format souhaité
        return date.strftime("%b %d, %Y, %I:%M:%S %p")

    @staticmethod
    def retrieve_metric_s3(metrics) -> dict:
        data = {}
        for metric in metrics:
            if metric['type'] == 's3':
                data['type'] = 'drive'
                data['storage_used'] = metric['occupied_size']
                data['max_size'] = metric['max_size']
                data['total_objects'] = metric['total_objects']
                data['last_metric_update'] = metric['metric_date']
                return data

        data['storage_used'] = 0
        data['total_objects'] = 0
        data['max_size'] = 0
        data['last_metric_update'] = Utils.format_date(datetime.now())
        return data

    @staticmethod
    def retrieve_history_s3(metrics) -> list:
        data = []
        for metric in metrics:
            d = {}
            if metric['type'] == 's3':
                d['category'] = 'drive'
                d['storage_used'] = metric['occupied_size']
                d['total_objects'] = metric['total_objects']
                d['last_metric_update'] = Utils.format_date(
                    metric['metric_date'])
                data.append(d)
        if len(data) == 0:
            data.append(
                {
                    'storage_used': 0,
                    'total_objects': 0,
                    'last_metric_update': Utils.format_date(datetime.now())
                }
            )
        return data

    @staticmethod
    def format_output_json(data):
        click.echo(json.dumps(data, indent=4))

    @staticmethod
    def format_output_text_s3(data):
        if isinstance(data, list):
            if len(data) == 0:
                click.echo(f"{Utils.log_info} No artifact found")

        table = Table()
        table.add_column('Storage used')
        table.add_column('Number of Elements')
        table.add_column('Last metric update')

        rows = (f"{str(naturalsize(data['storage_used'], True))}/"
                f"{str(naturalsize(data['max_size'], True))}",
                str(data['total_objects']),
                str(Utils.format_date(
                    data['last_metric_update']))
                )
        table.add_row(*rows)
        console = Console()
        console.print(table)

    @staticmethod
    def format_output_text_runs(data):
        if isinstance(data, list):
            if len(data) == 0:
                click.echo(f"{Utils.log_info} No artifact found")

        table = Table()
        table.add_column('Number of runs')
        table.add_column('Runs quotas')
        table.add_column('Pending runs')
        table.add_column('Max parallel runs')
        table.add_column('Execution time')
        exec_time = timedelta(seconds=data['execution_time'])

        rows = (str(data['number_of_runs']),
                str(data['max_run']),
                str(data['number_of_runs_parallel']),
                str(data['max_run_parallel']),
                str(precisedelta(exec_time, suppress=["days"], format="%0.4f"))
                )
        table.add_row(*rows)
        console = Console()
        console.print(table)

    @staticmethod
    def format_output_text_schedules(data):
        if isinstance(data, list):
            if len(data) == 0:
                click.echo(f"{Utils.log_info} No artifact found")

        table = Table()
        table.add_column('Number of schedules')
        table.add_column('Schedules quotas')
        table.add_column('Last metric update')

        rows = (str(data['cron_number']),
                str(data['max_cron']),
                str(Utils.format_date(
                    data['metric_date'],
                    '%Y-%m-%dT%H:%M:%SZ'))
                )
        table.add_row(*rows)
        console = Console()
        console.print(table)

    @staticmethod
    def format_output_text_history_s3(data):
        if isinstance(data, list):
            if len(data) == 0:
                click.echo(f"{Utils.log_info} No artifact found")

        table = Table()
        table.add_column('Storage used')
        table.add_column('Number of Elements')
        table.add_column('Last metric update (UTC)')

        for d in data:
            rows = (str(naturalsize(d['storage_used'])),
                    str(d['total_objects']),
                    str(d['last_metric_update'])
                    )
            table.add_row(*rows)
        console = Console()
        console.print(table)

    @staticmethod
    def prepare_graph_harbor(datas):
        name = []
        size = []
        for data in datas:
            name.append(data['deltatwin_name'])
            size.append(int(data['size']))
        return name, size

    @staticmethod
    def retrieve_metric_harbor(metrics) -> any:
        datas = []
        total = 0
        for metric in metrics:
            if metric['type'] == 'harbor':
                data = {
                    'deltatwin_name': metric['project_name'],
                    'size': metric['occupied_size'],
                    'last_metric_update': Utils.format_date(
                        metric['metric_date'])
                }
                datas.append(data)
                total += metric['occupied_size']
        return {'total_size': total,
                'type': 'deltatwin component',
                'details': datas}

    @staticmethod
    def format_output_json_harbor(datas):
        click.echo(json.dumps(datas, indent=4))

    @staticmethod
    def format_output_graph_harbor(datas):
        console = Console(highlight=False)
        twin_name, twine_size = Utils.prepare_graph_harbor(datas)
        Utils.display_line(
            console,
            'Total occupied space',
            f" {naturalsize(datas['Total_size'])}")

        plt.simple_bar(
            twin_name, twine_size,
            width=100,
            title='Occupied space by Deltatwin (Bytes)')
        plt.show()

    @staticmethod
    def format_output_text_harbor(datas):
        console = Console(highlight=False)
        Utils.display_line(
            console,
            'Total occupied space',
            f" {naturalsize(datas['total_size'])}")

        if len(datas['details']) > 0:
            table = Table()
            table.add_column('DeltaTwin Name')
            table.add_column('Size')
            table.add_column('Last metric update (UTC)')

            for data in datas['details']:
                rows = (str(data['deltatwin_name']),
                        str(naturalsize(data['size'])),
                        str(data['last_metric_update'])
                        )
                table.add_row(*rows)
            console = Console()
            console.print(table)

    @staticmethod
    def display_line(console, name, value):
        console.print(name, f"[bold]{value}[/bold]", sep=":")

    @staticmethod
    def display_run_detailed(run):
        console = Console(highlight=False)

        Utils.display_line(console, RUN_ID, run.get("run_id"))
        Utils.display_line(console, RUN_AUTHOR, run.get("author"))
        Utils.display_line(console, DELTATWIN,
                           f"{run.get('dtwin_id')}:{run.get('dtwin_version')}")
        Utils.display_line(console, RUN_DATE, run.get("generation_date"))
        Utils.display_line(console, RUN_DATE_END, run.get("end_at"))
        Utils.display_run_short(run)

    @staticmethod
    def display_run_short(run):
        status = run.get("status")
        color = Utils.get_status_color(status)
        console = Console(highlight=False)

        Utils.display_line(console, RUN_STATUS, f"[{color}]{status}[/{color}]")
        if status == "error":
            Utils.display_line(console, RUN_MESSAGE, run.get("message"))
        Utils.display_table_parameter(console, "Input", run.get("inputs"))

        Utils.display_table_parameter(console, "Output", run.get("outputs"))

    @staticmethod
    def display_run_node_status(run):
        console = Console(highlight=False)
        table = Table(show_edge=True)
        table.add_column("Node id")
        table.add_column("Node number")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Status")
        if run is not None:
            for data in run:
                table.add_row(
                    data['node_id'],
                    data['node_number'],
                    data['name'],
                    data['type'],
                    f"[{Utils.get_status_color(data['status'])}]"
                    f"{data['status']}[/"
                    f"{Utils.get_status_color(data['status'])}]"
                )
        console.print(Padding(table))

    @staticmethod
    def get_status_color(status):
        color = "white"
        match status:
            case "success":
                color = "green"
            case "error":
                color = "red"
            case "running":
                color = "blue"
            case "cancelled":
                color = "magenta"
        return color

    @staticmethod
    def display_table_schedule_parameter(console, prefix, datas):
        console.print(f"{prefix}s:")

        table = Table(show_edge=False, box=box.ASCII)
        table.add_column(prefix + " name")
        table.add_column("Type")
        table.add_column("Value/Basename")
        if datas is not None:
            for data in datas:
                value = ""
                if ("value" in datas[data].keys() and
                        datas[data].get("value") is not None):
                    value = datas[data].get("value")
                elif (
                        "basename" in datas[data].keys() and
                        datas[data].get("basename") is not None
                ):
                    value = datas[data].get("basename")
                elif "url" in datas[data].keys():
                    value = datas[data].get("url")
                table.add_row(
                    data,
                    datas[data].get("param_type"),
                    str(value)
                )
        console.print(Padding(table, (0, 4)))

    @staticmethod
    def display_table_parameter(console, prefix, datas):
        console.print(f"{prefix}s:")

        table = Table(show_edge=False, box=box.ASCII)
        table.add_column(prefix + " name")
        table.add_column("Type")
        table.add_column("Value/Basename")
        if datas is not None:
            for data in datas:
                value = ""
                if ("value" in data.keys() and
                        data.get("value") is not None):
                    value = data.get("value")
                elif (
                        "basename" in data.keys() and
                        data.get("basename") is not None
                ):
                    value = data.get("basename")
                elif "url" in data.keys():
                    value = data.get("url")
                table.add_row(
                    data.get("name"),
                    data.get("param_type"),
                    str(value)
                )
        console.print(Padding(table, (0, 4)))

    @staticmethod
    def filter_artefacts(data, author=None):
        results = []
        for artefact in data:
            if author is None or artefact['owner'] == author:
                results.append(artefact)
        return results

    @staticmethod
    def filter_dts(data, owner=None):
        results = []
        for dt in data:
            if owner is None or dt['owner'] == owner:
                results.append(dt)
        return results

    @staticmethod
    def date_matches(date_to_check: str, input_date: str) -> bool:
        try:
            date_to_check_dt = datetime.strptime(date_to_check, "%Y-%m-%d")

            if len(input_date) == 4:
                year = int(input_date)
                return date_to_check_dt.year == year

            elif len(input_date) == 7:
                year, month = map(int, input_date.split('-'))
                return (date_to_check_dt.year == year and
                        date_to_check_dt.month == month)

            elif len(input_date) == 10:
                date_input_dt = datetime.strptime(input_date, "%Y-%m-%d")
                return date_to_check_dt == date_input_dt

            else:
                return False

        except ValueError:
            return False

    @staticmethod
    def prepare_dt(dts):
        return [
            {
                'name': dt['name'],
                'short_description': dt.get(
                    'short_description',
                    'No short descritpion provided to see '
                    'description please use [deltatwin components get].'
                ),
                'publication_date': dt['publication_date'],
                'license': dt['license']['name'],
                'topics': dt['topics'],
                'owner': dt['owner'],
                'visibility': dt['visibility']
            } for dt in dts
        ]


class API:
    @staticmethod
    def log_to_api(api: str, username: str, password: str):
        myobj = {
            'username': username,
            'password': password

        }

        try:
            resp = requests.post(
                url=f"{api}/connect",
                json=myobj
            )
        except (ConnectionError, InvalidSchema):
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {api}"
            )

        Utils.check_status(resp)

        return json.loads(resp.text)

    @staticmethod
    def query_token(api: str, token: str):
        myobj = {
            'refresh_token': token
        }

        try:
            resp = requests.post(
                url=f"{api}/refresh",
                json=myobj
            )

        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {api}"
            )
        Utils.check_status(resp)

        data = resp.json()
        return data

    # Decorator to check if token still valid
    @staticmethod
    def check_token(func: Callable[[str, tuple, dict[str, Any]], Any]) \
            -> Callable[[str, tuple, dict[str, Any]], Any]:
        def check_token_decorator(conf, *args, **kwargs):
            conf = Utils.retrieve_conf(conf)
            try:
                config = Utils.read_config(conf, 'SERVICES')

                if 'token' in config:
                    token_creation_date = datetime.strptime(
                        config['token_created'],
                        '%Y-%m-%d %H:%M:%S'
                    )
                    now = datetime.now()

                    if (
                            (now - token_creation_date).total_seconds() >
                            float(config['expires_in'])
                    ):
                        API.refresh_token(conf)
                return func(conf, *args, **kwargs)
            except KeyError:
                raise click.UsageError(
                    f"No config find please use "
                    "deltatwin login before using this command."
                )

        return check_token_decorator

    @staticmethod
    def refresh_token(conf: str):
        created = datetime.now()
        try:
            config = Utils.read_config(conf, 'SERVICES')

            # Check if refresh token in conf
            if 'refresh_token' in config:
                date = datetime.strptime(
                    config['token_created'], '%Y-%m-%d %H:%M:%S')
                now = datetime.now()

                # check if refresh token is still valid
                if (now - date).total_seconds() < float(
                        config['refresh_expires_in']):
                    data = API.query_token(config['api'],
                                           config['refresh_token'])
                else:
                    data = API.log_to_api(
                        config['api'],
                        config['username'],
                        config['password'])
                    click.echo(
                        f'{Utils.log_info} Refresh token '
                        f'expired log again to the service')
            else:
                data = API.log_to_api(
                    config['api'],
                    config["username"],
                    config["password"]
                )

                click.echo(f"{Utils.log_info}"
                           f" Log to the service {config['api']}")

        except KeyError:
            raise click.UsageError(
                f"No config find please use "
                f"deltatwin login before using this command.")

        created = created.strftime("%Y-%m-%d %H:%M:%S")
        config['token_created'] = created
        config['token'] = data['access_token']
        config['expires_in'] = data["expires_in"]
        config['refresh_expires_in'] = data["refresh_expires_in"]
        config['refresh_token'] = data["refresh_token"]

        Utils.save_config(conf, 'SERVICES', config)

    @staticmethod
    def force_login(conf: str):
        created = datetime.now()

        config = Utils.read_config(conf, 'SERVICES')

        data = API.log_to_api(
            config['api'],
            config["username"],
            config["password"]
        )

        created = created.strftime("%Y-%m-%d %H:%M:%S")
        config['token_created'] = created
        config['token'] = data['access_token']
        config['expires_in'] = data["expires_in"]
        config['refresh_expires_in'] = data["refresh_expires_in"]
        config['refresh_token'] = data["refresh_token"]

        Utils.save_config(conf, 'SERVICES', config)

    @check_token
    @staticmethod
    def get_harbor_url(conf: str):

        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/harbor/registry'
        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()['harbor_url']

    @check_token
    @staticmethod
    def allowed_to_publish(conf: str, visibility: str,
                           version: str, name: str, topic):

        topics = []
        for tag_name in topic:
            topics.append(tag_name)

        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/deltatwins/allowed_to_publish'

        try:
            r = requests.post(
                url,
                headers={'Authorization': f'Bearer {token}'},
                json={
                    "visibility": visibility,
                    "version": version,
                    "name": name,
                    "topics": topics
                })
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        Utils.check_status(r)

        return True

    @check_token
    @staticmethod
    def get_twin_id_by_run_id(conf: str, run_id: str):

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/runs/{run_id}'

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        Utils.check_status(r)

        return r.json()['dtwin_id']

    @check_token
    @staticmethod
    def create_artifact(conf, run_id, output_name, name, description,
                        visibility, topics):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        twin_id = API.get_twin_id_by_run_id(conf, run_id)

        url = (f'{Utils.get_service(conf)}/deltatwins/'
               f'{twin_id}/runs/{run_id}/{output_name}/artifact')
        try:
            r = requests.post(
                url,
                headers={'Authorization': f'Bearer {token}'},
                json={"name": name, "description": description,
                      'visibility': visibility,
                      "topics": str(topics)}
            )
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)
        return r.status_code

    @check_token
    @staticmethod
    def download_artifact(conf, artifact_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = (f'{Utils.get_service(conf)}/artifacts/{artifact_id}/download')
        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r

    @check_token
    @staticmethod
    def list_artifact(conf, visibility, dtwin_name):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)
        params = {}
        if visibility is not None:
            params["visibility"] = visibility

        if dtwin_name is not None:
            params["dtwin_name"] = dtwin_name

        url = f'{Utils.get_service(conf)}/artifacts'

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'}, params=params)
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def download_run(conf, run_id, output_name):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        twin_id = API.get_twin_id_by_run_id(conf, run_id)

        url = (f'{Utils.get_service(conf)}/deltatwins/'
               f'{twin_id}/runs/{run_id}/{output_name}/download')

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        Utils.check_status(r)

        return r

    @check_token
    @staticmethod
    def get_run(conf, run_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)
        url = f'{Utils.get_service(conf)}/runs/{run_id}'

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def get_run_nodes(conf, run_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)
        url = f'{Utils.get_service(conf)}/run/{run_id}/nodes'

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def get_run_nodes_logs(conf, run_id, node_id, error=False):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)
        url = f'{Utils.get_service(conf)}/runs/{run_id}/nodes/{node_id}/stdout'
        if error:
            url = (f'{Utils.get_service(conf)}/runs/{run_id}'
                   f'/nodes/{node_id}/stderr')

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.content  # if r.content else b"No logs available."

    @check_token
    @staticmethod
    def delete_run(conf, run_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)
        url = f'{Utils.get_service(conf)}/runs/{run_id}'

        try:
            r = requests.delete(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

    @check_token
    @staticmethod
    def list_runs(conf, status, limit, offset):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/runs'

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'},
                params={"status": status,
                        "limit": limit, "offset": offset})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def list_runs_dt(conf, twin_name, status, limit, offset):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/deltatwins/{twin_name}/runs'

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'},
                params={"status": status,
                        "limit": limit, "offset": offset})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def start_run(conf, twin_name, input_file, version):
        conf = Utils.retrieve_conf(conf)
        params = {}

        if version is not None:
            params["version"] = version

        token = Utils.retrieve_token(conf)
        inputs_json = {}

        if input_file is not None:
            file_inputs = open(input_file)
            inputs_json = json.load(file_inputs)

        url = f'{Utils.get_service(conf)}/deltatwins/{twin_name}/runs'
        try:
            r = requests.post(
                url,
                headers={'Authorization': f'Bearer {token}'}, json=inputs_json,
                params=params)
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def start_scheduled_run(conf, twin_name, input_file,
                            type, schedule, name, version):
        conf = Utils.retrieve_conf(conf)
        token = Utils.retrieve_token(conf)
        inputs_json = []
        params = {}

        if version is not None:
            params["version"] = version

        if input_file is not None:
            file_inputs = open(input_file)
            inputs_json = json.load(file_inputs)

        url = f'{Utils.get_service(conf)}/deltatwins/{twin_name}/schedule'
        data = {
            "type": type,
            "schedule_name": name,
            "schedule": schedule,
            "inputs": inputs_json
        }
        try:
            r = requests.post(
                url,
                headers={'Authorization': f'Bearer {token}'}, json=data,
                params=params)
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def list_scheduled_run(conf, twin_name, author):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)
        params = {}
        if author is not None:
            params['owner'] = author
        if twin_name is not None:
            params['deltatwin_name'] = twin_name

        url = f'{Utils.get_service(conf)}/schedules'

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'}, params=params)
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def delete_scheduled_run(conf, schedule_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/schedules/{schedule_id}'

        try:
            r = requests.delete(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

    @check_token
    @staticmethod
    def get_scheduled_run(conf, schedule_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/schedules/{schedule_id}'

        try:
            r = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def resume_scheduled_run(conf, schedule_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/schedules/{schedule_id}/resume'

        try:
            r = requests.put(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def pause_scheduled_run(conf, schedule_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f'{Utils.get_service(conf)}/schedules/{schedule_id}/pause'

        try:
            r = requests.put(
                url,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def delete_artifact(conf, artifact_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            r = requests.delete(
                f'{Utils.get_service(conf)}/artifacts/{artifact_id}',
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(r)

    @check_token
    @staticmethod
    def get_artifact(conf, artifact_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            r = requests.get(
                f'{Utils.get_service(conf)}/artifacts/{artifact_id}',
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def update_drive_data(
            conf,
            kind: Literal["artifacts", "resources"],
            drive_id: str,
            param: dict
    ) -> None:

        conf = Utils.retrieve_conf(conf)
        token = Utils.retrieve_token(conf)
        delta_api = Utils.get_service(conf)

        try:
            headers = {
                'Authorization': f'Bearer {token}',
            }
            if "Topics" in param:
                headers['Topics'] = ','.join(param['Topics'])
            if "Visibility" in param:
                headers['Visibility'] = param['Visibility']
            if "Description" in param:
                headers['Description'] = param['Description']
            response = requests.put(
                f"{delta_api}/{kind}/{drive_id}",
                headers=headers,
            )
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        Utils.check_status(response)

        click.echo(f"{Utils.log_info} {kind} {drive_id} updated")

    @check_token
    @staticmethod
    def get_dt(conf, dt_name, param):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            dt_info_response = requests.get(
                f'{Utils.get_service(conf)}/deltatwins/{dt_name}',
                headers={'Authorization': f'Bearer {token}'},
                params=param)
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(dt_info_response)

        return dt_info_response.json()

    @check_token
    @staticmethod
    def delete_dt(conf, dt_name):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            dt_info_response = requests.delete(
                f'{Utils.get_service(conf)}/deltatwins/{dt_name}',
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(dt_info_response)
        click.echo(f"{Utils.log_info} DeltaTwin {dt_name} deleted")

    @check_token
    @staticmethod
    def update_dt(conf, dt_name: str, param: dict):
        conf = Utils.retrieve_conf(conf)
        token = Utils.retrieve_token(conf)
        delta_api = Utils.get_service(conf)
        try:
            response = requests.put(
                f"{delta_api}/deltatwins/{dt_name}",
                headers={"Authorization": f"Bearer {token}"},
                json=param
            )
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        Utils.check_status(response)

        click.echo(f"{Utils.log_info} DeltaTwin {dt_name} updated")

    @check_token
    @staticmethod
    def delete_dt_version(conf, dt_name, version):
        try:
            version = parse(version)
        except InvalidVersion:
            raise click.UsageError(f'Invalid version: {version}')

        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            dt_info_response = requests.delete(
                f'{Utils.get_service(conf)}/deltatwins/'
                f'{dt_name}/versions/{version}',
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(dt_info_response)
        click.echo(f"{Utils.log_info} Deltatwin {dt_name}:{version} deleted")

    @check_token
    @staticmethod
    def get_dt_manifest(conf, dt_name):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            dt_info_response = requests.get(
                f'{Utils.get_service(conf)}/deltatwins/'
                f'{dt_name}/files/manifest',
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(dt_info_response)

        return dt_info_response.json()

    @check_token
    @staticmethod
    def publish_dt(conf, data):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            resp = requests.post(
                f'{Utils.get_service(conf)}/deltatwins',
                headers={'Authorization': f'Bearer {token}'},
                json=data
            )
        except (ConnectionError, InvalidSchema):
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(resp)

    @check_token
    @staticmethod
    def publish_version_dt(conf, dt_name, data):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            resp = requests.post(
                f'{Utils.get_service(conf)}/deltatwins/{dt_name}',
                headers={'Authorization': f'Bearer {token}'},
                json=data
            )
        except (ConnectionError, InvalidSchema):
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(resp)

    @check_token
    @staticmethod
    def publish_dt_file(conf, data, file_to_publish):
        """
        Cett fonction renvoie une requete HTTP POST vers delta-api.
        La requete permet d'associer des fichiers à des deltatwin components
        Args:
            conf: la configuration des accès aux différents services autour
            data: les données pour savoir quel fichier associer à quel cmponent
            file_to_publish: le chemin du fichier à associer

        Returns:
            Aucun retour, mais on affiche les logs des appels sous-jacents
        """
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            # convertie depuis Postman
            resp = requests.post(
                url=f'{Utils.get_service(conf)}/deltatwins/'
                    f'{data["deltaTwinName"]}/files',
                headers={
                    'Authorization': f'Bearer {token}',
                    **data
                },
                files=[
                    ('file', ('file', open(file_to_publish, 'rb'),
                              'application/octet-stream'))
                ])
        except (ConnectionError, InvalidSchema):
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(resp)

    @check_token
    @staticmethod
    def check_dt_exists(conf, dt_name: str, version: str = None) -> bool:
        conf = Utils.retrieve_conf(conf)
        params = {}
        token = Utils.retrieve_token(conf)

        if version is not None:
            params['version'] = version
        try:
            version_resp = requests.get(
                f'{Utils.get_service(conf)}/deltatwins/{dt_name}',
                params=params,
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        return version_resp.status_code == 200

    @check_token
    @staticmethod
    def get_dt_version(conf, dt_name):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            version_resp = requests.get(
                f'{Utils.get_service(conf)}/deltatwins/{dt_name}/versions',
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(version_resp)

        return version_resp.json()

    @check_token
    @staticmethod
    def get_dts(conf, visibility):
        conf = Utils.retrieve_conf(conf)
        params = {}
        if visibility is not None:
            params['visibility'] = visibility
        token = Utils.retrieve_token(conf)

        try:
            dt = requests.get(
                f'{Utils.get_service(conf)}/deltatwins',
                headers={'Authorization': f'Bearer {token}'},
                params=params, stream=True)
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )

        Utils.check_status(dt)

        return dt.json()

    @check_token
    @staticmethod
    def retrieve_harbor_creds(conf) -> tuple[str, str]:
        conf = Utils.retrieve_conf(conf)
        token = Utils.retrieve_token(conf)

        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            credentials_resp = requests.get(
                f'{Utils.get_service(conf)}/harbor/credentials',
                headers=headers)
            Utils.check_status(credentials_resp)
            data = credentials_resp.json()

            return data["harbor_username"], data["harbor_secret"]
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        except Exception:
            raise click.UsageError(message='Usage Error')

    @check_token
    @staticmethod
    def create_project_harbor(conf,
                              project_name: str,
                              public: bool) -> tuple[str, str]:
        conf = Utils.retrieve_conf(conf)
        token = Utils.retrieve_token(conf)

        headers = {
            'Authorization': f'Bearer {token}',
        }

        data = {
            "project_name": project_name,
            "public": public
        }
        create_project_resp = requests.post(
            f'{Utils.get_service(conf)}/harbor/projects',
            headers=headers,
            data=json.dumps(data)
        )
        return create_project_resp.status_code

    @check_token
    @staticmethod
    def get_metric(conf):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            r = requests.get(
                f'{Utils.get_service(conf)}/metrics',
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service"
                        f" {Utils.get_service(conf)}"
            )
        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def get_metric_history(conf):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            r = requests.get(
                f'{Utils.get_service(conf)}/metrics/history',
                headers={'Authorization': f'Bearer {token}'})
        except ConnectionError:
            raise DeltaTwinServiceNotFound(
                message=f"Connection error to the service "
                        f"{Utils.get_service(conf)}"
            )
        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def create_resource(
            conf: str | None,
            path: str,
            filename: str,
            description: str,
            visibility: str,
            topics: list[str],
    ):
        conf = Utils.retrieve_conf(conf)
        owner = Utils.read_config(conf, "SERVICES").get("username", "John Doe")
        token = Utils.retrieve_token(conf)
        headers = {
            "Authorization": f"Bearer {token}",
            "Name": filename,
            "Visibility": visibility,
            "Description": description,
            "Topics": topics,
        }
        if re.match(r"^https?://", path):
            response = API.create_resource_from_remote_file(
                conf, path, headers
            )
        elif os.path.isfile(path):
            response = API.create_resource_from_local_file(conf, path, headers)
        else:
            raise DeltaTwinServiceError(f"File not found: {path}")
        Utils.check_status(response)

        return response.json().get("Id")

    @check_token
    @staticmethod
    def create_resource_from_local_file(
            conf: str, path: str, headers: dict[str, str]
    ):
        service_url = f"{Utils.get_service(conf)}/resources"
        # Supposed to stream the file as data without loading it in memory
        with open(path, "rb") as file:
            md5_hash = hashlib.file_digest(file, "md5")
            headers["Checksum"] = md5_hash.hexdigest()
            headers["Content-Length"] = str(os.stat(path).st_size)
            headers["Content-Disposition"] = (
                f"attachment; filename={os.path.basename(path)}"
            )
            headers["Content-Type"] = (
                    mimetypes.guess_type(path)[0] or "application/octet-stream"
            )
            file.seek(0)
            try:
                return requests.post(
                    service_url,
                    headers=headers,
                    data=file,
                )
            except ConnectionError:
                message = (f"{Utils.log_error} Connection error "
                           f"to the service {Utils.get_service(conf)}")
                raise DeltaTwinServiceError(message=message)

    @check_token
    @staticmethod
    def create_resource_from_remote_file(
            conf: str, url: str, headers: dict[str, str]
    ):
        service_url = f"{Utils.get_service(conf)}/resources"
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as ex:
            raise DeltaTwinServiceError(str(ex))

        if response.status_code != 200:
            raise DeltaTwinServiceError(
                "Invalid content provided: URL respond a "
                f"{response.status_code} status code"
            )

        # complete headers
        md5_hash = hashlib.md5()
        md5_hash.update(response.content)
        response_headers = response.headers
        headers["Checksum"] = md5_hash.hexdigest()
        headers["Content-Length"] = response.headers.get("Content-Length", -1)
        headers["Content-Type"] = response.headers.get(
            "Content-Type", "application/octet-stream"
        )
        if "Content-Disposition" in response_headers:
            headers["Content-Disposition"] = (
                response_headers["Content-Disposition"]
            )
        try:
            return requests.post(
                service_url,
                headers=headers,
                data=response.content,
            )
        except ConnectionError:
            message = (f"{Utils.log_error} Connection error "
                       f"to the service {Utils.get_service(conf)}")
            raise DeltaTwinServiceError(message=message)

    @check_token
    @staticmethod
    def delete_resource(conf, resource_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            r = requests.delete(
                f"{Utils.get_service(conf)}/resources/{resource_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
        except ConnectionError:
            message = (f"{Utils.log_error} Connection error "
                       f"to the service {Utils.get_service(conf)}")
            raise DeltaTwinServiceError(message=message)

        Utils.check_status(r)

    @check_token
    @staticmethod
    def download_resource(conf, resource_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        url = f"{Utils.get_service(conf)}/resources/{resource_id}/download"
        try:
            r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        except ConnectionError:
            message = (f"{Utils.log_error} Connection error "
                       f"to the service {Utils.get_service(conf)}")
            raise DeltaTwinServiceError(message=message)

        Utils.check_status(r)

        return r

    @check_token
    @staticmethod
    def get_resource(conf, resource_id):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)

        try:
            r = requests.get(
                f"{Utils.get_service(conf)}/resources/{resource_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
        except ConnectionError:
            message = (f"{Utils.log_error} Connection error "
                       f"to the service {Utils.get_service(conf)}")
            raise DeltaTwinServiceError(message=message)
        Utils.check_status(r)

        return r.json()

    @check_token
    @staticmethod
    def list_resource(conf, visibility):
        conf = Utils.retrieve_conf(conf)

        token = Utils.retrieve_token(conf)
        params = {}
        if visibility is not None:
            params["visibility"] = visibility

        url = f"{Utils.get_service(conf)}/resources"

        try:
            r = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params=params,
            )
        except ConnectionError:
            message = (f"{Utils.log_error} Connection error "
                       f"to the service {Utils.get_service(conf)}")
            raise DeltaTwinServiceError(message=message)

        Utils.check_status(r)

        return r.json()
