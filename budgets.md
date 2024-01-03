# Budgets

We have some mixed terminology when talking about financing compute. For regular DATASETs, this is the terminology you should know.

- a DATASET's GCP project budget:
    - Resets _monthly_
    - Usually in AUD
    - Managed in [cpg-infrastructure-private](https://github.com/populationgenomics/cpg-infrastructure-private) in the `DATASET/budgets.yaml` file.
    - Covers:
        - storage cost
        - dataproc + cromwell cost that's run in that dataset
        - some incidentals, like fees for using the secret manager.

- a DATASET's Hail Batch Billing Limit:
    - A cumulative budget (does not reset)
    - Always in USD
    - Managed manually in Hail Batch was someone with a _developer_ permission
    - Covers:
        - compute that occurs in Hail Batch, and run within that billing project.

- a DATASET's _shared_ GCP budget:
    - A cumulative budget (does not reset)
    - Usually in AUD
    - Managed in [cpg-infrastructure-private](https://github.com/populationgenomics/cpg-infrastructure-private) in the `DATASET/budgets.yaml` file.
    - Covers:
        - Usually just egress from the shared service-account when pulling data from requester-pays (release) bucket.

- The Hail GCP project budget:
    - Resets _monthly_
    - Covers the cost for ALL compute occuring within Hail directly, regardless of dataset.
    - Yes, this means compute through Hail Batch does NOT get assigned to a DATASET's GCP project, it gets billed to the Hail GCP project.

Also:

- Most GCP budgets are _monthly_ and _reset_ on the 1st of each month (in Pacific Time, about 5 PM AEST).

## Daily cost report in slack

A daily cost summary is reported to slack at 9am (Sydney time) every day. This reports the 24 hour / month-to-date _GCP Project_ spend, and highlights any projects whose spend is trending higher than the budget allows.

## Aggregated costs

As costs can occur in multiple environments, we redistribute these costs into topics - there is one topic per dataset (+ a couple of extra topics).

Here is the rough method for breaking these costs down:

- We pass all cost from each GCP project (except seqr) onto the respective topic
- For all hail batch projects except seqr, we calculate the Australian cost, and pass it onto the respective topic.
- For seqr:
    - For costs in the seqr hail batch billing project:
        - If the job has a "dataset" attribute, we pass that cost onto the specific dataset directly
        - If the job does not, we distribute this across all seqr projects, based on the dataset's proportionate cram size for when the most relevant _sample was added to metamist_.
    - For all costs in the seqr GCP project, we distribute this across all seqr projects, based on the dataset's proportionate cram size for when a sequencing group was added to _any elasticsearch index_.

## Costs

### GCP

Egress: $0.19 USD per GB (~$0.30 AUD per GB)

Storage:

- Standard $0.023 USD per GB per month (~$38 AUD per TB per month)
- Nearline $0.016 USD per GB per month (~$26 AUD per TB per month)
- Coldline $0.006 USD per GB per month (~$10 AUD per TB per month)

## Managing budgets and spending

### Transfer in

> I want to transfer 2.5 TB of data into $DATASET

1. Estimate how much storage will cost for the data you're ingesting (2.5 TB * $38 = $95 AUD per month)
1. Consider the analysis you intend to do for this project, including storing the results. This might initially be 2-3 times the initial storage cost.
1. Bump the GCP budget for the project to $300 AUD per month, by submitting a pull request to [cpg-infrastructure-private `$DATASET/budgets.yaml`](https://github.com/populationgenomics/cpg-infrastructure-private) file.
1. Reviewers will be automatically selected, and the budget will get updated shortly after merging.

### Large compute job

> I'm running a large compute job, eg: alignment, variant calling, joint-calling, etc.

1. You should make sure the GCP budget for the DATASET will cover the extra files you intend to produce, and any dataproc / cromwell cost that may occur.
    1. Submit a PR against the cpg-infra-private `DATASET/budgets.yaml` to increase this.

1. You must ensure the DATASET's Hail Batch Billing Limit will cover the expected compute cost.
    1. Chat to your manager who can action this.

1. Estimate the cost of analysis (in AUD) and ensure:
    1. The GCP budget for `hail-295901` has been updated to include the AUD cost of your analysis (including the cost of running Hail + other people's analysis). This must be done manually through the [budgets page](https://console.cloud.google.com/billing/01D012-20A6A2-CBD343/budgets?organizationId=648561325637). All data team leads have permissions to alter this budget.

1. Watch the budgets through your analysis, if Hail runs out, it will stop the Hail batch cluster, although your analysis will be fine, stopping compute jobs in the middle cause a restart, and can be economically costly as that work must be redone.


> I'm running a large compute job specifically in seqr

1. You should make sure the budget for all datasets for which you intend to produce data is set to cover the extra files you intend to produce.
    1. Submit a PR against the cpg-infra-private to each `DATASET/budgets.yaml` to increase this.

1. Estimate the cost of analysis (in AUD) and ensure:

    1. The GCP budget for `hail-295901` has been updated to include the AUD cost of your analysis (including the cost of running Hail + other people's analysis). This must be done manually through the [budgets page](https://console.cloud.google.com/billing/01D012-20A6A2-CBD343/budgets?organizationId=648561325637). Currently any of the data team leads have the permissions to alter this budget.

    1. The GCP budget for seqr has been updated to include the AUD cost of any dataproc / cromwell analysis. This must be done through cpg-infra-private.

    1. The hail cumulative budget for SEQR has been updated through the [billing project limits page](https://batch.hail.populationgenomics.org.au/billing_limits). This must be done by a "developer" (Hail concept).

1. Watch the budgets through your analysis, if Hail runs out, it will stop the Hail batch cluster, although your analysis will be fine, stopping compute jobs in the middle cause a restart, and can be economically costly as that work must be redone.


### Egress

> Collaborators want to egress some data from a $DATASET.

1. Calculate the size of the data to egress, (eg: 100 GB, ~$30 AUD)
1. Enable the `shared` project, and potentially a release bucket for the $DATASET. Create a pull request that configures both:
    1. Configures release / shared project in the [`production.yaml`](https://github.com/populationgenomics/cpg-infrastructure-private/blob/main/production.yaml), eg:

        ```yaml
        DATASET:
          enable_release: true
          enable_shared_project: true
        ```

    1. Sets the budget for the shared project in `DATASET/budgets.yaml`, eg:

        ```yaml
        gcp:
          monthly_budget: 400
          shared_total_budget: 450
        ```

1. Reviewers will be automatically selected, and the budget / shared project / bucket will get updated shortly after merging.
1. Create credentials for the `shared-sa` machine account

    ```bash
    # gcp project ID (may include numbers)
    export GCP_PROJECT="$DATASET"
    gcloud iam service-accounts keys create "$GCP_PROJECT-shared.json" "--iam-account=shared@$GCP_PROJECT-shared.iam.gserviceaccount.com"
    ```

1. (Optional) You may want to create a signed URL for files to release, these files MUST be in the release bucket - then you're able to run:

    ```bash
    gcloud storage sign-url \
        --private-key-file=$GCP_PROJECT-shared.json \
        --query-params=userProject=$GCP_PROJECT-shared \
        --duration=7d \
        gs://cpg-DATASET-release/$DATE/FILE
    ```
