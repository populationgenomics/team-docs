# Terminal

Tip on setting up your terminal and shell.

## Shell prompt

When working with tools like conda, git, gcloud, hail, you might need to frequently
switch between conda environments, git branches, Google Cloud projects, and Hail namespaces.
It's helpful to have them always displayed in your prompt. The following will work for
bash and [zsh](https://ohmyz.sh/) shells, and might be adapted for other shells
as well. Add this into your `.zshrc`, `.bashrc` or analogous:

```sh
git_rev() {
  # Returns current HEAD: either branch, or commit hash if detached.
  if [ ! -d .git ]; then echo ""; fi
  BRANCH=$(git branch --show-current)
  if [ -z $BRANCH ]
    then REV=$(git rev-parse --short HEAD)
    else REV=$BRANCH
  fi
  echo "$REV"
}

gcp_project() {
  # Returns current project, set with `gcloud config set project`.
  # Note: calling `gcloud config get-value project` is very slow, so parsing a file.
  PROJECT=$(grep project ~/.config/gcloud/configurations/config_default | sed 's/project = //')
  echo "$PROJECT"
}
conda_env() {
  # Returns current activated conda environment, assuming it's activated
  # with `conda activate`. For deactivated state, returns "base" or empty string.
  echo "$CONDA_DEFAULT_ENV"
}
hail_namespace() {
  # Returns current hail namespace set with `hailctl dev config set default_namespace`.
  echo "$(cat ~/.hail/deploy-config.json | jq -r ".default_namespace")"
}
_statuses() {
  echo "$(hail_namespace)·$(git_rev)·$(gcp_project)·$(conda_env)"
}

# For zsh:
PROMPT='%~%  $(_statuses) $ '  # %~% resolves to the home directory starting with ~. To show the absolute path, use %/%
# For bash:
PS1='\w  $(_statuses) $ '
```

You can add some colors:

```sh
PROMPT='%{$fg[cyan]%}%~%  %{$fg[yellow]%}$(_statuses)%{$reset_color%} $ '
PS1='\[\033[00;36m\]\w\[\033[00m\] \[\033[00;33m\]$(_statuses)\[\033[00m\] $ '
```

For more details on bash colors, [there are helpful articles](https://www.howtogeek.com/307701/how-to-customize-and-colorize-your-bash-prompt/).

It can be also useful to use color code to show the last command return value. In zsh, it can be done with:

```sh
PROMPT='%{$fg[cyan]%}%~%  %{$fg[yellow]%}$(_statuses)%{$reset_color%} %(?.%{$fg[green]%}.%{$fg[red]%})%B$%b '
```

Also, if you are using the a zsh [git-prompt plugin](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/git-prompt),
you can call `$(git_super_status)` instead `$(git_rev)`:

```sh
plugins=(<other plugins> git-prompt)
ZSH_THEME_GIT_PROMPT_PREFIX=""  # remove left parenthesis around git_super_status
ZSH_THEME_GIT_PROMPT_SUFFIX=""  # remove right parenthesis around git_super_status
_statuses() {
  echo "$(hail_namespace)·$(git_super_status)·$(gcp_project)·$(conda_env)"
}
```
