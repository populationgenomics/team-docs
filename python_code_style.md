# Python Code Style

We use [pylint](https://www.pylint.org/) to perform automatic code checks on our repositories. It helps enforce code standard, and also does some static code analysis for potential programming errors.


## Setting up a new project

When creating a new repository that contains Python code, please add into the repository root folder a file named `.pylintrc` with the following contents:

```
[MESSAGES CONTROL]
# We disable the following inspections:
# 1. f-string-without-interpolation (we allow f-strings that don't do any formatting for consistent looks and for future safety)
# 2. inherit-non-class ("Inheriting 'NamedTuple', which is not a class" false positive, see: https://github.com/PyCQA/pylint/issues/3876)
# 3. too-few-public-methods (produces false positives)
disable=f-string-without-interpolation,inherit-non-class,too-few-public-methods

# Overriding these to allow short 1- or 2-letter variable names
attr-rgx=[a-z_][a-z0-9_]{0,30}$
argument-rgx=[a-z_][a-z0-9_]{0,30}$
variable-rgx=[a-z_][a-z0-9_]{0,30}$

# Maximum number of characters on a single line
max-line-length=80
```

You may want to disable additional inspections if pylint hits a false positive. For example, it might fail to recognise imports of third-party libraries, in which case can add E0401 ("Unable to import") to the comma-separated list:

```
disable=f-string-without-interpolation,inherit-non-class,too-few-public-methods,E0401
```

In addition to `.pylintrc`, please create a GitHub Actions CI workflow under `.github/workflows/main.yaml` with the following contents (or just append the job called `lint`, if you have an exsting workflow):

```
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main

      - uses: actions/setup-python@v2

      - name: Install pylint
        run: pip install pylint

      - name: Run pylint
        run: pylint **/*.py
```

This will make GitHub run Pylint on every push and pull request, and display checks in the web interface.

![github_pylint_check](assets/github_pylint_check.png)


## Running Pylint

To install Pylint into your environment, run:

```
pip install pylint
```

It's also available on conda-forge under the same name.

To run Pylint manually, you can use:

```
pylint **/*.py
```


## Visual Studio Code

Visual Studio Code auto-detects a .pylintrc file in the project root and asks the user whether to install pylint, if it's not installed already.


## PyCharm

1. Make sure you have pylint installed with pip or conda.

2. Install a PyCharm "Pylint" plugin ([Preferences] > [Plugins] > search for "Pylint"). It will automatically find the pylint executable. A new tool window called Pylint will be added. You can use it to scan the project:
   ![pycharm_pylint_tool_window](assets/pycharm_pylint_tool_window.png)   

3. You can also enable real-time inspections by going to:
   Go to Preferences > Editor > Inspections > enable "Pylint real-time scan". However, it's not recommended as it's has a negative impact on system performance.

4. Pylint has a pre-commit hook integrated into a Pycharm commit modal window (cmd+K). Make sure the "Scan with Pylint" checkbox is enabled:
   ![pycharm_pylint_pre_commit](assets/pycharm_pylint_pre_commit.png)

Note that PyCharm comes with very useful and advanced built-in inspections out of the box; however, they don't fully overlap with pylint, so it's useful to have both.
