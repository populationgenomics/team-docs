# Data Sharing

If a collaborator wants to upload data to a GCS bucket, you can follow this
process to set up a service account that can be used to upload the data on their
behalf:

## Step 1: Create service account

- Log into your GCP account and select the project that contains the bucket in
  which the data will be uploaded.
- `IAM & Admin` `->` `Service Accounts` `->` `Create Service Account`.
- Fill in the service account name - the ID should be filled in automatically.
- (Optional) Add a description of the service account.
- `Create`.

<img src="https://i.postimg.cc/dV7XQ6sX/create-service-account.png" alt="create service account" height="200" />

## Step 2: Create key

- Locate your newly created service account in the main service account table.
- Under the `Actions` column, select the triple dot icon, then select:
  `Manage keys` `->` `ADD KEY` `->` `Create new key` `->` `Key type: JSON` `->`
  `Create`.
- A JSON file should automatically download through your browser. **IMPORTANT**:
  this contains a private key so it should be treated as a sensitive password
  i.e. do not share this publically.

<img src="https://i.postimg.cc/TPDZ09Bm/create-key.png" alt="create key" height="200" />

## Step 3: Add bucket permissions

- Select the bucket in which the data will be uploaded
- Select `Permissions` `->` `ADD`
- Add the name of the service account you created in Step 1 under `New members`
- Select/find the `Storage Object Creator` Role.
- `Save`

<img src="https://i.postimg.cc/NFfmsNcr/add-bucket-permissions.png" alt="add bucket permissions" height="200" />

## Step 4: Upload data

- Install the
  [Google Cloud SDK](https://cloud.google.com/sdk/docs/install#linux) tools
  (there's also a
  [conda package](https://anaconda.org/conda-forge/google-cloud-sdk) if you're
  familiar with conda).

- Run the following:

```bash
gcloud auth activate-service-account --key-file=<project-ID-numbers>.json  # this only needs to be run once

gsutil -m cp -r data_to_upload gs://my-bucket # the service account only has upload permissions
```