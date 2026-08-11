# Homebrew

Homebrew is a package manager which can make software installations trivially easy on MacOS.

Homebrew's [website](https://brew.sh) contains details, and installation instructions.

## Install

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

If you have not previously installed the MacOS Command Line Tools (CLT) (`XCode`, either from the app store or `xcode-select --install`), they will be installed as part of this action. `XCode` installs git, gcc, and other software build tools.

## Usage

Installations with Homebrew are very simple, and should be considered as a first choice where possible, e.g.

```bash
brew install bcftools samtools
```
