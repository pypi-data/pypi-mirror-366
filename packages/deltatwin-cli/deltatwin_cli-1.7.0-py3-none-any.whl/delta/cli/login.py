import os

import click

from delta.cli.utils import API, Utils


@click.command('login', short_help='Create a DeltaTwin® session.')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the configuration file that stores connection user data.')
@click.option(
    '--api',
    '-a',
    type=str,
    default=None,
    help='Url to the DeltaTwin® API service.')
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help='Log again the user without using the refresh token.')
@click.help_option("--help", "-h")
@click.argument('username', default=None, required=False)
@click.argument('password', default=None, required=False)
def delta_login(username, password, conf, api, force):
    """
    It logs the user to the DeltaTwin® Service, and allows the use of commands,
    such as
    ``deltatwin component list`` command, that requires online registration.

    Once logged in, all the information are stored in a conf.ini file. In this
    way, if you want to log in again you just have to use the command
    ``deltatwin login`` without entering your credentials, it will
    only try to refresh the token.
    The path to the conf.ini file can be set by the user using the option -c.
    By default, the file is saved in your HOME directory.

    """

    # Create default conf
    if conf is None:
        conf = os.path.expanduser('~') + '/.deltatwin/conf.ini'
        if not os.path.exists(os.path.expanduser('~') + '/.deltatwin'):
            os.mkdir(os.path.expanduser('~') + '/.deltatwin')
    elif not conf.endswith('.ini'):
        conf += '/conf.ini'

    # Load conf from an existing file
    if os.path.isfile(conf):
        data = Utils.read_config(conf, 'SERVICES')
        if username is not None and password is not None:
            data['username'] = username
            data['password'] = password

        if data['username'] is None or data['password'] is None:
            raise click.BadParameter(
                f'{Utils.log_error} an API URL must be provided')
        if api is None and data['api'] is None:
            raise click.BadParameter(
                f'{Utils.log_error} an API URL must be provided')
        elif api is not None:
            data['api'] = api

        Utils.save_config(conf, 'SERVICES', data)
    # Raise error if no login/password has been given
    else:
        if username is None or password is None:
            raise click.BadParameter(
                f'{Utils.log_error} an Username and Password must be provided')

        data = {
            'username': username,
            'password': password,
            'api': api
        }

        if data['api'] is None:
            raise click.BadParameter(
                f'{Utils.log_error} an API URL must be provided')

        Utils.save_config(conf, 'SERVICES', data)

    if force:
        API.force_login(conf)

    else:
        API.refresh_token(conf)
    click.echo(f'{Utils.log_info} Login to the service token saved in {conf}')
