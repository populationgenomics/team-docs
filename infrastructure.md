# CPG Infrastructure

## Dataset

A _dataset_ is a defined collection of resources, with an associated permissions group for controlling access. It has:

- A GCP project with associated billing thresholds
- A set of GCS buckets
- A set of secrets to manage access (access_group_cache, cromwell access keys)
- A set of GitHub repositories, whose code is allowed to access this data

## Components

- [Hail Batch](https://github.com/populationgenomics/hail)
- Hail Query (currently through Dataproc)
- [Analysis-runner](https://github.com/populationgenomics/analysis-runner)
    - A user submits a dataset, access_level, repo, commit and command to the analysis-runner,
    - The analysis-runner confirms the user has access to the _dataset_,
    - Using hail batch as the _service-account_ with the appropriate permissions, it checks out the repository at a specific commit
    - Runs the command on the freshly checked out repository: this often constructs a longer pipeline that's run in Hail Batch ("batch-in-batch").
- [Metamist server](https://github.com/populationgenomics/metamist): Stores metadata about participants, samples, sequences and families.
    - Manually managed MariaDB server (with system-versioned tables).
    - API layer hosted on Cloud Run, to check permissions and avoid direct access to SQL tables.
    - Permissions managed through secrets generated on Pulumi.
- [Cromwell](https://github.com/broadinstitute/cromwell): Used for running WDL workflows.
    - Access is only available through the analysis-runner.
    - A service account is provided to Cromwell, which runs the workflow as that service-account.
    - Eventually we'd like to replace our managed Cromwell with [Terra](https://terra.bio/) + [WorkFlow Launcher](https://broadinstitute.github.io/wfl/terra/)
- [Seqr](https://github.com/populationgenomics/seqr):
    - Django app - load balanced through a managed VM instance group.
        - Authentication using OAuth2 through the Identity-Aware Proxy.
    - Managed Elasticsearch - holds the annotated variant data, gets queried by the Django app. Managed through the GCP Marketplace.
    - Managed Postgres (Cloud SQL).
    - Reference database is updated using Cloud Scheduler and a separately hosted Cloud Run instance of _seqr_.

## Google Cloud Platform

To make sure we don't run into scalability limits with increasing dataset sizes,
we run all analyses at the Centre in a cloud computing environment. For now,
we're using Google Cloud Platform (GCP), since projects like Terra and Hail so
far work best on GCP.

To install the Google Cloud SDK: `brew install --cask google-cloud-sdk`

If you're new to GCP, read the excellent [How to Cloud](https://github.com/danking/hail-cloud-docs/blob/master/how-to-cloud.md) guide first.

For better isolation and cost accounting, we create separate GCP projects for each effort within the Centre. For example, the TOB-WGS effort would have a dedicated GCP project. It's important to keep in mind that the GCP project _name_ can be distinct from the dataset name (GCP project IDs must be unique, and as such often contain 6 digits, eg: `dataset-403812`. In general, when you specify projects, you'll have to use the GCP project ID (e.g. `gcloud config set project <project-id>`).

Permissions to projects and resources like Google Cloud Storage (GCS) buckets are managed using Google Groups that are linked to IAM permission roles. Take a look at our [storage policies](storage_policies/README.md) for a much more detailed description.

It's very important to avoid [network egress traffic](https://cloud.google.com/vpc/network-pricing#internet_egress) whenever possible: for example, copying 1 TB of data from the US to Australia costs 190 USD. To avoid these costs, always make sure that the GCP buckets that store your data are colocated with the machines that access the data (typically in the `australia-southeast1` region).

The exception to this rule are public buckets that don't have the [Requester Pays](https://cloud.google.com/storage/docs/requester-pays) feature enabled, such as `gs://genomics-public-data`, `gs://gcp-public-data--broad-references`, or `gs://gcp-public-data--gnomad`. Even though data is copied from the US to Australia when accessing these buckets, we don't get charged for the egress traffic.

_Important_: Please never copy non-public data from the corresponding GCP projects without getting approval first. For example, when copying data to an on-premise HPC system or your laptop, you've effectively changed the permission controls that were on the data. Not only does this increase the risk of data breaches, but such usage is generally not covered by our ethics approvals. Keep in mind that any non-public genomic data is highly sensitive. Leaving the data in the cloud also avoids incurring any egress costs that apply when downloading the data.

## Analysis platforms

### Hail + Hail batch

> See [Hail](hail.md) for more information

Hail Batch is our pipelining platform of choice. Our [production-pipelines](https://github.com/populationgenomics/production-pipelines) builds Hail Batch pipelines, you can visit [batch.hail.populationgenomics.org.au](https://batch.hail.populationgenomics.org.au) to visit our deployed GCP deployed instance.

Hail (query) is a python framework for manipulating genomics data in a highly parallelised environment (ie: Query on Batch, Spark / Dataproc).


### Cromwell

While Hail Batch is a very powerful way to define workflows especially when
using Hail Query functionality, a lot of existing genomic pipelines (like
Broad's GATK Best Practices Workflows) run on Cromwell.

While [Terra](https://terra.bio/) is a great way to run such workflows, there
are still a few features missing that would allow us to run production workflows
in Australia.

For now, the best way to run workflows written in WDL is therefore to use the analysis-runner, which is integrated with our Cromwell server.


## Permissions

We manage our permissions through Pulumi ([cpg-infrastructure](https://github.com/populationgenomics/cpg-infrastructure/blob/main/cpg_infra/driver.py)). All permissions are mirrored for each dataset. The [storage policies](storage_policies/README.md) document has more information about the different ways we store data in the CPG, but broadly, each dataset has two namespaces:

1. main - for all production data
2. test - for specific subsets, or synthetic data you can run unreviewed code on.

And three _access levels_:

- `full`: commit MUST be on the branch branch, allowed all operations on `dataset-main*` and `dataset-test` buckets
- `standard`: commit MUST be on the main branch, allowed READ / WRITE access to `dataset-main*` buckets
- `test`: can run any commit on the allowed repositories, on the `dataset-test*` buckets

If you want to affect genomics data, or metadata - you'll usually need to write a script, publish it to a populationgenomics repository and ask the [_analysis-runner_](getting_started.md#analysis-runner) to run that script for you. If you want to affect _main_ namespaced data, your script will need to be on the `main` branch (which requires a code review).


## Example: seqr loading pipeline

The seqr loading pipeline is good example, as it uses most components within the CPG's infrastructure.

This relies on the collaborator providing us their:

- Sequencing data (in fastqs, bams, or crams)
    - And uploaded to our `dataset-main*` GCS bucket.
- Relevant metadata having been uploaded to the sample-metadata system:
    - Including pedigree data, individual level metadata (eg: HPO terms)
    - The _seqr_ wizard will pass this metadata from seqr directly.

Entrypoint: [GH: hail-elasticsearch-pipelines::batch_seqr_loader/batch_workflow.py](https://github.com/populationgenomics/hail-elasticsearch-pipelines/blob/main/batch_seqr_loader/batch_workflow.py)

1. The batch_workflow script is submitted to the analysis-runner, to use `main` data.
1. This script uses the sample-metadata database to get the active samples for the current project.
1. The input data is validated:
    - Perform relatedness checks to check the pedigree matches the genetic data.
1. It uses state in the sample-metadata to work out which samples need to be:
    1. Aligned (in Hail Batch)
    2. Run germline short variant discovery to get SNPs and indels (ie: HaplotypeCaller, in Hail Batch)
    3. (Future) Call structural variants using GATK-SV (in Cromwell from Hail Batch)
1. Update the sample-metadata system as each of the previous results are available.
1. Joint-call the SNPs and Indel variants for the cohort using [`gatk GenotypeGVCFs`](https://github.com/populationgenomics/hail-elasticsearch-pipelines/blob/ddd3fd747bed12b2baedc067d92e8df332fca195/batch_seqr_loader/batch_workflow.py#L1655-L1656)
1. Spin up a dataproc cluster with vep and to run the hail pipeline `batch_seqr_loader/scripts/load_project_to_es.py`:
    1. Annotate the joint-call set with VEP and other clinical databases
    1. Export the annotated variants into a new index on the managed Elasticsearch instance

Now that the Elasticsearch index has been created:

- Link the seqr project with the new elasticsearch index:
    - Seqr queries ES to check for the newly added samples
- Link the aligned crams with the seqr project (for the embedded [IGV browser](https://software.broadinstitute.org/software/igv/))
