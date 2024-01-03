# Setting up a new repository

By default, all our repositories should be public and MIT licensed, unless there's a specific reason that's not possible.

This document describes how to set up a new repository:

* Within GitHub (user permissions, branch protection)
* Applying code linters (black, ruff, mypy)
* As a package source (setup.py, pypi preparation)

## Repository Template

The [cpg-python-template-repo](https://github.com/populationgenomics/cpg-python-template-repo) template contains a README & MIT software license, and has linter configuration & github actions configured. This can be used as a starting template to simplify setup.

To use this template you can either create a new repository and select this from the drop-down templates, or navigate to the template repository and click `Use This Template` to begin. Branch protection rules, user access, and pip packaging (where appropriate) still need to be added manually.

---

After you have created a GitHub repository, you should change the following  settings:

![merge settings](figures/merge.png)

Only allow _merge commits_ for forks in which you'll incorporate upstream changes. Squash merging keeps the history much cleaner.

Under _Branches_, add a _branch protection rule_ to enforce reviews for the `main` branch:

![branch rule](figures/branch_rule.png)

Under _Manage Access_, add collaborators. Prefer to add teams instead of individual people. It's common to add `populationgenomics/software-team` and `populationgenomics/genomic-analysis-team` with _write_ permissions.

The next step is to initiate a `README.md`, add an MIT license, and a `.gitignore` file, unless these files were already added previously via the GitHub web interface.

Following that, you may want to set up linters for code style and error checks, and (if the project can be shipped as a package) set up versioning and automated artifact
builds. This document provides tips on how to set these things up.

* [Linters](#linters)
  * [Setting up pre-commit](#setting-up-pre-commit)
  * [Disabling inspections](#disabling-inspections)
* [Setting up setup.py](#setting-up-setuppy)
* [Versioning project](#versioning-project)
* [GitHub Actions](#github-actions)
  * [Adding GitHub Actions](#adding-github-actions)

## Linters

To help us in implementing a consistent coding style throughout our code base, we use git [pre-commit](https://github.com/pre-commit/pre-commit) hooks with a set of linters that check and/or reformat the files in the repository.

* pre-commit comes with a [set of hooks](https://github.com/pre-commit/pre-commit-hooks#hooks-available) that perform some very useful inspections:
  * `check-yaml` to check YAML file correctness,
  * `end-of-file-fixer` that automatically makes sure every file ends with exactly one line end character,
  * `trailing-whitespace` that removes whitespace in line ends,
  * `check-case-conflict` checks for files with names that would conflict on a case-insensitive filesystems like MacOS,
  * `check-merge-conflict` check files that contain merge conflict strings,
  * `detect-private-key` checks for existence of private keys
  * `debug-statements` checks for debugger imports and py37+ breakpoint() calls in Python source
  * `check-added-large-files` prevents giant files from being committed (larger than 500kB);
  * [markdownlint](https://github.com/igorshubovych/markdownlint-cli) checks the style of the Markdown code;
* [ruff](https://github.com/astral-sh/ruff/) and [mypy](https://mypy-lang.org/) check Python code style in accordance with [PEP8](https://www.python.org/dev/peps/pep-0008/), and perform static analysis to catch potential programming
  errors.
* [black](https://github.com/psf/black) reformats Python code to make it conform
  to [PEP8](https://www.python.org/dev/peps/pep-0008/).

### Setting up pre-commit

Instead of setting up fresh pre-commit configuration, the [template repository](https://github.com/populationgenomics/cpg-python-template-repo)
already has the following content:

* `.pre-commit-config.yaml` - contains inspection settings for each tool
* `.markdownlint.json` - settings for [markdownlint](https://github.com/igorshubovych/markdownlint-cli)
* `pyproject.toml` - settings for [black](https://github.com/psf/black) and [ruff](https://github.com/astral-sh/ruff/)

Editing the content of these files can modify the behaviour of individual tools. Please copy these files as required from the cpg-python-template repo where you want to add these to an existing, or non-templated repository.

### Enabling pre-commit plugins

Install pre-commit globally, or into your virtual environment. You don't need to install ruff or other tools, as pre-commit will do that for you.

```shell
pip install pre-commit
```

You can run pre-commit manually:

```sh
pre-commit run --all-files
```

> Optional: Run pre-commit hooks with Git
>
> ```sh
> pre-commit install --install-hooks
> ```
>
> On every `git commit`, the code will be automatically checked, and possibly reformatted. If any of the checks didn't pass, or any reformatting was done, the actual `git commit` command will not be performed. Instead, you can act upon linters' suggestions and re-run the `git commit` command afterwards.


### Disabling inspections

Note that you may find some linters produce false positives, or just find some checks irrelevant for your particular project. In this case, you may want to modify the configuration files to disable additional inspections.

Carefully consider before disbaling specific inspections for an entire project.

#### Ruff

To disable an inspection for rust, you can either:

```python
# ruff: noqa: F401
# When at the start of the file, this disables F401 for the whole file

# disable F401 for this specific line
from foo import bar # noqa: F401

# disable ruff for this specific line
from foo import bar # noqa
```

Or add it to the pyproject.toml.

#### Mypy

Note that mypy won't typecheck a function if the parameters and return types aren't completely typed.

You can disable typing for a specific line by adding:

```python
x: int = "bla"  # type: ignore
```

#### Black

To hide a piece of code from being reformatted with black, you
[can surround](https://github.com/psf/black#the-black-code-style)
your code with `# fmt: off` and `# fmt: on`.

#### Pylint / Flake8

In some of our repositories, we stil use Pylint / Flake8. Flake8 uses the same semantic as `ruff`. For pylint, disable a specific inspection with `# pylint: disable=<inspection-id>`. For examples, look at
the [Hail code base](https://github.com/hail-is/hail/blob/5b25084d7d8d5ff9908dc48ced1f3583eabd25d2/hail/python/hailtop/hailctl/__main__.py#L60).


## Setting up setup.py

For Python projects, you want to create a `setup.py` file in the root of your project. See [`analysis-runner/setup.py`](https://github.com/populationgenomics/analysis-runner/blob/main/setup.py) as an example to bootstrap from.

After creating `setup.py`, you can install your code as a Python package into your dev environment in the "editable" mode with:

```bash
pip install --editable .
```

This will make sure that any changes to the code base will be immediataly reflected in the module and scripts you just installed, so you won't have to rerun `pip install`, unless you change `setup.py` again.

## Versioning project

To version projects, we use a tool called [bump2version](https://pypi.org/project/bump2version/). It helps to avoid editing version tags manually, which can be very error-prone. Instead, bump2version can increment the version of the project for you with one command. It relies on a config file called `.bumpversion.cfg` to determine the current project version, as well as the locations in the code where this version should be updated.

See the [`analysis-runner/.bumpversion.cfg`](https://github.com/populationgenomics/analysis-runner/blob/main/.bumpversion.cfg) as an example.

To increment the new version, run `bump2version <mode>`, where `<mode>` is:

* `major`: `X.0.0`
* `minor`: `0.X.0`
* `patch`: `0.0.X`

If you get the error: `bumpversion: error: the following arguments are required: --new-version`, you're probably in a directory without the config.

## GitHub Actions

It is useful to have a [GitHub Actions](https://github.com/features/actions) workflow set for your repository that will do a set of automated tasks, like check the code with linters, run tests, and/or package and ship the code.

To set up a workflow that would check the code with pre-commit on every git push or pull-request event, create a file called `.github/workflows/lint.yaml` based the following: [cpg-utils/lint.yaml](https://github.com/populationgenomics/cpg-utils/blob/main/.github/workflows/lint.yaml).


```yaml
# .github/workflows/lint.yaml
name: Lint
on: [push]

jobs:
  lint:
    runs-on: ubuntu-latest
    defaults:
      run:
        shell: bash -l {0}

    steps:
    - uses: actions/checkout@v2

    - uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install packages
      run: pip install -r requirements.txt

    - name: pre-commit
      run: pre-commit run --all-files
```

After pushing `.github/actions/lint.yaml` and `requirements.txt`, GitHub will know to run linters on every push and pull request, and display checks in the web interface.

<img src="figures/github_lint_check.png" width="400"/>

### Adding GitHub Actions

You can set up GitHub Actions to build and upload the package to the Pypi, so it becomes available to install with `pip install <package>`. We traditionally push to pypi on every push to the `main` branch. We don't override packages, so ensure you add a bumpversion commit to release the package.

First, you need to create a GitHub secret with the Pypi token. To find the token, please contact a software team member.

Finally, set up another GitHub workflow:

```yaml
# .github/workflows/deploy.yaml

name: Deploy
on:
  push:
    branches:
      - main

jobs:
  package:
    runs-on: ubuntu-latest
    defaults:
      run:
        shell: bash -l {0}
    steps:
    - uses: actions/checkout@main

    - uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Build
      run: python setup.py sdist

    - name: Test install
      run: pip install dist/*

    - name: Test import
      run: python -c "import <package>"

    - name: Publish the wheel to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        user: __token__
        password: ${{ secrets.PYPI_API_TOKEN }}
        packages-dir: dist/
        skip-existing: true
```
