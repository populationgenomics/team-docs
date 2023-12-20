# Welcome to the CPG

This document describes the commonly used technologies at the Centre, together
with some hints on how to use various tools.

- [Welcome to the CPG](#welcome-to-the-cpg)
  - [Google Cloud Platform](#google-cloud-platform)
  - [Hail](#hail)
  - [Hail Batch](#hail-batch)
    - [Analysis runner](#analysis-runner)
  - [Terra / Cromwell](#terra--cromwell)

## Brew

If you're on Mac, then `brew` is a great way to install lots of software - this guide will provide instructions using Brew.

## Google Cloud Platform

To make sure we don't run into scalability limits with increasing dataset sizes,
we run all analyses at the Centre in a cloud computing environment. For now,
we're using Google Cloud Platform (GCP), since projects like Terra and Hail so
far work best on GCP.

To install the Google Cloud SDK: `brew install --cask google-cloud-sdk`

If you're new to GCP, read the excellent [How to Cloud](https://github.com/danking/hail-cloud-docs/blob/master/how-to-cloud.md) guide first.

For better isolation and cost accounting, we create separate GCP projects for each effort within the Centre. For example, the TOB-WGS effort would have a dedicated GCP project called `tob-wgs`. It's important to keep in mind that the GCP project _name_ can be distinct from the project _ID_. In general, when you specify projects, you'll have to use the project ID (e.g. `gcloud config set project <project-id>`).

Permissions to projects and resources like Google Cloud Storage (GCS) buckets are managed using Google Groups that are linked to IAM permission roles. Take a look at our [storage policies](storage_policies) for a much more detailed description.

It's very important to avoid
[network egress traffic](https://cloud.google.com/vpc/network-pricing#internet_egress) whenever possible: for example, copying 1 TB of data from the US to Australia costs 190 USD. To avoid these costs, always make sure that the GCP buckets that store your data are colocated with the machines that access the data (typically in the `australia-southeast1` region).

The exception to this rule are public buckets that don't have the [Requester Pays](https://cloud.google.com/storage/docs/requester-pays) feature enabled, such as `gs://genomics-public-data`, `gs://gcp-public-data--broad-references`, or `gs://gcp-public-data--gnomad`. Even though data is copied from the US to Australia when accessing these buckets, we don't get charged for the egress traffic.

_Important_: Please never copy non-public data from the corresponding GCP projects without getting approval first. For example, when copying data to an on-premise HPC system or your laptop, you've effectively changed the permission controls that were on the data. Not only does this increase the risk of data breaches, but such usage is generally not covered by our ethics approvals. Keep in mind that any non-public genomic data is highly sensitive. Leaving the data in the cloud also avoids incurring any egress costs that apply when downloading the data.

## Genomics overview

If you're new to genomics (or would be interested in a refresher) you might like to explore the [learngenomics.dev](https://learngenomics.dev/) resource.

It was written by and for computer scientists and engineers, and provides an awesome overview of pertinent biological concepts.

Note, while the resource approaches the topics from the lens of cancer genomics, most of the topics are still very relevant to our current work.

### Hail

> See [Hail](/hail.md) for more information

### Analysis runner

We don't allow users to run scripts directly on genomics data, we require code to be commited, reviewed, and then ran. The analysis-runner is the mechanism we use for that indrection. The analysis-runner builds a Batch pipeline from a specific commit in a GitHub repository.

There's a handy CLI tool too (`pip install analysis-runner`)

Make sure you have:

- the name of the [dataset](storage_policies), as this controls what data you can access and which code repositories are available,
- authenticated with your GCP account using `gcloud auth application-default login`,
- ensured your `@populationgenomics.org.au` account has been added to the permission group corresponding to the dataset (ask in the `#team-data` channel if you need to get access).
- You're in the repository you're trying to submit code from (the CLI will automatically detect the repo / commit).

Example:

```bash
# What you would use to run Batch directly:
# python3 path/to/myscript.py -p 3

# Using the analysis runner instead:
analysis-runner \
    --dataset <dataset> \
    --description "Description of the run" \
    --access-level <level>
    --output-dir <directory-within-bucket> \
    python3 path/to/myscript.py -p 3
```

See the [analysis runner documentation](https://github.com/populationgenomics/analysis-runner#cli) for more information.

## Terra / Cromwell

While Hail Batch is a very powerful way to define workflows especially when
using Hail Query functionality, a lot of existing genomic pipelines (like
Broad's GATK Best Practices Workflows) run on Cromwell.

While [Terra](https://terra.bio/) is a great way to run such workflows, there
are still a few features missing that would allow us to run production workflows
in Australia.

For now, the best way to run workflows written in WDL is therefore to use the analysis-runner, which is integrated with our Cromwell server.
