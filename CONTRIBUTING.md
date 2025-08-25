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
should be run in **Terminal** window on **macOS**.

#### One-time `uv` Setup

Install the [`uv`](https://github.com/astral-sh/uv) tool one-time to prepare for
**all** Python tools and packages installation. Install
[`uv`](https://github.com/astral-sh/uv) by its standalone installers:

```
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After `git clone ...` the repo to your local disk, go to the local project folder
and run the [`uv`](https://github.com/astral-sh/uv) command:

```
uv pip install -e '.[dev]'
```

This will create a hidden virtualenv dir in the local project folder - `.venv` and
install all dependencies defined in the `pyproject.toml` file in this virtualenv.

If the `.venv` exists, this command will update the project version and dependencies
in the existing `.venv` virtualenv.

#### Activate Development Virtualenv

Run the command to activate the development virtualenv:

```
source .venv/bin/activate
```

#### Activate `pre-commit`

The [`pre-commit`](https://pre-commit.com/#installation) tool is installed as part
of **dev** dependencies. It is the tool to automatically trigger actions when making
a `git commit ...`. To activate the tool, please run the **one-time** command:

```
pre-commit install
```

After the activation, the plugin will run every time you commit a change. If any
error during the run, the `git commit ...` will fail. Please fix the error and
commit the change again. Optionally, you can manually run the plugin:

```
pre-commit run --all-files --show-diff-on-failure
```

#### Run `ruff`

The [`ruff`](https://github.com/astral-sh/ruff) tool is installed as part of
**dev** dependencies. It is to check and fix Python code format and lint.
Run the [`ruff`](https://github.com/astral-sh/ruff) linter command:

```
ruff check --fix --exit-non-zero-on-fix
```

Run the [`ruff`](https://github.com/astral-sh/ruff) formater command:

```
ruff format --diff --check
```

#### Run `pylint`

The [`pylint`](https://github.com/pylint-dev/pylint) tool is installed as part
of **dev** dependencies. It is a static code analyser checking the Python code
without running it. The `pylint` is slower than `ruff`. They are complementary
to each other.
Run the [`pylint`](https://github.com/pylint-dev/pylint) command:

```
pylint $(git ls-files '*.py')
```

#### Run `pytest`

The [`pytest`](https://github.com/pytest-dev/pytest) tool is installed as part of
**dev** dependencies. It will run all the **unit tests** and integration tests.
Run the [`pytest`](https://github.com/pytest-dev/pytest) command:

```
pytest
```

Run the [`pytest`](https://github.com/pytest-dev/pytest) with code coverage:

```
pytest --cov-report=term --cov=batch_img tests
```

Run command defined in [`Makefile`](https://github.com/john-liu2/batch_img/blob/main/Makefile):

```
make test
```
