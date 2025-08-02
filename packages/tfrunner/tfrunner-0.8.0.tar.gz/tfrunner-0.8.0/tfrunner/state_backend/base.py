from abc import ABC, abstractmethod
from enum import Enum, unique

from pydantic import BaseModel

class GenericStateBackend(BaseModel):
    """
    Define a generic remote state backend.
    """

    flavour: str
    address: str
    username: str
    password: str
    lock_method: str = "POST"
    unlock_method: str = "DELETE"
    retry_wait_min: int = 5


class StateInitializer:
    """
    Generates an init command using a remote state backend.
    """

    @staticmethod
    def run(backend: GenericStateBackend) -> list[str]:
        return [
            backend.flavour,
            "init",
            f"-backend-config=address={backend.address}",
            f"-backend-config=lock_address={backend.address}/lock",
            f"-backend-config=unlock_address={backend.address}/lock",
            f"-backend-config=username={backend.username}",
            f"-backend-config=password={backend.password}",
            f"-backend-config=lock_method={backend.lock_method}",
            f"-backend-config=unlock_method={backend.unlock_method}",
            f"-backend-config=retry_wait_min={backend.retry_wait_min}",
        ]


########################################################
# Abstract base classes for state backend integrations #
########################################################


@unique
class StateBackendKind(Enum):
    GITLAB = "gitlab"


class StateBackendSpec(ABC, BaseModel):
    """
    Base Model for any state backend provider integration.
    """

    pass


class StateBackend(ABC):
    @classmethod
    def run(cls, state_name: str, config: StateBackendSpec) -> list[str]:
        """
        Returns a list of strings, consisting of a terraform
        command to execute to initialize the state backend.

        Args:
          state_name (str): name of the terraform state to use
          config (StateBackendSpec): configuration of the state backend

        Returns:
          list[str]: terraform init command for the selected backend
        """
        backend: GenericStateBackend = cls._get_state_backend(state_name, config)
        return StateInitializer.run(backend)

    @classmethod
    @abstractmethod
    def destroy(cls, state_name: str, config: StateBackendSpec) -> None:
        """
        Destroys the terraform state file.
        """
        pass

    @staticmethod
    @abstractmethod
    def _get_state_backend(
        state_name: str, config: StateBackendSpec
    ) -> GenericStateBackend:
        """
        Converts the State Backend Configuration of the provider to
        a generic state backend.

        Args:
          config (StateBackendSpec): configuration of the provider backend

        Returns:
          GenericStateBackend: backend configuration that's provider agnostic
        """
        pass
