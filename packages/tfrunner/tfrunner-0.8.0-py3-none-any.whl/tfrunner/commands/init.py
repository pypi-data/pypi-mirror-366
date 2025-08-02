import subprocess
from pathlib import Path
from typing import Annotated, Optional

import typer

from tfrunner.projects.base import ProjectConfig, TfrunnerConfig
from tfrunner.state_backend.factory import StateBackendFactory
from tfrunner.utils import get_sandbox_state_name

app = typer.Typer()


@app.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    }
)
def init(
    ctx: typer.Context,
    project: Annotated[
        Optional[str], typer.Option(help="name of the project to initialize")
    ],
    git_sandbox: Annotated[
        bool,
        typer.Option(
            help="execute terraform/tofu project in a sandbox environment of your git branch"
        ),
    ] = False,
    config_path: Annotated[
        Path,
        typer.Option(
            help="location of the config file to use for the tool's execution"
        ),
    ] = Path("tfrunner.yaml"),
) -> None:
    # Fetch configurations
    config = TfrunnerConfig.from_yaml(config_path)
    project_config: ProjectConfig = config.projects[project]

    # Append git branch to state name if using git sandbox mode
    if git_sandbox:
        state_name: str = get_sandbox_state_name(project_config.state_name)
    else:
        state_name: str = project_config.state_name

    # Initialize terraform
    init_cmd: list[str] = StateBackendFactory.run(
        kind=config.state_backend.kind,
        state_name=state_name,
        spec=config.state_backend.spec,
    )
    init_cmd += ctx.args
    subprocess.call(init_cmd, cwd=project_config.path)
