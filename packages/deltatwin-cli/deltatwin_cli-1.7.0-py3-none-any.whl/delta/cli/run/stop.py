from delta.core import DeltaCore
import click


@click.command(
    'stop',
    short_help='Stop the DeltaTwin component execution',
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ))
@click.pass_context
def stop(ctx):
    """Stop the DeltaTwin component execution.
    Your current directory is supposed to be a DeltaTwin component directory

    **Warning :** This command only works for the first versions of DeltaTwin
    component.
    Contact your administrator to get access to these Delta component.
    """
    parameters = {}
    for item in ctx.args:
        parameters.update([item.split('=')])
    with DeltaCore() as core:
        core.run_stop(**parameters)
