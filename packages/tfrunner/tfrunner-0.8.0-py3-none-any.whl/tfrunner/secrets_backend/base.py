from abc import ABC, abstractmethod
from enum import Enum, unique

from pydantic import BaseModel


#######################################################
# Abstract base classes for all provider integrations #
#######################################################


@unique
class SecretsBackendKind(Enum):
    GITLAB = "gitlab"
    DOPPLER = "doppler"


class SecretsBackendSpec(ABC, BaseModel):
    """
    Base Model for any secret backend provider integration
    """


class SecretsBackend(ABC):
    @classmethod
    @abstractmethod
    def run(cls, config: SecretsBackendSpec) -> dict[str, str]:
        """
        Fetches secrets and converts them to environment variables.

        Returns the secrets as an output.

        Args:
          config (SecretsBackendSpec): configuration of the secrets backend

        Returns:
          dict[str, str]: secrets
        """
        pass
