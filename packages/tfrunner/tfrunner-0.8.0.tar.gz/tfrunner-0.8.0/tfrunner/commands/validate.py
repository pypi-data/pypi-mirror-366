import subprocess
from pathlib import Path
from typing import Annotated, Optional

import typer

from tfrunner.projects.base import ProjectConfig, TfrunnerConfig

app = typer.Typer()


@app.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    }
)
def validate(
    ctx: typer.Context,
    project: Annotated[
        Optional[str], typer.Option(help="name of the project to initialize")
    ],
    config_path: Annotated[
        Path,
        typer.Option(
            help="location of the config file to use for the tool's execution"
        ),
    ] = Path("tfrunner.yaml"),
) -> None:
    config = TfrunnerConfig.from_yaml(config_path)
    project_config: ProjectConfig = config.projects[project]
    cmds: list[str] = [config.flavour.value, "validate"] + ctx.args
    subprocess.call(cmds, cwd=project_config.path)
