CPG Infrastructure User Guide
=============================

This doc is a user guide for cpg-infrastructure configuration. See the :doc:`developer`. for information on how to developer the CPG infrastructure.

Overview
--------

The CPG infrastructure is a set of resources that make our analysis possible. It includes resources like buckets for data storage, groups, budget management, and all the permissions to access these resources.

The cpg-infrastructure-private is where all of our configuration lives. You can modify these files to change the configuration of the infrastructure, and it gets automatically released on merge.

Quick guide
------------

This section has a bunch of quick guides to get you started!

How do I add someone to a dataset?
++++++++++++++++++++++++++++++++++

1. Ensure the user is added to the ``users.yaml`` file.
2. Ensure the user is in a protocol/project in the ``projects.yaml`` file that covers the dataset.
    - This requires an approval from the PM team (to ensure onboarding requirements are met).
3. Ensure the user is added to the correct group in the ``config/DATASET/members.yaml`` file.
    - This requires an approval from the dataset owner.

Example PR: https://github.com/populationgenomics/cpg-infrastructure-private/pull/340

What groups can I add a user to?
++++++++++++++++++++++++++++++++

- ``web-access``
    - Access to web reports via the web server (main-web.populationgenomics.org.au/dataset/...)
- ``upload``
    - Read + Write permissions to the upload buckets
- ``metadata-access``
    - Read metadata in metamist, including access to the metamist UI
- ``metadata-write``
    - Read + write metadata in metamist (includes test projects)
- ``analysis``
    - Read metadata in metamist
    - Read permissions to the main analysis buckets
    - List permissions to all other main buckets
    - Read + write permissions to test buckets
    - Other permissions directly related to analysis, eg: dataproc logs
- ``data-manager``
    - All permissions from analysis
    - Read access to main buckets
    - Write access to metadata
    - Ability to generate credentials for the shared projects

- ``release-access``
    - Ability to read from the release bucket


How do I add a new dataset?
++++++++++++++++++++++++++++

You can run the handy ``scripts/create_dataset.py`` script, which creates _most_ of the entries needed to spin up a dataset on merge.

Some common options:

- ``--dataset DATASET``: The name of the dataset.
- ``--add-as-rare-disease-dependency``: Add the dataset as a dependency to the rare disease dataset (which basically adds it to seqr).
- ``--budget 100``: The monthly budget in AUD for the dataset.

.. code-block :: bash

    python scripts/create_dataset.py \
        --dataset $DATASET \
        -- budget 100 \
        --add-as-rare-disease-dependency


Common errors, and how to fix them
++++++++++++++++++++++++++++++++++

User USER is not in the users.yaml file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A user was added to a members.yaml file, but the system couldn't find them in the users.yaml file. Make sure you add the user to the users.yaml file.

DATASET: Has user USER but, but there are no projects / protocols
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dataset didn't have any protocols / projects in the projects.yaml file. You'll need to talk to the PM team about which protocol best covers your new dataset.

(This error is more common on dataset creation).

DATASET: USER does not have any of the required projects: PROJECT1, PROJECT2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A user was added to a dataset, but they didn't have any of the required projects / protocols in the projects.yaml file. You'll need to add them to one of the listed projects, and get approval from the PM team.

You should reach out to your team-lead / the PM team for help with this.


What's the ``projects.yaml``?
------------------------------

The ``projects.yaml`` file is a list of legal projects / protocols that we use to double check people have access to the datasets. This isn't used in the infra code directly, it's a process check on top which blocks CI merges.

For example, if USER1 wants access to DATASET, they must fulfill the legal onboarding requirements of PROJECT1, which could include undertaking specific training, or signing a legal agreement.

Note:

* there may be multiple protocols that cover a dataset (eg: a project may have a protocol for each institution).

* a protocol may cover multiple datasets, which may often happen for some grants.


The projects.yaml file is maintained by the PM team, hence any change to that file must be approved by the PM team.

A project looks like this:

.. code-block :: yaml

   protocol-name:
     name: A test protocol that covers the dataset
     datasets:
       - DATASET1
     members:
       - user.name
       - user2.name



If this file isn't filled out correctly, you will get an automated comment on your PR. Some common error messages with the solution are listed above.
