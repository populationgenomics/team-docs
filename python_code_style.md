# Python Code Style

- [Python Code Style](#python-code-style)
  - [Setting up a new project](#setting-up-a-new-project)
  - [False positives](#false-positives)
  - [GitHub checks of PRs](#github-checks-of-prs)
  - [Visual Studio Code](#visual-studio-code)
  - [PyCharm](#pycharm)

To help us in implementing a consistent coding style throughout
our code base, we use git [pre-commit](https://github.com/pre-commit/pre-commit)
hooks with a set of linters to check and reformat the code:

- [pylint](https://www.pylint.org/) and [flake8](https://flake8.pycqa.org/)
  check the code style in accordance with
  [PEP8](https://www.python.org/dev/peps/pep-0008/), and perform some static
  analysis to catch potential programming errors.
- [pylint-quotes](https://pypi.org/project/pylint-quotes/) is a plugin to
  pylint that adds checks of the consistency of quotes (we stick to single
  quotes, with the only reason to prefer them over double quotes being the
  visual noise).
- [black](https://github.com/psf/black) actually reformats the code to make
  it conform to [PEP8](https://www.python.org/dev/peps/pep-0008/).
- Additional hooks provided by
  [pre-commit](https://github.com/pre-commit/pre-commit-hooks#hooks-available):
  - check-yaml
  - end-of-file-fixer
  - trailing-whitespace
  - check-case-conflict
  - check-merge-conflict
  - detect-private-key
  - debug-statements
  - check-added-large-files

## Setting up a new project

When creating a new repository that contains Python code, please add
these configuration files into the repository root folder:

```sh
URL=https://raw.githubusercontent.com/populationgenomics/team-docs/main/linting
wget $URL/pre-commit-config.yaml -O .pre-commit-config.yaml
wget $URL/pyproject.toml -O pyproject.toml
wget $URL/pylintrc -O .pylintrc
wget $URL/flake8.toml -O .flake8.yaml
```

Follow it with the following commands to enable pre-commit hooks:

```sh
pip install pre-commit
pre-commit install
```

Now on every `git commit`, the code will be automatically checked and
possibly reformatted. If any of the checks didn't pass or reformatting was
done, the actual `git commit` command will not be performed. You can act
upon linters' suggestions and re-run the `git commit` command afterwards.

## False positives

Note that you may find some linters produce false positives, or run checks
irrelevant for your particular project. In this case, you may want to modify
the configuration files to disable additional inspections. For example, pylint
might fail to recognise imports of third-party libraries; in
which case you can add E0401 ("Unable to import"), E1101 (no-member) and
I1101 (c-extension-no-member) to the comma-separated list in `.pylintrc`:

```sh
disable=<...>,E0401,E1101,I1101
```

To hide a piece of code for being reformatted with black, you
[can surround](https://github.com/psf/black#the-black-code-style)
your code with `# fmt: off` and `# fmt: on`.

## GitHub checks of PRs

In addition to `.pylintrc`, create a GitHub Actions CI workflow under
`.github/workflows/main.yaml` with the following contents (or add the `lint` job
to an exsting workflow):

```sh
mkdir -p .github/workflows
wget https://raw.githubusercontent.com/populationgenomics/team-docs/main/pylint\
/github-workflow.yaml -O .github/workflows/main.yaml
```

This will make GitHub run the linters on every push and pull request, and
display checks in the web interface.

<img src="figures/github_lint_check.png" width="400"/>

## Visual Studio Code

Visual Studio Code auto-detects a .pylintrc file in the project root and asks
the user whether to install pylint, if it's not installed already.

## PyCharm

1. Make sure you have pylint installed with `pip install pylint pylint-quotes`.

2. Install the PyCharm "Pylint" plugin ([Preferences] > [Plugins] > search for
   "Pylint"). It will automatically find the pylint executable. A new tool
   window called Pylint will be added. You can use it to scan the project:

   <img src="figures/pycharm_pylint_tool_window.png" width="700"/>

3. You can also enable real-time inspections by going to: Go to Preferences >
   Editor > Inspections > enable "Pylint real-time scan". However, it's not
   recommended as it's has a negative impact on system performance.

4. Pylint has a pre-commit hook integrated into a PyCharm commit modal window
   (Cmd+K). Make sure the "Scan with Pylint" checkbox is enabled:

   <img src="figures/pycharm_pylint_pre_commit.png" width="700"/>

Note that PyCharm comes with very useful and advanced built-in inspections out
of the box; however, they don't fully overlap with pylint, so it's useful to
have both.
