# Targets and Stages

In production pipelines, stages process different types of targets: SequencingGroup, Dataset, Cohort, or MultiCohort. Understanding the characteristics of each target and the corresponding stage type is essential for building workflows effectively.

## Targets Overview

### SequencingGroup

A SequencingGroup represents the sequence data from a single sample. It is effectively the result of running sequencing.

Example:

```json
{
    "id": "CPGAAAA",
    "type": "genome",
    "technology": "short-read",
    "platform": "illumina"
}
```

### Dataset

A Dataset is a collection of SequencingGroups belonging to the same project. The terms Dataset and Project are used interchangeably at CPG, and each dataset has a 1:1 relationship with a project.

Example:

```json
{
    "id": 14,
    "name": "fewgenomes",
    "dataset": "fewgenomes",
    "sequencingGroups": [
        {"id": "CPGAAA"},
        {"id": "CPGBBB"},
        {"id": "CPGCCC"}
    ]
}
```

### Cohort

A Cohort is a curated group of SequencingGroups that share common characteristics or criteria.

Example:

```json
{
    "id": "COH501",
    "name": "ExomeCohortABC",
    "description": "All exomes in Dataset A, B, and C, as of Batch 15 processed on 24/08/24",
    "template": "TMPL12"
}
```

### MultiCohort

A MultiCohort is a collection of Cohorts. Unlike other target types, a MultiCohort is not stored or represented in metamist.

Example:

```json
[ "COH123", "COH456", "COH675" ]
```

## Stages Overview

Each stage in a production pipeline acts on a specific type of target. There are four types of stages, each designed to accommodate different targets:

* SequencingGroupStage
* DatasetStage
* CohortStage
* MultiCohortStage

### How to Determine the Appropriate Stage Type

The choice of stage type depends on the nature of the output produced by the stage:

#### SequencingGroupStage

**Use this stage when:** There is one unique output per SequencingGroup.

**Example:** When running alignment, you produce a .cram file for each SequencingGroup.

#### DatasetStage

**Use this stage when:** There is one unique output per Dataset.

**Example:** When running AnnotateDataset, which splits the MT by dataset and annotates dataset-specific fields.

#### CohortStage

**Use this stage when:** There is one unique output per Cohort.

**Example:** When analyzing a group of SequencingGroups that share common characteristics, producing a single output per Cohort.

#### MultiCohortStage

**Use this stage when:** There is one output for the entire workflow run, which may involve multiple Cohorts.

**Example:** JointCalling, which produces a VCF for all the GVCFs from all SequencingGroups. Note that a MultiCohort stage can run on a single Cohort or multiple Cohorts.
