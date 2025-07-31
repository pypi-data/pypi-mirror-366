import click

from delta.cli.utils import API


@click.command(
    'delete',
    short_help='Delete a version of a DeltaTwin® component '
               'or the entire component.'
)
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.argument('dt_name')
@click.option('--version', '-v', type=str, default=None,
              help='Version of DeltaTwin® component to be deleted')
@click.option('--yes', '-y',
              type=bool,
              required=False,
              is_flag=True,
              default=False,
              help="Don't ask for confirmation of deletion")
@click.help_option("--help", "-h")
def delete_deltatwin_info(
        conf,
        dt_name,
        version,
        yes):
    """This command can be used to remove either a version of a DeltaTwin®
    component or the whole Deltatwin® component, i.e all its versions.

    Before using this command the user must be logged in.

    WARNING: When deleting a DeltaTwin® component, all generated
    artifacts are transformed into resources because the service will
    no longer be able to relate them to the version of the DeltaTwin®
    component that was used to generate them.


    Only the user who has published the DeltaTwin® version or the administrator
    can perform the deletion.
    """
    msg = f'Are you sure you want to delete the DeltaTwin® {dt_name} ?'
    if yes or click.confirm(msg, default=False):
        if version is not None:
            API.delete_dt_version(conf, dt_name, version)
        else:
            API.delete_dt(conf, dt_name)
