# Hail Batch developer setup

If you only intend to use Hail Batch for running your pipelines, you can skip this
document. This is meant for developers that work on the Hail Batch codebase.

1. Instead of using the standard sign-up link, ask another existing Hail developer to create a Hail developer account for you. If you've already signed up, that's okay too, but [a little more work to fix](https://github.com/hail-is/hail/blob/main/dev-docs/creating-a-developer-account.md).
1. Ask to be added to the `hail-dev@populationgenomics.org.au` permissions group.
1. Follow the instructions to add an [OAuth 2.0 redirect URI](https://github.com/hail-is/hail/blob/main/dev-docs/creating-a-developer-account.md), but note that our GCP project is called `hail-295901`. If your email address is `jane.doe@populationgenomics.org.au`, your Hail `$USERNAME` will be `janedoe` (i.e. does not contain a dot).
1. Install Hail:

   ```bash
   conda create --name hail -c cpg -c bioconda -c conda-forge hail
   conda activate hail
   ```

1. Retrieve a new Hail token:

   ```bash
   hailctl auth login
   ```

1. Prepare a change and push it to `$BRANCH` in our Hail fork. Then run a `dev deploy`, which will run the steps you specify as defined in the `build.yaml` file in your branch. The corresponding Kubernetes deployments will be brought up in your own separate namespace, so they won't interfere with the production deployment.

   ```bash
   hailctl dev deploy --branch populationgenomics/hail:$BRANCH --steps deploy_batch,deploy_query
   ```

1. The previous step should have printed a link to a CI dashboard. Follow the progress in the CI dashboard and wait until all steps have succeeded.
1. The first time you run a `dev deploy`, you'll also have to create a new user. Unless you delete the "auth tables" in your namespace, subsequent deploys will be able to see the same user. At the moment, this initial setup requires a few manual steps. Steps below assume that you've set up the environment variable `$NAMESPACE` according to your Hail user name, e.g.

   ```bash
   export NAMESPACE=janedoe
   ```

   1. Create a new Google Service account and store its key locally:

      ```bash
      gcloud config set project hail-295901

      gcloud config set compute/zone australia-southeast1-b

      gcloud iam service-accounts create $NAMESPACE-dev --description="dev namespace"

      gcloud iam service-accounts keys create /tmp/key.json --iam-account $NAMESPACE-dev@hail-295901.iam.gserviceaccount.com
      ```

   1. Fetch the credentials for the GKE cluster:

      ```bash
      gcloud container clusters get-credentials vdc
      ```

   1. Store the key as a Kubernetes secret in your namespace:

      ```bash
      kubectl --namespace $NAMESPACE create secret generic $NAMESPACE-dev-gsa-key --from-file=/tmp/key.json
      ```

   1. Create a new token. Within a Hail environment, run in Python:

      ```python
      import secrets
      import os
      from hailtop.auth import session_id_encode_to_str

      with open('/tmp/tokens.json', 'wt') as f:
          f.write(f'{{"{os.getenv("NAMESPACE")}": "{session_id_encode_to_str(secrets.token_bytes(32))}"}}')
      ```

   1. Store the token as a Kubernetes secret in your namespace:

      ```bash
      kubectl --namespace $NAMESPACE create secret generic $NAMESPACE-dev-tokens --from-file=/tmp/tokens.json
      ```

      Print the token value, which will be inserted as `$TOKEN` in the database section below.

      ```bash
      kubectl --namespace $NAMESPACE get secret$NAMESPACE-dev-tokens
      ```

   1. You'll now need to add your user to the "auth table" in the SQL instance. First, get a list of all pods, then pick an auth pod, e.g. "auth-6d559bd9b6-npw56".

      ```bash
      kubectl --namespace $NAMESPACE get pod
      ```

   1. Connect to the pod you've selected:

      ```bash
      kubectl --namespace $NAMESPACE exec -it auth-6d559bd9b6-npw56 -- /bin/bash
      ```

   1. On the pod, connect to the SQL instance and set the `$NAMESPACE` variable (the one you exported earlier is not available to the pod). From `sql-config.cnf`, set the variable `$HOST`, and note the `password`.

      ```bash
      cd /sql-config
      cat /sql-config/sql-config.cnf
      export NAMESPACE="<janedoe>"
      export HOST="<host-from-sql-config.cnf>"
      mysql --ssl-ca=server-ca.pem --ssl-cert=client-cert.pem --ssl-key=client-key.pem --host=$HOST --user=$NAMESPACE --password
      ```

   1. Within `mysql>`, run the following, but note that you'll have to replace `$NAMESPACE`, `$EMAIL`, and `$TOKEN` manually:

      ```sql
      use $NAMESPACE;

      INSERT INTO users (state, username, email, is_developer, is_service_account, tokens_secret_name, gsa_email, gsa_key_secret_name, namespace_name) VALUES ('active', '$NAMESPACE', '$EMAIL@populationgenomics.org.au', 1, 0, '$NAMESPACE-dev-tokens', '$NAMESPACE-dev@hail-295901.iam.gserviceaccount.com', '$NAMESPACE-dev-gsa-key', '$NAMESPACE');

      INSERT INTO sessions (session_id, user_id) VALUES ('$TOKEN', 6);
      ```

   1. Close the connection to the database and the pod.

   1. Navigate to `https://internal.hail.populationgenomics.org.au/$NAMESPACE/batch/batches` in your browser. Select Batch > Billing Projects and add `$NAMESPACE` to the `test` billing project.

   1. Give your Google Service Account _Storage Admin_ permissions to a Hail bucket used for submitting batches, e.g. in your "dev" GCP project.

1. You can now switch to your development namespace like this:

   ```bash
   hailctl dev config set default_namespace $NAMESPACE
   ```

1. Tokens are managed separately for each namespace. To get a token for your developer namespace, run:

   ```bash
   hailctl auth login
   ```

1. You can now run a standard Python script to submit a batch. Use the Hail bucket you've configured earlier, together with the `test` Hail billing project.

1. While REST API calls for the default (production) namespace look like `https://auth.hail.populationgenomics.org.au/api/v1alpha/userinfo`, you'll need to change this to `https://internal.hail.populationgenomics.org.au/$NAMESPACE/auth/api/v1alpha/userinfo` to route the request to your dev namespace. This now requires two tokens: one for the default namespace, and the other for your development namespace. They need to be passed as separate headers:

   ```bash
   DEFAULT_TOKEN=$(jq -r .default ~/.hail/tokens.json)
   DEV_TOKEN=$(jq -r .$NAMESPACE ~/.hail/tokens.json)
   curl -H "X-Hail-Internal-Authorization: Bearer $DEFAULT_TOKEN" -H "Authorization: Bearer $DEV_TOKEN" https://internal.hail.populationgenomics.org.au/$NAMESPACE/auth/api/v1alpha/userinfo
   ```

1. Similarly, to navigate to the web endpoints served by your namespace, use the form `https://internal.hail.populationgenomics.org.au/$NAMESPACE/batch/batches`.

1. To switch back to the production namespace, simply run:

   ```bash
   hailctl dev config set default_namespace default
   ```

1. Since your Kubernetes deployment is independent of the production deployment, it will bring up additional pods that will require workers to run on. If you're not planning on using them for development, it's a good idea to turn them down to reduce cost. However, be extremely careful when using destructive Kubernetes commands like these, as it's easy to accidentally bring down the whole production namespace if you forget to specify your namespace. You might want to add an alias for the command to reduce that risk:

   ```bash
   alias hail-cleanup="kubectl --namespace $NAMESPACE delete deployment --all"
   hail-cleanup
   ```

## Debugging

When you need to debug an issue within your namespace, it's often helpful to inspect the logs of the pods that run the service in question. Keep in mind that many services are replicated, so you might have to check multiple pods.

```bash
kubectl --namespace $NAMESPACE get pod
kubectl --namespace $NAMESPACE logs $POD
```

## Merging upstream changes

We try to keep our Hail fork as close as possible to the upstream repository. About once a week we integrate any upstream changes as follows:

```bash
git remote add upstream https://github.com/hail-is/hail.git  # One-time setup.

git fetch origin
git fetch upstream
git checkout -b upstream
git reset --hard origin/main
git merge upstream/main  # Potentially resolve any conflicts.
git push origin upstream  # Create a PR as usual.
```

## Upstreaming changes

Whenever we make a change that isn't purely specific to CPG (like deployment settings), we should upstream those changes. In general, the process looks like this:

1. Get the change reviewed and deployed locally.
1. Test and double-check everything is working as intended.
1. Create a new branch, based on the current `hail-is/hail:main`, and cherry-pick or rebase your change.
1. Open a standard PR for the `hail-is/hail` repository and coordinate on Zulip to get your PR reviewed.

## Deploying changes to production

After a change has been merged to the `main` branch, it can be deployed to the `default` namespace using the `prod_deploy` API endpoint. This will always use the current `HEAD`. Similar to a `dev deploy`, you can specify the steps from `build.yaml` that should be run. Unless there's a good reason to only deploy a particular service, you should use the set listed below. This is a partial list of steps that is specific to the CGP setup, and excludes services we don't use, for example the blog or image fetcher.

It's a good idea to give a quick heads-up in the `#team-software` channel before you're doing this, just in case something breaks.

```bash
curl -X POST -H "Authorization: Bearer $(jq -r .default ~/.hail/tokens.json)" \
    -H "Content-Type:application/json" \
    -d '{"steps": ["deploy_auth", "deploy_batch", "deploy_ci", "deploy_notebook", "deploy_query", "deploy_router"]}' \
    https://ci.hail.populationgenomics.org.au/api/v1alpha/prod_deploy
```

You can follow the progress on the [CI dashboard](https://ci.hail.populationgenomics.org.au/batches) by inspecting the most recent batch of type "deploy".

**Warning**: Any changes that involve a database migration will result in the batch service being shut down. You'll then need to [bring it back up manually](https://github.com/hail-is/hail/blob/main/dev-docs/development_process.md#merge--deploy).

## Infrastructure

The underlying GCP infrastructure is [configured using Terraform](https://github.com/populationgenomics/hail/blob/main/infra/main.tf). The Terraform state file is stored in the `cpg-hail-terraform` bucket.

Please don't modify any properties for the `hail-295901` project (e.g. permissions for service accounts) using `gsutil` or the GCP Cloud Console UI, as those won't be reflected in the Terraform state. Instead, always modify the Terraform declarations and run the following after your changes have been reviewed:

```bash
cd infra
terraform apply -var-file=global.tfvars
```

## Billing projects

If you have a Hail developer account, you can manage Hail [billing projects](https://batch.hail.populationgenomics.org.au/billing_projects) and [associated budget limits](https://batch.hail.populationgenomics.org.au/billing_limits). It's important to keep in mind that Hail billing projects are completely distinct from GCP projects and are tracked in Hail Batch's database.

When users submit a batch, they specify a billing project which will be charged with the associated resource cost of running the batch. In order to do so, users first need to be [added](https://batch.hail.populationgenomics.org.au/billing_projects) to billing projects. Note that [billing project limits](https://batch.hail.populationgenomics.org.au/billing_limits) are not monthly budgets, but total budgets that don't reset automatically.

Billing projects also determine the visibility of batches. If two users use the same billing project, they can see each other's batches submitted under that billing project.

For each of our [datasets](storage_policies), we have a dedicated Hail billing project. Whenever someone gets added to the dataset's permission group, they should also be added to the corresponding Hail Batch billing project.
