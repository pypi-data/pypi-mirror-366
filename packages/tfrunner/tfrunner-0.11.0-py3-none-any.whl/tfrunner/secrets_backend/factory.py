import typer

from .base import SecretsBackendKind
from .gitlab import GitlabSecretsBackend, GitlabSecretsBackendSpec
from .doppler import DopplerSecretsBackend, DopplerSecretsBackendSpec

from tfrunner.projects.base import TfrunnerConfig, ProjectConfig


class SecretsBackendFactory:
    @classmethod
    def select_and_run(
        cls, config: TfrunnerConfig, project: ProjectConfig, environment: str
    ) -> dict[str, str]:
        """
        Selects the secrets backend based on the configuration and runs it.

        Args:
          config (TfrunnerConfig): configuration of the tfrunner tool
          project (ProjectConfig): configuration of the project
          environment (str): environment to run the secrets backend in

        Returns:
          dict[str, str]: secrets
        """
        if config.secrets_backend is None and project.secrets_backend is None:
            typer.echo("No secrets backend configured. Skipping secrets loading.")
            typer.echo("You can configure it in tfrunner.yaml file.")
            return {}
        elif project.secrets_backend is not None:
            typer.echo("Using project-specific secrets backend.")
            secrets_backend = project.secrets_backend
        else:
            typer.echo("Using global secrets backend from tfrunner.yaml.")
            secrets_backend = config.secrets_backend
        _ = cls.run(
            kind=secrets_backend.kind,
            environment=project,
            spec=secrets_backend.spec,
        )
        return cls.run(
            kind=secrets_backend.kind,
            environment=environment,
            spec=secrets_backend.spec,
        )

    @staticmethod
    def run(kind: SecretsBackendKind, environment: str, spec: dict) -> dict[str, str]:
        if kind == SecretsBackendKind.GITLAB:
            spec = GitlabSecretsBackendSpec(**spec)
            return GitlabSecretsBackend.run(environment, spec)
        elif kind == SecretsBackendKind.DOPPLER:
            spec = DopplerSecretsBackendSpec(**spec)
            return DopplerSecretsBackend.run(environment, spec)
        else:
            raise ValueError(f"Unsupported secrets backend {kind}")
