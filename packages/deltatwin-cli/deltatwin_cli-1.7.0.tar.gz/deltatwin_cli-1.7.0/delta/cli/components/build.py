import click
from delta.core import DeltaCore


@click.command(
    "build", short_help="""Build the DeltaTwin® component image
                        with a (user) provided tag"""
)
@click.option(
    "--tag",
    "-t",
    type=str,
    default="latest",
    help="The (build) image tag name. Default value is 'latest'",
)
@click.option(
    "--registry",
    "-r",
    type=str,
    default="docker.io",
    help="The user defined registry. Default value is 'docker.io'",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="If enabled, do not use cache Docker build cache"
)
@click.help_option("--help", "-h")
def build(tag, registry, no_cache):
    """Build the DeltaTwin® component image with a (user) provided tag

    \b
    🛈 This command must be executed on the directory of the DeltaTwin®
    component

    \b
    Example:
        cd <delta_twin_directory>
        deltatwin component build --no-cache --tag dev --registry registry_url
    """
    with DeltaCore() as core:
        try:
            core.drive_build(version=tag, registry=registry, no_cache=no_cache)
        except Exception as e:
            raise click.UsageError(
                f"Something went wrong when building image:\n\t{e}")
