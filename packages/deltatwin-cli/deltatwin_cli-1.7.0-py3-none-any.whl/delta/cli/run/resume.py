import click

from delta.cli.utils import Utils


@click.command(
    'resume',
    short_help='Resume a model execution',
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ))
@click.pass_context
def resume(ctx):
    """Resume a model execution (if supported)

    **Note:** THIS COMMAND WILL BE AVAILABLE SOON
    """
    click.echo(
        f'{Utils.log_info} delta run resume not yet implemented.'
    )
