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

   1. Within `mysql>`, run the following, but note that you'll have to replace `$NAMESPACE` and `$EMAIL` manually:

      ```sql
      use $NAMESPACE;

      INSERT INTO users (state, username, email, is_developer, is_service_account, tokens_secret_name, gsa_email, gsa_key_secret_name, namespace_name) VALUES ('active', '$NAMESPACE', '$EMAIL@populationgenomics.org.au', 1, 0, '$NAMESPACE-dev-tokens', '$NAMESPACE-dev@hail-295901.iam.gserviceaccount.com', '$NAMESPACE-dev-gsa-key', '$NAMESPACE');
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
