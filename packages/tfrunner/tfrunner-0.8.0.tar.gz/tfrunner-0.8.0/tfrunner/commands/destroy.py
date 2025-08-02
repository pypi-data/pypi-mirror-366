import subprocess
from pathlib import Path
from typing import Annotated, Optional

import typer

from tfrunner.projects.base import ProjectConfig, TfrunnerConfig
from tfrunner.secrets_backend.factory import SecretsBackendFactory
from tfrunner.state_backend.factory import StateBackendFactory
from tfrunner.utils import set_git_sandbox_env_var, get_sandbox_state_name

app = typer.Typer()


@app.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    }
)
def destroy(
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
    config = TfrunnerConfig.from_yaml(config_path)
    project_config: ProjectConfig = config.projects[project]
    _ = SecretsBackendFactory.select_and_run(
        config=config,
        project=project_config,
        environment=project,
    )
    if git_sandbox:
        set_git_sandbox_env_var()
    cmds: list[str] = [config.flavour.value, "destroy"] + ctx.args
    subprocess.call(cmds, cwd=project_config.path)
    if git_sandbox:
        state_name: str = get_sandbox_state_name(project_config.state_name)
        StateBackendFactory.destroy(
            kind=config.state_backend.kind,
            state_name=state_name,
            spec=config.state_backend.spec,
        )
