# Storage policies

- [Storage policies](#storage-policies)
  - [Typical data flow](#typical-data-flow)
  - [Buckets](#buckets)
    - [reference: `gs://cpg-reference`](#reference-gscpg-reference)
    - [upload: `gs://cpg-<dataset>-upload`](#upload-gscpg-dataset-upload)
    - [archive: `gs://cpg-<dataset>-archive`](#archive-gscpg-dataset-archive)
    - [main: `gs://cpg-<dataset>-main`](#main-gscpg-dataset-main)
    - [test: `gs://cpg-<dataset>-test`](#test-gscpg-dataset-test)
    - [analysis: `gs://cpg-<dataset>-analysis`](#analysis-gscpg-dataset-analysis)
    - [temporary: `gs://cpg-<dataset>-temporary`](#temporary-gscpg-dataset-temporary)
    - [web: `gs://cpg-<dataset>-web`](#web-gscpg-dataset-web)
    - [release: `gs://cpg-<dataset>-release-requester-pays`](#release-gscpg-dataset-release-requester-pays)
  - [Deletion](#deletion)
  - [Access permissions](#access-permissions)
  - [Analysis runner](#analysis-runner)
  - [Deployment](#deployment)

This document describes where our production datasets are stored, how
[object lifecycles](https://cloud.google.com/storage/docs/lifecycle) are
configured, and how access permissions are managed.

We are trying to strike a balance between:

- Quick development iterations and unlimited ad-hoc data exploration.
- Robust, reproducible pipelines, using only strictly necessary cloud resources.

This motivates two somewhat unusual principles in the design:

- Quick development iterations and testing only happens on a small (but
  representative) subset of the data (blue highlight in the graph below). The
  full dataset is only accessible through code that has been reviewed and
  committed (green highlight in the graph below).
- All outputs are versioned and immutable, except for purely temporary results
  (yellow highlight in the graph below). Since "production runs" of pipelines
  only happen after sufficient testing on subsets of the data, immutable results
  generally shouldn't cause a lot of churn or resource usage.

## Typical data flow

![data flow](figures/dataflow.svg)

## Buckets

In this context, a dataset corresponds to a particular project / effort, e.g.
_TOB-WGS_ or _RDNow_, with separate buckets and permission groups. Below,
`<dataset>` is a placeholder for the name of that effort, e.g. `<dataset>` =
`tob-wgs`.

Currently, all buckets reside in the `australia-southeast1` GCP region. It's
therefore essential that all computation happens in that region too, to avoid
network egress costs.

In general, all datasets within buckets should be versioned, using a simple
major-minor naming scheme like `gs://cpg-<dataset>-main/qc/v1.2/`. We don't have a
strict semantic definition to distinguish between major and minor version
increments. The addition of significant numbers of samples or the use of a
substantially different analysis method usually justifies a major version
increase.

### reference: `gs://cpg-reference`

- **Description**: Contains reference data that's independent of any particular
  dataset, e.g. the GRCh38 human reference genome sequences used for alignment,
  the GENCODE GTF used for functional annotations, the version of dbSNP used to
  add rsIDs, etc. These resource "bundles" are versioned together.
  Most pipelines will depend on this bucket to some degree.
- **Storage**: Standard Storage indefinitely.
- **Access**: Everybody in the organisation has viewer permissions.

### upload: `gs://cpg-<dataset>-upload`

- **Description**: Contains files uploaded from sequencing providers, as a
  staging area.
- **Main use case**: Raw sequencing reads (e.g. CRAM files) and derived data
  from initial production pipelines: QC metrics including coverage results,
  additional outputs from variant callers (e.g. structural variants,
  repeat expansions, etc.), and GVCFs. An upload processor pipeline moves these
  files into the _archive_ and _main_ buckets in batches, creating new releases.
- **Storage**: Standard Storage indefinitely, but cleared up regularly by
  the upload processor.
- **Access**: Restricted to service accounts that run workflows. Sequencing
  providers have creator permissions, using a service account.

### archive: `gs://cpg-<dataset>-archive`

- **Description**: Contains files for _archival purposes_, where long term
  storage is cheap, but _retrieval is very expensive_.
- **Main use case**: Raw sequencing reads (e.g. CRAM files) and potentially
  GVCFs (after conversion to Hail MatrixTables).
- **Storage**: Standard Storage for 30 days, before changing to Archive Storage.
  This allows workflows to do post-processing of the data shortly after initial
  creation (e.g. copying windowed regions of raw reads around interesting
  variants) before retrieval becomes expensive.
- **Access**: Restricted to service accounts that run workflows, to avoid
  accidental retrieval costs incurred by human readers.

### main: `gs://cpg-<dataset>-main`

- **Description**: Contains _input_ files that are frequently accessed for
  analysis. Long term storage is expensive, but retrieval is cheap.
- **Main use case**: Hail tables (e.g. merged GVCF files), metadata, SV caller
  outputs, transcript abundance files, etc.
- **Storage**: Standard Storage indefinitely.
- **Access**: Human users only get listing permissions, but viewer permissions
  are granted indirectly through the [analysis runner](#analysis-runner)
  described below. This avoids high costs through code that hasn't been
  reviewed. See the _test_ bucket below if you're developing / prototyping a new
  pipeline.

### test: `gs://cpg-<dataset>-test`

- **Description**: Contains _input_ test data, which usually corresponds to a
  subset of the data stored in the _main_ bucket. Long term storage is
  expensive, but retrieval is cheap.
- **Main use case**: Iterate quickly on new pipelines during development.
  This bucket contains representative data, but given the much smaller dataset
  size the risk of accidental high cloud computing costs is greatly reduced.
- **Storage**: Standard Storage indefinitely.
- **Access**: Human users only get viewer permissions, so pipeline code doesn't
  need to be reviewed before this data can be read.

### analysis: `gs://cpg-<dataset>-analysis`

- **Description**: Contains files frequently accessed for analysis.
  Long term storage is expensive, but retrieval is cheap.
- **Main use case**: Analysis results derived from the _main_
  bucket, which in turn can become inputs for further analyses.
- **Storage**: Standard Storage indefinitely.
- **Access**: Human users only get listing permissions, but creator permissions
  are granted indirectly through the [analysis runner](#analysis-runner)
  described below.

### temporary: `gs://cpg-<dataset>-temporary`

- **Description**: Contains files that only need to be retained _temporarily_
  during analysis or workflow execution. Retrieval is cheap, but old files get
  automatically deleted.
- **Main use case**: Hail "checkpoints" that cache results while repeatedly
  running an analysis during development.
- **Storage**: Files that are older than 30 days get deleted automatically.
- **Access**: Human users get admin permissions, so care must be taken not to
  accidentally overwrite / delete each other's results (e.g. by avoiding naming
  collisions through a file name prefix).

### web: `gs://cpg-<dataset>-web`

- **Description**: Contains static web content, like QC reports as HTML pages,
  which is served through an access-restricted web server.
- **Main use case**: Human-readable analysis results, like reports and notebooks.
- **Storage**: Standard Storage indefinitely.
- **Access**: Human users only get viewer permissions, but creator permissions
  are granted indirectly through the [analysis runner](#analysis-runner)
  described below.

### release: `gs://cpg-<dataset>-release-requester-pays`

- **Description**: Contains data that's shared with other researchers or is
  publicly available. Long term storage is expensive, but network egress costs
  are covered by the users who download the data.
- **Main use case**: Aggregate results that are made publicly available or
  snapshots of datasets that are shared with other researchers through
  restricted access.
- **Storage**: Standard Storage indefinitely.
- **Access**: Human users only get viewer permissions, to reduce the risk of
  accidental modification / deletion of files.

## Deletion

By default, human users can't delete objects in any bucket except for the
_temporary_ bucket. This avoids accidental deletion of results and makes sure
our pipelines stay reproducible. However, it will sometimes be necessary to
delete obsolete results, mainly to reduce storage costs. Please coordinate
directly with the software team in such cases.

All buckets retain one noncurrent object version for 30 days, after which
noncurrent files get deleted. This allows "undelete" recovery in case of
accidental deletion.

## Access permissions

Permissions are managed through IAM, using access groups.

- `<dataset>-access@populationgenomics.org.au`: human users are added to this group to
  gain permissions as described above. Users should also be added to the
  corresponding Hail billing project, so they can see the batches launched through
  the [analysis runner](#analysis-runner).
- `<dataset>-release-access@populationgenomics.org.au`: grants members viewer
  permissions to the _release_ bucket. Only required if the releases are not
  public. This usually includes users outside the CPG, in which case they must
  use Google accounts.

## Analysis runner

To encourage reproducible workflows and code getting reviewed before it's run on
"production data", viewer permissions to the _main_ bucket and creator
permissions to the _analysis_ bucket are available only through the
[analysis runner](#analysis-runner).

There are three distinct access levels: _test_, _standard_, and _full_.

- **test**: Prototype and iterate on your pipeline using the _test_ access level. This will
  give you permissions to read from the _test_ bucket for input and the _temporary_ / _web_
  buckets for outputs. You don't need to get your code reviewed, but it needs to be
  pushed to a remote branch in the _populationgenomics_ GitHub organization in order
  for the analysis runner to work. In summary:
  - **Access**: _test_
  - **Input**: _test_
  - **Output**: _temporary_ / _web_
  - **GitHub**: no PR, just push to remote branch
- **standard**: Once you're ready to run your pipeline on the _main_ / _analysis_ buckets for
  input and the _analysis_ / _temporary_ / _web_ buckets for output, create a pull request to get your code
  reviewed. Once your code has been merged in the `main` branch, run the analysis
  runner using the _standard_ access level. In summary:
  - **Access**: _standard_
  - **Input**: _main_ / _analysis_
  - **Output**: _analysis_ / _temporary_ / _web_
  - **GitHub**: PR merged to `main` branch
- **full**: If you ever need write access to other buckets, e.g. to initialize data in the
  _main_ bucket, you can get full write / delete access to all buckets using the _full_ access
  level. However, to reduce risk of accidental data loss, only request this access
  level if you really need it. In summary:
  - **Access**: _full_
  - **Input**: anywhere
  - **Output**: anywhere
  - **GitHub**: PR merged to `main` branch

For more detailed instructions and examples, look at the
[analysis runner repository](https://github.com/populationgenomics/analysis-runner).

If this causes too much friction in your daily work, please don't work around
the restrictions. Instead, reach out to the software team, so we can work on
process improvements together.

## Deployment

See the [analysis runner repository](https://github.com/populationgenomics/analysis-runner/tree/main/stack)
for the deployment configuration that can be used to bring up a stack
corresponding to a dataset.
