Dataproc
========

.. note::

   Playbook of errors available: :doc:`../playbooks/hail_query_on_dataproc`

Dataproc is a managed Spark and Hadoop service provided by Google that we use for running Hail query analyses. For the most part, we want to use Query on Batch, but occasionally we must fallback to Dataproc.

The analysis-runner package includes helper functions for managing Dataproc clusters, including spinning up and down clusters, and submitting jobs.

.. code-block:: python

   from analysis_runner import dataproc
   from cpg_utils.hail_batch import get_batch

   b = get_batch()

   # this command adds 3 jobs to:
   #   1. Start the dataproc cluster
   #   2. Submit the file to the cluster, which:
   #       1. Checks out the repository you're currently in (at the specific commit of the repo you're in on run)
   #       2. Submits the file to the dataproc cluster using the hailctl command
   #   3. Shut down the cluster
   j = dataproc.hail_dataproc_job(
       batch=b,
       script=script,
       packages=['cpg_workflows', 'google', 'fsspec', 'gcloud'],
       num_workers=2,
       num_secondary_workers=20,
       job_name=job_name,
       depends_on=depends_on,
       scopes=['cloud-platform'],
       pyfiles=pyfiles,
   )

Docker driver image
--------------------

The dataproc image is effectively a driver image for the *setting up*, *submitting to*, and *spinning down* the cluster. It doesn't do anything too fancy, but it's useful to keep this disconnected from the regular analysis-runner driver image to avoid any arbitrary changes to pip_dependencies in the deploy_config (`/usr/local/lib/python3.10/dist-packages/hailtop/hailctl/deploy.yaml`).

Note that our `Hail fork <https://github.com/populationgenomics/hail>`_ at `HEAD` is used to build the image. You can use the `COMMIT_HASH` arg to build an image with a specific version of hail instead of the latest version, which is what `HEAD` will use.

We manually build our version of Hail in the dataproc container. (Ideally it would be good to use a multistage build process to reduce this image size, but we don't want to support dataproc into the indefinite future).

Spinning up a dataproc cluster
------------------------------

A dataproc cluster is spun up within a specific dataset's GCP project for billing reasons.

We call `hailctl dataproc start`, as configured in the `analysis_runner/dataproc` module. We specify a number of default packages in this module as a sensible default. We by default specify the init script (`gs://cpg-common-main/hail_dataproc/${HAIL_VERSION}/`), but you can override this on cluster configuration.

By default, Hail specifies the image to use on Dataproc. The image version comes from the command `dataproc cluster image version lists <https://cloud.google.com/dataproc/docs/concepts/versioning/dataproc-version-clusters#debian_images>`_, and is specified here: `hail:hail/python/hailtop/hailctl/dataproc/start.py#L147 <https://github.com/populationgenomics/hail/blob/main/hail/python/hailtop/hailctl/dataproc/start.py#L147>`_.

At the time of writing (2023-11-24), this was using Python 3.10.8.

Initialization script
~~~~~~~~~~~~~~~~~~~~~

The scripts in `init_scripts` are used to install dependencies on Dataproc master nodes through the `init` parameter of the `setup_dataproc` function. The scripts get copied to `gs://cpg-common-main/hail_dataproc/${HAIL_VERSION}` `automatically <../.github/workflows/copy_dataproc_init_scripts.yaml>`_ on pushes to `main`.

Updating dataproc
-----------------

When you're trying to update the default version of dataproc, you should:

1. Bump the `DEFAULT_HAIL_VERSION` in `analysis_runner/dataproc.py`
   * Side note: hail must be released before this happens, including the wheel at `gs://cpg-hail-ci/wheels/hail-{HAIL_VERSION}-py3-none-any.whl`
2. Completely release the analysis-runner CLI (merge to main with a bumpversion commit)
3. Rebuild the dataproc image, using the command below (#rebuilding-the-dataproc-driver-image)
4. Rebuild the analysis-runner driver image

Note, we support specifying the hail_version, but only a very select number of versions are available (due to the init scripts not always being updated).

Rebuilding the dataproc driver image
------------------------------------

.. code-block:: sh

   gcloud config set project analysis-runner
   # grab the HAIL_VERSION from analysis_runner/dataproc.py
   HAIL_VERSION=$(grep "DEFAULT_HAIL_VERSION = '" ../analysis_runner/dataproc.py | awk -F\' '{print $2}')

   # if from repo root
   cd dataproc
   gcloud builds submit \
     --timeout=1h \
     --tag=australia-southeast1-docker.pkg.dev/analysis-runner/images/dataproc:hail-$HAIL_VERSION \
     .


CPG-UTILS documentation
-----------------------
We use Dataproc (GCP flavoured Spark cluster) to run Hail Query. This module
provides utilities to interact with Dataproc (start, stop, submit jobs, etc).

.. automodule:: cpg_utils.dataproc
   :members:
   :undoc-members:
