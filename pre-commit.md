# Setting up Pre-Commit

When creating a new Python code repository, the preferred approach is to create a new branch from the template repo
(see [new repository template](new_repository.md#Repository Template)). Where that is not possible e.g. adding
pre-commit to an existing repository, please add these configuration files into the root folder.

(you can skip the last 3 lines if your project is not going to contain any Python code):

```sh
# make sure you declare this variable since it is used throughout this document
URL_NEW_REPO=https://raw.githubusercontent.com/populationgenomics/team-docs/main/new_repository

wget $URL_NEW_REPO/pre-commit-config.yaml -O .pre-commit-config.yaml
wget $URL_NEW_REPO/markdownlint.json -O .markdownlint.json
wget $URL_NEW_REPO/pyproject.toml -O pyproject.toml
wget $URL_NEW_REPO/pylintrc -O .pylintrc
wget $URL_NEW_REPO/flake8 -O .flake8
```