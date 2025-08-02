import os
from typing import Optional

from pydantic import HttpUrl

from tfrunner.exceptions import EnvVarNotSet
from tfrunner.types import ConfigBaseModel


class GitLabProjectConfig(ConfigBaseModel):
    url: HttpUrl
    project_id: int
    token_var: str
    state_name: str
