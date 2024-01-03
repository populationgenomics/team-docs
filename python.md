# Python at the CPG

The CPG is mostly a Python shop! We strongly recommend using virtual environments (over conda) to manage Python.

We try to stay relatively up-to-date, most of our tools use Python 3.10 (with a few rare 3.8 exceptions), some are using 3.11 and 3.12. This can be super confusing!

## Managing Python versions

We strongly recommend using `pyenv` to manage versions of Python. This makes it really easy to install and manage multiple versions:

```shell
brew install pyenv

pyenv install 3.10.12
pyenv global 3.10.12
```

### Named virtual environments

If you like named virtual environments (rather than many `env/` directories in your repos), take inspiration from this snippet you could add to your `.zshrc` file:

```bash
export VIRTUALENV_DIR="$HOME/.venv"

if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi

function venv() {
  if test -f "$VIRTUALENV_DIR/$@/bin/activate"; then
    source $VIRTUALENV_DIR/$@/bin/activate
  else
    # have to use (pyenv which python3) otherwise old conda could take over
    virtualenv -p $(pyenv which python3) $VIRTUALENV_DIR/$@/ && source $VIRTUALENV_DIR/$@/bin/activate
  fi
}
function activate() {
  source $VIRTUALENV_DIR/$@/bin/activate
}
alias venvlist="ls $VIRTUALENV_DIR && echo 'You can activate one of these virtualenvs with: activate <env>'"

# allow autocomplete of `activate <name>`
_activate_completion() {
    local cur_word="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=($(compgen -W "$(ls $VIRTUALENV_DIR | grep "^$cur_word")" -- "$cur_word"))
}
complete -F _activate_completion activate
```

## Visual Studio Code

See [Code editors](code_editors.md#vscode---python) for more information on configuring Python in VSCode.
