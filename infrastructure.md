# CPG Infrastructure

## Dataset

A *dataset* is a defined collection of resources, with an associated permissions group for controlling access. It has:

- A GCP project with associated billing thresholds
- A set of GCS buckets
- A set of secrets to manage access (access_group_cache, cromwell access keys)
- A set of GitHub repositories, whose code is allowed to access this data

## Components

- [Hail Batch](https://github.com/populationgenomics/hail)
- Hail Query (currently through Dataproc)
- [Analysis-runner](https://github.com/populationgenomics/analysis-runner)
    - A user submits a dataset, access_level, repo, commit and command to the analysis-runner,
    - The analysis-runner confirms the user has access to the *dataset*,
    - Using hail batch as the *service-account* with the appropriate permissions, it checks out the repository at a specific commit
    - Runs the command on the freshly checked out repository: this often constructs a longer pipeline that's run in Hail Batch ("batch-in-batch").
- [Sample-metadata server](https://github.com/populationgenomics/sample-metadata): Stores metadata about participants, samples, sequences and families.
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
    - Reference database is updated using Cloud Scheduler and a separately hosted Cloud Run instance of *seqr*.


## Permissions

We manage our permissions through Pulumi ([config](https://github.com/populationgenomics/analysis-runner/blob/main/stack/__main__.py)). All permissions are mirrored for each dataset. The [storage policies](storage_policies) document has more information about the different ways we store data in the CPG, but broadly, each dataset has three levels:

- `test`: can run any commit on the allowed repositories, on the `dataset-test*` buckets
- `standard`: commit MUST be on the main branch, allowed READ / WRITE access to `dataset-main*` buckets
- `full`: commit MUST be on the branch branch, allowed all operations on `dataset-main*` and `dataset-test` buckets

## Example: seqr loading pipeline

The seqr loading pipeline is good example, as it uses most components within the CPG's infrastructure.

This relies on the collaborator providing us their:

- Sequencing data (in fastqs, bams, or crams)
    - And uploaded to our `dataset-main*` GCS bucket.
- Relevant metadata having been uploaded to the sample-metadata system:
    - Including pedigree data, individual level metadata (eg: HPO terms)
    - The *seqr* wizard will pass this metadata from seqr directly.

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
- NB: These currently happen manually through reports generated by the sample-metadata server, but we want to action them.
