import requests
import typer

from tfrunner.projects.base import TfrunnerFlavour
from tfrunner.utils import load_env_var

from .base import GenericStateBackend, StateBackend, StateBackendSpec


class GitlabStateBackendSpec(StateBackendSpec):
    flavour: TfrunnerFlavour
    url: str
    project_id: int
    token_var: str


class GitlabStateBackend(StateBackend):
    @staticmethod
    def _get_state_backend(
        state_name: str,
        config: GitlabStateBackendSpec,
    ) -> GenericStateBackend:
        typer.echo(
            "==> Using Gitlab terraform state backend. Initializing backend properties..."
        )
        return GenericStateBackend(
            flavour=config.flavour,
            address="{}/api/v4/projects/{}/terraform/state/{}".format(
                config.url, config.project_id, state_name
            ),
            username="dummy",
            password=load_env_var(config.token_var),
        )

    @classmethod
    def destroy(
        cls,
        state_name: str,
        config: GitlabStateBackendSpec,
    ) -> None:
        typer.echo(f"==> Destroying GitLab state: {state_name}...")
        state_backend: GenericStateBackend = cls._get_state_backend(
            state_name=state_name, config=config
        )
        requests.delete(
            url=state_backend.address,
            headers={"PRIVATE-TOKEN": state_backend.password},
        )
