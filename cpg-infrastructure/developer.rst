CPG Infrastructure Developer Guide
===================================

Our CPG Infrastructure is our way of defining resources to make our analysis possible. This guide is intended for developers who want to contribute to the CPG Infrastructure. See the :doc:`user` for information on how to use the CPG Infrastructure.

Repository structure
--------------------

The core of our infrastructure is defined in `cpg-infrastructure <https://github.com/populationgenomics/cpg-infrastructure>`_, and is made up of 3 levels.

1. ``CPGInfrastructure``: 
    - Infrastructure defined ONCE CPG wide, so all datasets can reuse them. 
    - Manages group membership, see below for more details about that.
    - Coordinates the level below.
2. ``CPGDatasetInfrastructure``
    - Infrastructure defined ONCE for a specific dataset.
    - Pretty light, mostly the metamist project.
3. ``CPGDatasetCloudInfrastructure```
    - All the resources for a dataset, for each specific cloud provider.

Configuration
-------------

The CPG configures our infrastructure in a private repository, which is structured like:

- ``config-infrastructure.yaml``: 
    - Contains general configuration with org constants and cloud provider details.
- ``config-datasets.yaml``: 
    - Contains dataset specific configuration, like the dataset name, and the cloud environments to use for each dataset.
    - This matches the config.

    .. code-block:: yaml

       dataset:
         # other datasets this one need to READ but not write
         depends_on_readonly:
           - dataset-1
           - dataset-2
         # other datasets this one need to READ + WRITE
         depends_on:
           - dataset-3
         enable_release: true
         enable_shared_project: true
         # read the user.rst docs on these params
         is_internal_dataset: true
         gcp:
           project: dataset-gcp-project-id

- ``users.yaml``
    - Contains the users and their roles in the CPG infrastructure.
    - This is used to manage group memberships.

    .. code-block:: yaml

       firstname.lastname:
       can_access_internal_dataset_logs: true
       gcp:
         hail_batch_username: hailbatchusername
         # an email recognised by google identity, to add to google groups
         id: firstname.lastname@populationgenomics.org.au

- ``projects.yaml``
    - A list of legal projects / protocols that we use to double check people have access to the datasets. This isn't used in the infra code directly, it's a process check on top which blocks CI merges.

- ``Pulumi.production.yaml``
    - Contains the Pulumi configuration for the production environment.
    - Basically no extra information, except a pointer to the config.

- ``datasets/$DATASET/*``
    - ``budgets.yaml``
        - Contains the budgets for the dataset.
        - See [Budgets](../budgets.md) for more information.
    - ``members.yaml``
        - A map of a dataset group, to a list of users.
        - See the ``setup_externally_specified_members`` method for it's implementation.
    - ``repositories.yaml``:
        - A list of repositories for which you can run code against within the analysis-runner for this dataset. (Note, there are default repositories). 
        - This is implemented in ``tokens/main.py`` in cpg-infra-private.

Group membership
----------------

Groups are used to control access to resources and services. In most places, we add a group to a cloud resource, and let the cloud provider handle the rest. In other cases (like the web service / metamist / analysis-runner), we can't just lookup the group membership from the cloud provider (because it's slow, and it's a little tedious to add members not defined within that cloud), so we have a members cache (a file that stores the group members). 

We bring all group memberships under cpg-infrastructure, this allows us to:

- unwrap groups completely, hence we know the full list of users / accounts that need to access specific resources. 
- better version control and store history of group memberships. In the CPG's configuration, we have CODEOWNER policies to manage who can add / remove users from groups.


In code, we have a wrapper around a group, which is a list of GroupMember's, which is either a user or itself another group. We track which cloud we need to create the group for. At anytime you can request a full list of users, however the ID component might be a pulumi output value, eg: you can't know the service-account ID before you create it.

All dataset infrastructure methods can create groups, and add members to them, and at the very end, these group members are finalised, synced to the cloud resource, and any access group caches are updated.


How does it actually get deployed?
----------------------------------


In cpg-infrastructure-private, we have a deploy.yaml GitHub action. This:

- Installs the latest cpg-infrastructure package
- Runs the pulumi up command:
    - This internally runs the ``__main__.py`` file, which is the entry point for the pulumi program. This packages up all the configuration in the private repo into:

        1. A ``CPGInfrastructureConfig`` object, which contains users.
        2. A ``list[CPGDatasetConfig]`` objects, which contains the datasets to spin up. 

Puluim does the rest!


Previewing the workflow locally
-------------------------------

Prerequisites:

* Have installed:
    * Pulumi
    * google-cloud-sdk
    * azure-cli
* Get and export the pulumi access token from a CPG team-member
* Have both `cpg-infrastructure` and `cpg-infrastructure-private` cloned locally
* Set-up a python virtual environment, installed cpg-infrastructure.
    * Usually better to `pip install -e .` in the cpg-infrastructure directory.

Noting we set these environment variables:

- ``PULUMI_EXPERIMENTAL``: So we can use the skip checkpoints feature
- ``PULUMI_SKIP_CHECKPOINTS``: Allows us to skip checkpoints which take forever!

Some extra notes:

- The `--non-interactive` flag is important because the interactive mode breaks for how many resources we have
- The `--diff` flag is important because it shows us what pulumi is going to change, and it's a bug: https://github.com/pulumi/pulumi/issues/12162

.. code-block:: bash

    pulumi login gs://cpg-pulumi-state/
    pulumi stack init production

    PULUMI_EXPERIMENTAL=true PULUMI_SKIP_CHECKPOINTS=true pulumi preview \
        --non-interactive --diff -p 20
