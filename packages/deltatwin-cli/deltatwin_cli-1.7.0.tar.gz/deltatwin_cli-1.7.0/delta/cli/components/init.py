import json
import os
import shutil

import click

from delta.cli.components.template.manifest import Manifest
from delta.cli.utils import Utils


@click.command(
    'init',
    short_help='Create locally an empty DeltaTwin® repository')
@click.argument('directory',
                type=str)
@click.help_option("--help", "-h")
def init(directory):
    """Create locally an empty DeltaTwin® repository.

    The DIRECTORY automatically contains the files
    used to manage a DeltaTwin® component, namely the manifest and workflow
    files.
    A sub-directory named "models" is created to store the code files.

    The manifest file contains the DeltaTwin® description, like the aim
    of the project, the licence, the required inputs and their description,
    the generated outputs, the models or the processes to be executed.
    The workflow file defines how the different processes (models) work
    together to achieve the desired outcome.

    For help building your manifest and workflow files,
    please refer to our tutorial documentation available here:
        https://deltatwin.destine.eu/docs/tutorials

    MANDATORY ARGUMENT:

    DIRECTORY : path to the folder containing the DeltaTwin® component.
    """
    if os.path.isdir(directory):
        raise click.UsageError("DIRECTORY must not exists")
    os.makedirs(os.path.join(directory, "models"), exist_ok=True)
    conf = Utils.retrieve_conf(None)
    owner = Utils.read_config(conf, "SERVICES").get("username", "John Doe")
    dt_name = os.path.basename(directory)
    manifest = Manifest(name=dt_name, owner=owner)
    manifest_dump = manifest.model_dump(
        include=["name", "description", "license", "owner"]
    )
    with open(os.path.join(directory, "manifest.json"), "w") as f:
        json.dump(manifest_dump, f, indent=4)
    workflow_tmpl = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "template", "workflow.yml"
    )
    shutil.copyfile(workflow_tmpl, os.path.join(directory, "workflow.yml"))
    click.echo(f"{Utils.log_info} DeltaTwin {dt_name} created")
