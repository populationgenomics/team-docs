# Welcome to the CPG

This document describes the commonly used technologies at the Centre, together with some hints on how to use various tools.

- [Welcome to the CPG](#welcome-to-the-cpg)
  - [Genomics overview](#genomics-overview)
  - [Brew](#brew)
  - [Analysis flow at the CPG](#analysis-flow-at-the-cpg)
  - [Infrastructure](#infrastrucutre)

## Genomics overview

If you're new to genomics (or would be interested in a refresher) you might like to explore the [learngenomics.dev](https://learngenomics.dev/) resource.

It was written by and for computer scientists and engineers, and provides an awesome overview of pertinent biological concepts.

Note, while the resource approaches the topics from the lens of cancer genomics, most of the topics are still very relevant to our current work.

## Brew

If you're on Mac, then [`brew`](https://brew.sh/) is a great way to install lots of software - this guide will provide instructions using Brew.

## Analysis flow at the CPG

At the CPG, we organise data into logical _dataset_ efforts. Around each dataset is a billing boundary, a set of cloud buckets, and machine accounts. More information is available in our [Storage Policies](/storage_policies/) doc.

We mostly store genomics data in blobs our the specific blob storage (GCP / Azure). We store structured metadata in metamist - our metadata database as a service. We sometimes refer to metamist as the _state_ of analysis at the centre.

We have two namespaces at the centre:

1. main - for all production data
2. test - for specific subsets, or synthetic data you can run unreviewed code on.

If you want to affect genomics data, or metadata - you'll usually need to write a script, publish it to a populationgenomics repository and ask the [_analysis-runner_](#analysis-runner) to run that script for you. If you want to affect _main_ namespaced data, your script will need to be on the `main` branch (which requires a code review).

> For example, our production-pipelines are triggered through the analysis-runner, this constructs a processing pipeline based on the metadata in metamist - as this pipeline runs, it creates new artifacts (CRAMs, VCFs, QC reports), and updates metamist.

### Analysis runner

We don't allow users to run scripts directly on genomics data, we require code to be commited, reviewed, and then ran. The analysis-runner is the mechanism we use for that indrection. The analysis-runner builds a Batch pipeline from a specific commit in a GitHub repository.

There's a handy CLI tool too (`pip install analysis-runner`)!

Make sure you have:

- the name of the [dataset](/storage_policies/), as this controls what data you can access and which code repositories are available,
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


## Infrastrucutre

> See [infrastructure](/infrastructure) for more information.

The CPG integrates a number of products into our ecosystem, mostly using Pulumi to coordinate this. From Google Cloud Platform, Hail Batch, Cromwell, Metamist and more.
