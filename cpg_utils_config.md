# Configuration

The [`cpg-utils` library](https://github.com/populationgenomics/cpg-utils) ([pypi](https://pypi.org/project/cpg-utils/)) contains a streamlined config management tool. This config management is used by most production CPG workflows, but is useful in projects or scripts at any scale.

This configuration tool uses one or more `TOML` files, and creates a dictionary of key-value attributes which can be accessed at any point, without explicitly passing a configuration object. If jobs are set up using `analysis-runner`, config will be set up automatically within each job environment. Please see the end section of this document for extra details on how to set up config outside analysis-runner. 

## TOML

[Tom's Obvious, Minimal Language](https://toml.io/en/) is a config file format designed to be easily human readable and writeable, with clear data structures. Sections are delineated using bracketed headings, and key-value pairs are defined using `=` syntax, e.g. :

```toml
global_key = "value"

[heading_1]
name = "Luke Skywalker"
age = 53

[heading_1.subheading]
occupation = ["Jedi", "Hermit", "Force Ghost"]
```

will be digested into the dictionary:

```python
{
    'global_key': 'value',
    'heading_1': {
        'name': 'Luke Skywalker',
        'age': 53,
        'subheading': {
            'occupation': ["Jedi", "Hermit", "Force Ghost"]
        }
    }
}
```


## Config Template

The `cpg-utils` repository contains a template config, [toml template](https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/config-template.toml). This is always loaded first and becomes the base config content. For each additional config file in order, the base config is updated with further content. New content is added, and content with the exact same key is updated/replaced, e.g.

Base file:

```toml
[file]
name = "first.toml"
[content]
square = 4
```

Second file:

```toml
[file]
name = "second.toml"
[content]
triangle = 3
```

Result:

```python
{
    'file': 'second.toml',
    'content': {
        'square': 4,
        'triangle': 3
    }
}
```

It's important to note that the config files are loaded 'left-to-right', so when multiple configuration files are loaded, only the right-most value for any overlapping keys will be retained.  

This configuration template contains a number of 'live' attributes, as well as many which are commented out (which is permitted in TOML). These commented out attributes provide examples of useful content in the configuration file, and logical places to place them in the overall config structure (e.g. many examples of content expected to appear in `['workflow']`). If you find a useful config parameter missing from the base template, please create a PR adding new content into the template.



## Config in Analysis-Runner jobs

Analysis-runner incorporates a simple interface for config setting. When setting off a job, the flag `--config` can be used, pointing to a config file (local, or within GCP and accessible with current logged-in credentials).
The `--config` flag can be used multiple times, which will cause the argument files to be aggregated in the order they are defined. When `--config` is set in this way, the job-runner performs the following actions:

1. Locally (where `analysis-runner` is invoked), a [merged configuration file is generated](https://github.com/populationgenomics/analysis-runner/blob/main/analysis_runner/cli_analysisrunner.py#L199-L201), creating a single dictionary
2. This dictionary is sent with the job definition to the execution server
3. The merged data is saved in TOML format to a GCP path
4. The env. variable `CPG_CONFIG_PATH` is set to this new TOML location
5. Within the driver image `get_config()` can be called safely with no further config setting

If batch jobs are run in containers, passing the environment variable to those containers will allow the same configuration file to be used throughout the Hail Batch. The `cpg-utils.hail_batch.copy_common_env` [method](https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/hail_batch.py#L54) facilitates this environment duplication, and [container authentication](https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/hail_batch.py#L427-L454) is required to make the file path in GCP accessible.

Even without additional configurations, analysis-runner will load the template, and supplement with run-specific attributes, e.g.

- `get_config()['workflow']['access_level']` e.g. test, or standard
- `get_config()['workflow']['dataset']` e.g. tob-wgs, or acute-care

## Reading config

To use the `cpg_utils.config` functions, import `get_config` into any code:

```python
from cpg_utils.config import get_config
```

The first call to `get_config` sets the global config dictionary and returns the content, subsequent calls will just return the config dictionary.

```python
assert get_config()['file'] == 'second.toml'
```

Because configuration is loaded lazily, start-up overhead is minimal, but can result in late failures if files with invalid content are specified.

---

## Config outside Analysis-Runner

The config utility can be used outside `analysis-runner`, requiring the user to manually set the config file(s) to be read. Configuration files can be set in two ways:

1. Set the `CPG_CONFIG_PATH` environment variable
2. Use `set_config_paths` to point to one or more config TOMLs
    - `from cpg_utils.config import set_config_paths`  

When configuration is loaded outside `analysis-runner`, the content is still loaded on top of the base template in the `cpg-utils` package.