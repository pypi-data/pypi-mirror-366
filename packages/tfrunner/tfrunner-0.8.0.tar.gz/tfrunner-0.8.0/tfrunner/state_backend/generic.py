from pydantic import BaseModel

from tfrunner.projects.base import TfrunnerFlavour

class GenericStateBackend(BaseModel):
    """
    Define a generic remote state backend.
    """

    flavour: TfrunnerFlavour
    address: str
    username: str
    password: str
    lock_method: str = "POST"
    unlock_method: str = "DELETE"
    retry_wait_min: int = 5
