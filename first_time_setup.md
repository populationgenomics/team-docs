# Setup

This identifies a couple of key steps in setting up your new laptop for authenticating against and interacting with CPG resources. Some are essential for interacting with compute and data, some are personal preference.

## Terminal

If you are involved with data analysis or infrastructure management, you will spend a lot of time on the terminal. The MacOs default `Terminal` application is fine, but [ITerm2](https://iterm2.com/) should be strongly considered due to its wealth of advanced features (dividing tabs into split-panes, improved text search, command autocomplete, password manager, easily accessed command history, and more).

## Homebrew

See the [Homebrew page](homebrew.md) for instructions on how to install this handy package manager.

## XCode

If you install `Homebrew`, you won't need to install XCode manually. If you avoid Homebrew, XCode is a collection of MacOS developer tools (git, make, various compilers). You can install XCode from the [App Store](https://apps.apple.com/au/app/xcode/id497799835?l=en-GB&mt=12Xcode), or from the command line:

```bash
xcode-select --install
```

Once XCode is installed, you may need to activate your installation by agreeing to the software license agreement. Running `gcc` in a terminal will prompt you to run the license prompt, or you can access it directly through:

```commandline
sudo xcodebuild -license
```

## GCloud

The GCloud SDK is the main way to interact with Google Compute Resources through the command line, and the way to authenticate various applications to enable usage of the Google APIS. See [Gcloud](gcloud.md) for instructions.

## Analysis-Runner

At CPG we don't typically permit analysts to deploy jobs or scripts directly. Instead we have [Analysis-Runner](https://github.com/populationgenomics/analysis-runner) to broker interactions between the User and Cloud compute. The handy command line tool can be installed as a python package:

```bash
pip install analysis-runner
# or
uv pip install analysis-runner
```

In environments with `analysis-runner` installed you will be able to access the handy client using the `analysis-runner` command. See the [analysis-runner exercise](exercise-analysis-runner/README.md) for a worked example.

## Docker

[Docker](https://www.docker.com/) is a software containerisation tool, frequently used to build Docker Images for running software in Google's Cloud infrastructure.

>**Note**: When Docker images are built, they are compiled for a specific platform (i.e. a Docker Image built for Apple Silicon may not work as expected on Intel processors). You should always build a Docker Image for the hardware it is intended to be deployed on.

You can install Docker using [Homebrew](homebrew.md), or you can download [Docker Desktop](https://www.docker.com/products/docker-desktop/) to add a graphical user interface.

Most of our images are built using Continuous Integration (CI) workflows in GitHub, which ensures the build and deployment infrastructure are aligned. This can also result in much faster build times.

If you want to pull (or push) Docker Images from the GCP Artifactory, you will need to first install [GCloud](#gcloud), then you will need to configure your local Docker installation to use GCloud as an authentication method:

```commandline
gcloud auth configure-docker australia-southeast1-docker.pkg.dev
```

## BCFtools and SAMtools

If you interact with genomic data formats, locally or in GCS, you will likely use both BCFtools and SAMtools. See the [setup guide here](bcftools_and_samtools.md), noting that for most users the majority of that guide can be replaced with a simple [Homebrew](homebrew.md) installation. The [Authentication](bcftools_and_samtools.md#auth-token) section would be relevant for all users interacting directly with files in GCP.

## Other Installations

Depending on the institute your hardware has been provided by, the restrictions may vary. If your device was provided by Garvan IT, you should have a taskbar daemon called `Endpoint Privilege Management`. When you try to install software this will often pop up, prompting you to provide a reason for the action, usually "required for a one-time installation" will remove the block and allow you to complete an installation.
