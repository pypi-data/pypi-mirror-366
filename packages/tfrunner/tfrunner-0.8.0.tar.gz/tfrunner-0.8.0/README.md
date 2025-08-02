# Tfrunner

Welcome to `tfrunner`, a `cli` tool to run terraform commands with the following facilities:
- Multi-project support
- Automation support
- Remote backend
- GitLab secrets pulling


## Installation

Since `tfrunner` is a `cli` tool, the recommended installation is using `pipx`.

Please ensure you have a compatible `python >= 3.12` version.

Install with: `pipx install tfrunner`


## Usage

**Requirements**: `tfrunner` expects the following binaries to be installed:
- `terraform`: `tfrunner` is a wrapper on top of `terraform`
- `git`: when using the `--git-sandbox` flag, ensure you have `git` installed and that you are running the command in a `git` project

To use it to manage multiple projects, create a `yaml` file configuring each.

Here is an example file, let's name it `tfrunner.yaml`:
```yaml
state_backend:
  kind: gitlab
  spec:
    url: https://gitlab.com
    project_id: 123456
    token_var: KUBORG_TOKEN

secrets_backend:
  kind: gitlab
  spec:
    url: https://gitlab.com
    project_id: 123456
    token_var: KUBORG_TOKEN

projects:
  great-project:
    path: ./infra/great-project/terraform
    state_name: great-state

  awesome-project:
    path: ./infra/awesome-project/terraform
    state_name: awesome-state
```

Now you can run `tfrunner` as you would run any regular `terraform` command (options are also included). You need only to be wary of two additional arguments that are needed:
- `--project`: name of your project, as specified in your config file.
- `--config_path`: path to your configuration file. By default it will look for a `tfrunner.yaml` file in the current folder

As examples, for the `great-project` in our example `tfrunner.yaml` file, you could run:
```bash
tfrunner init --project great-project
tfrunner fmt --project great-project
tfrunner validate --project great-project
tfrunner plan --project great-project
tfrunner apply --project great-project
tfrunner destroy --config_path tfrunner.yaml --project great-project
```

The `--config_path` is optional in the `tfrunner destroy` command, as `tfrunner` will by default assume its path to be `tfrunner.yaml`.

## Usage with git-sandboxes

```bash
tfrunner init --project great-project --git-sandbox
tfrunner plan --project great-project --git-sandbox
tfrunner apply --project great-project --git-sandbox
tfrunner destroy --project great-project --git-sandbox
```

## Local development

**Requirements**:
- `uv` installed
- `terraform` installed
- `git` installed

1. Install virtual environment: `uv sync --all-groups`


# TODO:

- Make `tfrunner plan` generate a plan file by default
- Make `tfrunner apply` use that plan file by default
