# CPG Infrastructure

## Dataset

A *dataset* is a defined collection of resources, with an associated permissions group for controlling access. It has:

- A GCP project
- A set of GCS buckets
- A set of secrets to manage access (access_group_cache, cromwell access keys)
- A set of GitHub repositories, whose code is allowed to access this data

## Components

- [Hail Batch](https://github.com/populationgenomics/hail)
- Hail Query (currently through Dataproc)
- [Analysis-runner](https://github.com/populationgenomics/analysis-runner)
- [Sample-metadata server](https://github.com/populationgenomics/sample-metadata)
- [Cromwell](https://github.com/broadinstitute/cromwell)
- [Seqr](https://github.com/populationgenomics/seqr):
    - Elasticsearch - managed through the GCP Marketplace.
    - Postgres - managed through the Cloud SQL.
    - Authentication using OAuth2 through the Identity-Aware Proxy.


## Permissions

The [storage policies](storage_policies) document has more information about the different ways we store data in the CPG, but broadly, each dataset has three levels:

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
    - The _seqr_ wizard will pass this metadata from seqr directly.

Entrypoint: [GH: hail-elasticsearch-pipelines::batch_seqr_loader/batch_workflow.py](https://github.com/populationgenomics/hail-elasticsearch-pipelines/blob/main/batch_seqr_loader/batch_workflow.py)

1. The batch_workflow script is submitted to the analysis-runner, to use `main` data
1. This script uses the sample-metadata database to get the active samples for the current project.
1. The input data is validated:
    - Perform relatedness checks to check the pedigree matches the genetic data.
1. It uses state in the sample-metadata to work out which samples need to be:
    1. Aligned (in Hail Batch)
    2. Run germline short variant discovery to get SNPs and indels (ie: HaplotypeCaller, in Hail Batch)
    3. (Future) Call structural variants using GATK-SV (in Cromwell from Hail Batch)
1. Update the sample-metadata system as each of the previous results are available.
1. Spin up a dataproc cluster to joint-call the SNPs and Indel variants for the cohort:
    1. Run the variant combiner (in `Hail`) to add new samples to the latest joint-call set.
1. Spin up a dataproc cluster with vep, to run the hail pipeline `batch_seqr_loader/scripts/load_project_to_es.py`:
    1. Annotate the joint-call set with VEP and other clinical databases
    1. Export the annotated variants into a new index on the managed ElasticSearch instance

Now that the elastic search index has been created:

- Link the seqr project with the new elasticsearch index:
    - Seqr queries ES to check for the newly added samples
- Link the aligned crams with the seqr project (for the embedded [IGV browser](https://software.broadinstitute.org/software/igv/))