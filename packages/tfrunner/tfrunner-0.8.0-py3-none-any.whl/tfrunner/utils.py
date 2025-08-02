import os
import subprocess
from typing import Optional


def load_env_var(var: str) -> str:
    token: Optional[str] = os.environ.get(var)
    if token is None:
        raise ValueError(f"Environment variable {var} is not set.")
    return token


###########
# Sandbox #
###########


def get_current_git_branch_sanitized_name() -> str:
    branch_name: str = subprocess.getoutput("git rev-parse --abbrev-ref HEAD").strip()
    return branch_name.lower().replace("/", "-").replace("_", "-")


def get_sandbox_state_name(original_state_name: str) -> str:
    branch_name: str = get_current_git_branch_sanitized_name()
    return f"{branch_name}-{original_state_name}"


def set_git_sandbox_env_var() -> None:
    branch_name: str = get_current_git_branch_sanitized_name()
    os.environ["TF_VAR_sandbox_name"] = branch_name
