

# Custom Cohorts 

## What is a cohort?

A cohort refers to a curated group of sequencing groups (SGs) that share common characteristics or criteria. These cohorts are explicitly defined and managed, allowing users to tailor their analyses to specific subsets of sequencing data.

In essence, a cohort serves as an immutable set of specific sequencing groups. Users can create cohorts based on various criteria such as project/dataset names, inclusion/exclusion of specific sequencing groups, sample type, sequencing group type, or by referencing a previous cohort ID.
To create a cohort, users must specify a name, description, and either a template ID or a set of cohort criteria.

Cohort Example:

* Cohort ID: COH501
* Name: ExomeCohortABC
* Description: All exomes in Dataset A, B, and C, as of Batch 15 processed on 24/08/24
* Template ID: TEMPLATE12


## What is a cohort template?

A cohort template serves as a predefined set of criteria used for creating cohorts. It encapsulates the specific conditions or filters that define a cohort's composition. Templates are stored in the system and can be reused to generate cohorts with consistent criteria.

Each template typically includes parameters or rules for selecting sequencing groups (SGs) based on various factors such as project/dataset names, metadata attributes, inclusion/exclusion criteria, or referencing a previous cohort ID. By defining templates, users can streamline the cohort creation process and ensure consistency in cohort definitions across analyses.

Templates enhance efficiency and reproducibility by allowing users to quickly create cohorts with predefined criteria. They serve as a blueprint for cohort creation, enabling users to apply consistent selection criteria to different subsets of sequencing data. Additionally, templates facilitate collaboration and knowledge sharing by providing a standardized approach to cohort generation within the system.

Template Example:

* Template ID: TMPL123
* Name: ExomeABCTemplate
* Description: Dataset A, B, and C Exomes
* Cohort Criteria: {projects: ['A', 'B', 'C'], sg_type: ['exome']}


## How can I create a cohort?

### Recommended
* Use the create custom cohort script [create_custom_cohort.py](https://github.com/populationgenomics/metamist/blob/dev/scripts/create_custom_cohort.py)
* Input all specified parameters, including your desired cohort name, template ID, or criteria.

Example From Existing Template:

```shell 
analysis-runner 
--dataset example-dataset --description "Create Cohort X"
--output-dir "example-dataset" --access-level standard 
scripts/create_custom_cohort.py --project example-dataset 
--name ExomeCohortABC --description "March Run, TMP123, all the exomes in ABC" 
--template TMPL123
```

Example From Criteria:

```shell
analysis-runner \
--dataset example-dataset --description "Create Cohort X" \
--output-dir "example-dataset" --access-level standard \
scripts/create_custom_cohort.py --project example-dataset \
--name ExomeCohortABC --description "March Run, All exomes in ABC" \
--projects "projectA" "projectB" "projectC" --sg-types "exome"
```

### Swagger Page
* Create a template using the /cohort/{project}/cohort_template endpoint and pass the returned template ID to the /cohort/{project}/cohort endpoint. 
* Alternatively, you can use the create cohort endpoint directly.