# Budgets

Budgets at the CPG are managed _mostly_ through GitHub, and there are a few places where budgets need to be managed.

Some _you should knows_ from the start:

- Compute through Hail Batch does NOT get assigned to the GCP project, it gets billed to the Hail GCP project.
    - Compute through Dataproc and notebooks DO get assigned to the GCP project.
- Hail maintains its own set of [_cumulative_ budgets](https://batch.hail.populationgenomics.org.au/billing_limits), in USD.
- GCP budgets are _monthly_ and _reset_ on the 1st of each month (in Pacific Time, about 5 PM AEST).
    - GCP budgets are managed in [cpg-infrastructure-private](https://github.com/populationgenomics/cpg-infrastructure-private) (except Hail).

## Costs

### GCP

Egress: $0.19 USD per GB (~$0.30 AUD per GB) 

Storage:

- Standard $0.023 USD per GB per month (~$38 AUD per TB per month)
- Nearline $0.016 USD per GB per month (~$26 AUD per TB per month)
- Coldline $0.006 USD per GB per month (~$10 AUD per TB per month)


## Situations

> I'm about to 2.5 TB of data into $DATASET

1. Estimate how much storage will cost for the data you're ingesting (2.5 TB * $38 = $95 AUD per month)
2. Consider the analysis you intend to do for this project, including storing the results. This might initially be 2-3 times the initial storage cost.
2. Bump the GCP budget for the project to $300 AUD per month, by submitting a pull request to [cpg-infrastructure-private `$DATASET/budgets.yaml`](https://github.com/populationgenomics/cpg-infrastructure-private) file.
3. Reviewers will be automatically selected, and the budget will get updated shortly after merging.


> I'm running a large compute job for seqr, eg: alignment, variant calling, joint-calling, etc.

1. You should make sure the budget for DATASET's GCP project is set to cover the extra files you intend to produce.
    1. Follow the steps above to bump the budget for DATASET's project.
1. Estimate the cost of analysis (in AUD) and ensure:
    1. The GCP budget for `hail-295901` has been updated to include the AUD cost of your analysis (including the cost of running Hail + other people's analysis). This must be done manually through the [budgets page](https://console.cloud.google.com/billing/01D012-20A6A2-CBD343/budgets?organizationId=648561325637). Currently any of the data team leads have the permissions to alter this budget.
    1. The hail cumulative budget for SEQR has been updated through the [billing project limits page](https://batch.hail.populationgenomics.org.au/billing_limits). This must be done by a "developer" (Hail concept).
1. Watch the budgets through your analysis, if Hail runs out, it will stop the Hail batch cluster, although your analysis will be fine, stopping compute jobs in the middle cause a restart, and can be economically costly as that work must be redone.

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
