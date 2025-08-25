## Contributing Guidelines

### Before Contributing

Welcome to [batch_img](https://github.com/john-liu2/batch_img)! Before submitting a
pull request, please ensure that you __read the whole guidelines__. If you have any
question about this contributing guide, please [open an issue and state it
clearly](https://github.com/john-liu2/batch_img/issues/new).

#### Contribution

Any contribution is appreciated. Please read this section for making the contribution.
The contribution will be tested by the [test automation in GitHub
Actions](https://github.com/john-liu2/batch_img/actions) to make the code clean and
neat. After submitting your pull request, you should see the GitHub Actions tests
start to run at the pull request page. If the tests fail, click on the ___details___
button to read through the GitHub Actions output to understand the failure. If you do
not understand the failure, please ask for help.

#### Issues

To resolve an [open issue](https://github.com/john-liu2/batch_img/issues), simply make
a pull request with your proposed fix. __We do not assign issues in this repo__ so
please do not ask for permission to work on an issue.

Please add `Fixes #{$ISSUE_NUMBER}` to the pull request description that resolves
the open issue.
For example, if the pull request fixes issue #10, then please add the following to its
description:

```
Fixes #8
```

GitHub will use this tag to [auto-close the
issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)
when the pull request is merged.

### One-time Development Setup

The project was developed on **macOS** using **PyCharm** IDE. The commands below
should be run in **Terminal** windows on **macOS**.

#### One-time Toolchain Setup

One time installation of the `uv` tool to prepare for **All** future Python tools
installation. Install `uv` tool by its standalone installers:

```
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After **git clone** the repo to your local disk, go to the local project folder
and run the `uv` command:

```
uv pip install -e '.[dev]'
```

This will create a hidden virtualenv in the local project folder `.venv` and install
all dependencies defined in `pyproject.toml` file in this virtualenv.

If the `.venv` exists, this command will update the project version and dependencies
in the existing `.venv` virtualenv.

#### Activate Development Virtualenv

Run the command to activate the development virtualenv:

```
source .venv/bin/activate
```

#### One-time Pre-commit Plugin Installation

The **dev** dependencies have [pre-commit](https://pre-commit.com/#installation)
installed. This is the tool to automatically trigger actions when making a
**git commit**. To activate the tool, please run the **one-time** command:

```
pre-commit install
```

After the installation, the plugin will run every time you commit a change. If any
error during the run, the **git commit** will fail. Please fix the error and commit
the change again. Optionally, you can manually run the plugin:

```
pre-commit run --all-files --show-diff-on-failure
```
