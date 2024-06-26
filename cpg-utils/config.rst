Configuration
=============

.. note::
   Scroll to the bottom of this document for the API reference.

The ```cpg-utils`` library <https://github.com/populationgenomics/cpg-utils>`__
(`pypi <https://pypi.org/project/cpg-utils/>`__) contains a streamlined
config management tool. This config management is used by most
production CPG workflows, but is useful in projects or scripts at any
scale.

This allows you to run the same code, across multiple datasets,
namespaces and even clouds without any change to your code.
Configurations like this can make it tricky to work out exactly where
parameters come from, we recommend:

-  Putting the parameter on the CLI if the value is unique for each run
-  Putting the parameter in a config if it's useful for many runs to
   have this value, and it changes predictably with the dataset.
-  And we discourage using environment variables to pass around information.

This configuration tool uses one or more ``TOML`` files, and creates a
dictionary of key-value attributes which can be accessed at any point,
without explicitly passing a configuration object. If jobs are set up
using ``analysis-runner``, config will be set up automatically within
each job environment. Please see the end section of this document for
extra details on how to set up config outside analysis-runner.

Configs and the analysis-runner
-------------------------------

The analysis-runner is the entry point to analysis at the CPG, but it’s
secondary role is to combine a bunch of configs together for your
analysis.

This includes:

-  Storage configuration generated by the
   `cpg-infrastructure <https://github.com/populationgenomics/cpg-infrastructure/blob/e25cb54d4c81a03e91270bf2165143ac798de09d/cpg_infra/driver.py#L1120>`__
-  Selected configuration attributes (also from
   `cpg-infrastructure <https://github.com/populationgenomics/cpg-infrastructure/blob/e25cb54d4c81a03e91270bf2165143ac798de09d/cpg_infra/driver.py#L495-L502>`__)
-  `Images <https://github.com/populationgenomics/images/blob/main/images.toml>`__
-  `References <https://github.com/populationgenomics/references>`__

The `analysis-runner
server <https://github.com/populationgenomics/analysis-runner/blob/23989ca333d1c31e5e502e3643e3295fff31518e/server/util.py#L263-L267>`__ combines
all of these configs together.

You can generate an example config using the ``analysis-runner config``
command:

.. code:: shell

   analysis-runner config --help

   # usage: config subparser [-h] --dataset DATASET -o OUTPUT_DIR [--access-level {test,standard,full}] [--image IMAGE] [--config CONFIG] [--config-output CONFIG_OUTPUT]
   #
   # options:
   #   -h, --help            show this help message and exit
   #   --dataset DATASET     The dataset name, which determines which analysis-runner server to send the request to.
   #   -o OUTPUT_DIR, --output-dir OUTPUT_DIR
   #                         The output directory within the bucket. This should not contain a prefix like "gs://cpg-fewgenomes-main/".
   #   --access-level {test,standard,full}
   #                         Which permissions to grant when running the job.
   #   --image IMAGE         Image name, if using standard / full access levels, this must start with australia-southeast1-docker.pkg.dev/cpg-common/
   #   --config CONFIG       Paths to a configurations in TOML format, which will be merged from left to right order (cloudpathlib.AnyPath-compatible paths are supported). The analysis-runner will add the default
   #                         environment-related options to this dictionary and make it available to the batch.
   #   --config-output CONFIG_OUTPUT
   #                         Output path to write the generated config to (in YAML)

TOML
----

`Tom’s Obvious, Minimal Language <https://toml.io/en/>`__ is a config
file format designed to be easily human readable and writeable, with
clear data structures. Sections are delineated using bracketed headings,
and key-value pairs are defined using ``=`` syntax, e.g. :

.. code:: toml

   global_key = "value"

   [heading_1]
   name = "Luke Skywalker"
   age = 53

   [heading_1.subheading]
   occupation = ["Jedi", "Hermit", "Force Ghost"]

will be digested into the dictionary:

.. code:: python

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

Config in Analysis-Runner jobs
------------------------------

Analysis-runner incorporates a simple interface for config setting. When
setting off a job, the flag ``--config`` can be used, pointing to a
config file (local, or within GCP and accessible with current logged-in
credentials).

The ``--config`` flag can be used multiple times, which will cause the
argument files to be `aggregated <#config-aggregation>`__ in the order
they are defined. When ``--config`` is set in this way, the job-runner
performs the following actions:

1. Locally (where ``analysis-runner`` is invoked), a `merged
   configuration file is
   generated <https://github.com/populationgenomics/analysis-runner/blob/main/analysis_runner/cli_analysisrunner.py#L199-L201>`__,
   creating a single dictionary
2. This dictionary is sent with the job definition to the execution
   server
3. The merged data is saved in TOML format to a GCP path
4. The env. variable ``CPG_CONFIG_PATH`` is set to this new TOML
   location
5. Within the driver image ``get_config()`` can be called safely with no
   further config setting

If batch jobs are run in containers, passing the environment variable to
those containers will allow the same configuration file to be used
throughout the Hail Batch. The ``cpg-utils.hail_batch.copy_common_env``
`method <https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/hail_batch.py#L54>`__
facilitates this environment duplication, and `container
authentication <https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/hail_batch.py#L427-L454>`__
is required to make the file path in GCP accessible.

Even without additional configurations, analysis-runner will insert
infrastructure and run-specific attributes, e.g.

-  ``config_retrieve(['workflow', 'access_level'])`` e.g. test, or standard
   - OR ``get_access_level()`` gives the same result
-  ``config_retrieve(['workflow', 'dataset'])`` e.g. tob-wgs, or acute-care

Config aggregation
------------------

When passing the Analysis-runner multiple configs, the configs defined
earlier are used as a base that is updated with values from configs
defined later. New content is added, and content with the exact same key
is updated/replaced, e.g.

Base file:

.. code:: toml

   [file]
   name = "first.toml"
   [content]
   square = 4

Second file:

.. code:: toml

   [file]
   name = "second.toml"
   [content]
   triangle = 3

Result:

.. code:: toml

   [file]
   name = "second.toml"
   [content]
   square = 4
   triangle = 3

It’s important to note that the config files are loaded ‘left-to-right’,
so when multiple configuration files are loaded, only the right-most
value for any overlapping keys will be retained.

Reading config
--------------

To use the ``cpg_utils.config`` functions, import ``get_config`` into
any code:

.. code:: python

   from cpg_utils.config import get_config

The first call to ``get_config`` sets the global config dictionary and
returns the content, subsequent calls will just return the config
dictionary.

.. code:: python

   assert get_config()['file'] == 'second.toml'

Because configuration is loaded lazily, start-up overhead is minimal,
but can result in late failures if files with invalid content are
specified.

Config outside Analysis-Runner
------------------------------

The config utility can be used outside ``analysis-runner`` and CPG
infrastructure, requiring the user to manually set the config file(s) to
be read. Configuration files can be set in two ways:

1. Set the ``CPG_CONFIG_PATH`` environment variable
2. Use ``set_config_paths`` to point to one or more config TOMLs:

   -  ``from cpg_utils.config import set_config_paths``

You can refer to `the example configuration
TOML <cpg_config_example.toml>`__ in this repository and use it as a
template.

--------------

API Reference
-------------

.. automodule:: cpg_utils.config
   :members:
   :undoc-members:
