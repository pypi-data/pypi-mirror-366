import typer
import os

from tfrunner.projects.base import TfrunnerConfig, ProjectConfig
from tfrunner.utils import load_env_var


class EnvLoader:
    """
    Read variables from the environment and loads them as terraform vars
    """

    @classmethod
    def select_and_load(cls, config: TfrunnerConfig, project: ProjectConfig) -> None:
        """
        Selects the environment variables from the config and loads them.

        If both global and project env vars are available, merge them, overriding
        any colliding global vars with their project counterparts.
        """
        project_vars: dict[str, str] = project.env or {}
        global_vars: dict[str, str] = config.env or {}
        combined_vars = {**global_vars, **project_vars}
        vars = cls.fetch_env_values(combined_vars)
        cls.load(vars)
        typer.echo(f"=> Loaded environment variables: {list(vars.keys())}")

    @classmethod
    def fetch_env_values(cls, vars: dict[str, str]) -> dict[str, str]:
        return {k: cls.might_load_env_var(v) for k, v in vars.items()}

    @staticmethod
    def might_load_env_var(var: str) -> str:
        if var.startswith("$"):
            return load_env_var(var[1:])
        else:
            return var

    @staticmethod
    def load(vars: dict[str, str]) -> None:
        """
        Load the environment.
        This method should be implemented by subclasses.
        """
        for k, v in vars.items():
            os.environ[f"TF_VAR_{k.lower()}"] = v
