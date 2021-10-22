# CPG Infrastructure

## Dataset

A dataset is one defined collection of resources. It has:

- A GCP project
- A set of buckets
- A set of secrets to manage access (access_group_cache, cromwell access keys)
- A set of allowed_repositories

## Components

- Hail query / batch
- Analysis-runner
- Sample-metadata server


## Permissions

The [storage policies](storage_policies) document has more information about the different ways we store data in the CPG, but broadly, each dataset has three levels:

- `test`: can run any commit on the allowed repositories, on the `dataset-test*` buckets
- `standard`: commit MUST be on the main branch, allowed READ / WRITE access to `dataset-main*` buckets
- `full`: commit MUST be on the branch branch, allowed all operations on `dataset-main*` and `dataset-test` buckets

## Example: seqr loading pipeline

The seqr loading pipeline is good example, as it uses almost every single piece of architecture that the CPG offers.

This relies on:

- samples being loaded into a `dataset-main*` bucket
- sample metadata being loaded into the sample-metadata system
    - Including pedigree data, individual level metadata (eg: HPO terms)

Entrypoint: [GH: hail-elasticsearch-pipelines::batch_seqr_loader/batch_workflow.py](https://github.com/populationgenomics/hail-elasticsearch-pipelines/blob/main/batch_seqr_loader/batch_workflow.py)

1. The batch_workflow script is submitted to the analysis-runner, to use `main` data
1. This script first contacts the sample-metadata system to get the active samples for the current project.
1. It uses state in the sample-metadata to work out which samples still need to realigned, and variant called
1. After potential alignment and variant calling, it determines the samples to add to the joint-call
1. Spin up a dataproc cluster with vep, and submit `batch_seqr_loader/scripts/load_project_to_es.py` to the dataproc cluster.
1. The `load_project_to_es` workflow uses hail to annotate the joint-call set with VEP, and a number of other clinical databases, before loading into elasticsearch.

Now that the elastic search index has been created:

- The seqr project can be created (if not already),
- Export the following from the sample-metadata server and load into seqr:
    - Pedigree
    - (_in-progress_) family phenotypes
    - Individual ID,Cram path,Internal SampleID map
    - Participant-id to internal sample id map, import with the ES index name
    - Individual level metadata
