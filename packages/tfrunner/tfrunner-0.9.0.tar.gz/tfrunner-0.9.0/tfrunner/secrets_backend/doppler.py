from dopplersdk import DopplerSDK
import typer

from tfrunner.env.env_loader import EnvLoader
from tfrunner.utils import load_env_var

from .base import SecretsBackend, SecretsBackendSpec


class DopplerSecretsBackendSpec(SecretsBackendSpec):
    # Name of the project to store secrets backend in
    project: str
    config: str
    # Name of the environment variable to fetch doppler token from
    token_var: str


class DopplerSecretsBackend(SecretsBackend):
    """
    Fetches Doppler secrets inside of a project.

    Loads them as env variables and returns them.
    """

    @classmethod
    def run(
        cls,
        environment: str,
        config: DopplerSecretsBackendSpec,
    ) -> dict[str, str]:
        typer.echo("==> Using Doppler secrets backend. Loading CI variables...")
        typer.echo(f"=> Doppler environment: {environment}")
        vars: dict[str, str] = cls.__get_doppler_secrets(
            project=config.project, config=config.config, token_var=config.token_var
        )
        EnvLoader.load(vars)
        typer.echo(f"=> Loaded variables: {list(vars.keys())}")
        return vars

    @classmethod
    def __get_doppler_secrets(cls, project: str, config: str, token_var: str) -> dict:
        sdk = DopplerSDK(access_token=load_env_var(token_var))
        results = sdk.secrets.list(project=project, config=config)
        results: dict = vars(results)
        return {k: v["raw"] for k, v in results["secrets"].items() if v["raw"] != ""}
