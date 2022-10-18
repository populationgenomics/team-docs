# Configuration

The [cpg-utils library](https://github.com/populationgenomics/cpg-utils) ([pypi](https://pypi.org/project/cpg-utils/)) contains a streamlined config management tool. This config management is used by most production CPG workflows, but is useful in projects or scripts at any scale.

This configuration tool uses one or more `TOML` files, and creates a dictionary of key-value attributes which can be accessed at any point, without explicitly passing a configuration object.

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

will be digested into the simple dictionary:

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

## Using cpg-utils.config

To use the `cpg-utils.config` functions, import these two key methods into any script:

```python
from cpg_utils.config import get_config, set_config_paths
```

Configuration is loaded lazily, so config files are loaded into memory only when we try to retrieve values from them. This reduces start-up overhead for scripts using this config approach, but can result in late failures if files with invalid content are specified.

### Setting configuration content

Configuration files can be set in two ways:

1. Set the `CPG_CONFIG_PATH` environment variable
2. Use `set_config_paths` to point to one or more config TOMLs

`CPG_CONFIG_PATH` can be a comma-delimited String, and the argument to `set_config_paths` is a list of `strings`. The
config functionality allows for multiple files to be specified, applied in the following way:

1. The cpg-utils repository contains a template config,
[toml template](https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/config-template.toml); this is loaded first and becomes the base config.
2. For each additional config file in order, recursively update the base config with further content. New content is added, and content with the exact same key is updated/replaced.

#### config loading example

First file:

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

### Getting configuration content

Once configuration paths are set, values can be retrieved at any point using `get_config`. The first call to `get_config` sets the global config dictionary and returns the content, subsequent calls will just return the config dictionary.

```python
assert get_config()['file'] == 'second.toml'
```

## Analysis-Runner

Analysis-runner incorporates a simple interface for config setting. When setting off a job, the flag `--config` can be used, pointing to a config file (local, or within GCP and accessible with current logged-in credentials).
The `--config` flag can be used multiple times, which will cause the argument files to be aggregated in the order they are defined. When `--config` is set in this way, the job-runner performs the following actions:

1. Locally (where `analysis-runner` is invoked), a [merged configuration file is generated](https://github.com/populationgenomics/analysis-runner/blob/main/analysis_runner/cli_analysisrunner.py#L199-L201), creating a single dictionary
2. This dictionary is sent with the job definition to the execution server
3. The data is saved in TOML format to a dataset-specific temporary location in GCP
4. The env. variable `CPG_CONFIG_PATH` is set to this new TOML location
5. Within the driver image `get_config()` can be called safely with no further manual config setting

If batch jobs are run in containers, passing the environment variable to those containers will allow the same configuration file to be used throughout the Hail Batch. The `cpg-utils.hail_batch.copy_common_env` [method](https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/hail_batch.py#L54) facilitates this environment duplication, and [container authentication](https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/hail_batch.py#L427-L454) is required to make the file path in GCP accessible.
