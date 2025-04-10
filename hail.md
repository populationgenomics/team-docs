# Hail Query and Hail Batch

[Hail](https://hail.is) is an amazing open source library and platform for genomic data analysis, developed at the Broad Institute that often refers to two things:

- Hail Batch is our pipelining platform of choice, it contains APIs for constructing compute jobs that run in a container, and have dependencies between these jobs.
- Hail (query) is a python framework for manipulating genomics data in a highly parallelised environment (ie: Query on Batch, Spark / Dataproc) - you specify the queries you want, and the framework decides how to distribute this analysis.

Given its proven scalability and our good relationship with the Hail development team, we heavily use both Hail Batch and Hail Query.

To install Hail, run:

```bash
pip3 install hail
```

## Hail Query

The Hail [documentation](https://hail.is/docs/0.2/index.html) is a good starting point. In particular, the [tutorials](https://hail.is/docs/0.2/tutorials-landing.html) are worth looking into. You may also find the following [workshop](https://www.youtube.com/watch?v=GolxWJ477FM&list=PLlMMtlgw6qNg7im-zHSWu7M1N8xigpv4m) recording helpful if you would prefer to watch a live demonstration. Both the tutorials and workshops cover an introduction to Hail through the exploration and analysis of the public 1000 Genomes dataset.

Hail has a "lazy evaluation" model, so it often feels unintuitive at first. It takes some time getting used to, but it's extremely powerful.

To understand how Hail works on GCP, read the [How to Cloud with Hail](https://github.com/danking/hail-cloud-docs/blob/master/how-to-cloud-with-hail.md) guide.

You can use Hail in two environments:

- Using Query on Batch by specifying a service backend (letting Hail Batch manage the distribution).
- Launching a Dataproc (Spark) cluster. Please always set a maximum age for the cluster (`--max-age` below), to avoid accidental spending in case you forget to stop the cluster after your job has completed:

   ```bash
   hailctl dataproc start --max-age 2h --region australia-southeast1 my-cluster
   ```

There's also a [workshop recording](https://drive.google.com/file/d/1c5us8YSApSGl81CrojeR426wTS2QA53d/view?usp=sharing) that contains a lot of useful tips, although not everything is applicable to the Centre.

If you have any Hail related questions, feel free to ask on Slack in the `#team-data` channel. The Hail team is also very responsive in the [Zulip chat](https://hail.zulipchat.com), but you'll have to take the time zone difference into account. Finally, there's also an official [discussion forum](https://discuss.hail.is/).

If you're interested in the Hail internals, this developer focussed [overview](https://github.com/hail-is/hail/blob/main/dev-docs/hail-overview.md) is very helpful. To understand how a query gets translated from Python all the way to the Query backend, see this [description of the query lifecycle](https://github.com/hail-is/hail/blob/main/dev-docs/hail-query/hail-query-lifecycle.md).

### Hail Query Pro Tips

Hail Query uses a deferred execution model - beware! It also does not cache intermediate results. For example:

```python
mt = hl.read_matrix_table(...)
mt = mt.filter(filter1)  # does nothing immediately
mt = mt.filter(filter2)  # does nothing immediately
mt.show()            # hail query excecutes filters 1 + 2
mt.show()            # hail query (again) executes filters 1 + 2
```

You can cache a matrix table using the `.checkpoint("gs://tmp-location")` method, this causes a (relatively uncompressed write), and read, applying any operations during this write. If you're having memory troubles, you may consider checkpointing before other heavy operations to make Hail's life a bit easier.

```python
mt = hl.read_matrix_table(...)
mt = mt.filter(filter1)       # does nothing immediately
mt = mt.checkpoint(tmp_path)  # write + read matrix table to tmp_location
# make sure you checkpoint BEFORE a show, otherwise you'll double execute
mt.show()                     # just read
```

Another consideration when processing large datasets is the number of partitions your data is divided into. If you have all your data in a single partition, each filter or annotation will be run sequentially. If your data is divided into a thousand partitions, Hail Query will operate on each partition in parallel, greatly reducing the overall runtime, and reducing the memory required for each individual operation. There's no exact right or wrong partition size to aim for, but repartitioning data can be done when checkpointing to allow efficiency gains in downstream operations. A useful Zulip thread with syntax on how to repartition a dataset is [here](https://discuss.hail.is/t/best-way-to-repartition-heavily-filtered-matrix-tables/2140)

## Hail Batch

[Hail Batch](https://hail.is/docs/batch/service.html) is a generic job scheduling system: you describe a workflow using a Python API as a series of jobs consisting of Docker container commands, input and output files, and job interdependencies. Hail Batch then runs that workflow in GCP using a dynamically scaled pool of workers.

In the near future, Hail Batch will integrate nicely with the Hail _Query_ component, which means that you won't need to run a Dataproc cluster anymore. Instead, you'll be able to run scalable Hail analyses directly from Batch, using a shared pool of worker VMs that also process your other jobs.

To avoid network egress costs, we run our own Hail Batch deployment in Australia using the `hail.populationgenomics.org.au` domain. Consequently, the worker VMs are located in the `australia-southeast1` region, which is typically colocated with the buckets that store our datasets.

### Local setup

The `hailctl` tool you've installed previously can also be used to interact with Hail Batch. To point it at the correct domain, you have to set up a deployment configuration:

<!-- markdownlint-disable -->

```bash
mkdir ~/.hail

echo '{"location": "external", "default_namespace": "default", "domain": "hail.populationgenomics.org.au"}' > ~/.hail/deploy-config.json
```

<!-- markdownlint-restore -->

_Note:_ If you're going to work on the Hail codebase as a developer, don't sign up as described below. Instead, you should follow the more involved [developer setup](#hail-batch-developer-setup).

To create a Hail Batch account, visit the
[sign-up page](https://auth.hail.populationgenomics.org.au/signup) using your
@populationgenomics.org.au Google Workspace account. Navigate to the [user
page](https://auth.hail.populationgenomics.org.au/user) to see your account
details, including your GCP service account email address.

You should now be able to authenticate from the commandline:

```bash
hailctl auth login
```

To get familiar with the Hail Batch API, check out the
[tutorial](https://hail.is/docs/batch/tutorial.html). There's also a
[workshop recording](https://drive.google.com/file/d/1_Uo_OlKw6dJsBsa6bH5NwMinfLahDX6U/view?usp=sharing)
that explains how to run workflows in Hail Batch.

Note that billing projects in Hail are distinct from GCP projects. Initially,
you're assigned a small trial project. Let the software team know in case your
user needs to have access to an existing billing project or if you need to
create a new billing project.

You can submit jobs to Hail Batch by running the "driver" program (which
defines the batch) locally, which is handy for prototyping and testing.
However, that's problematic in terms of
[reproducibility](reproducible_analyses.md) for analyses run on production data,
as local changes might not be committed to a repository. Instead, you should
use the [analysis runner](https://github.com/populationgenomics/analysis-runner),
which builds a Batch pipeline from a specific commit in a GitHub repository by
running the driver itself on Hail Batch.

### Hail Batch developer setup

If you only intend to use Hail Batch for running your pipelines, you can skip this section. This is meant for developers that work on the Hail Batch codebase.

The [Hail dev-docs](https://github.com/hail-is/hail/tree/main/dev-docs) have articles on developer focused guides to Hail. For example, see [this introduction](https://github.com/hail-is/hail/blob/main/dev-docs/hail-for-new-engineers.md) for a brief history of Hail and an overview of its various components.

1. Instead of using the standard sign-up link, ask another existing Hail developer to create a Hail developer account for you. If you've already signed up, that's okay too, but [a little more work to fix](https://github.com/hail-is/hail/blob/main/dev-docs/services/creating-a-developer-account.md).
1. Ask to be added to the `hail-dev@populationgenomics.org.au` permissions group.
1. Follow the instructions to add an [OAuth 2.0 redirect URI](https://github.com/hail-is/hail/blob/main/dev-docs/services/creating-a-developer-account.md), but note that our GCP project is called `hail-295901`. If your email address is `jane.doe@populationgenomics.org.au`, your Hail `$USERNAME` will be `janedoe` (i.e. does not contain a dot).

## Hail Batch Job Resources

Specifying resources in Hail Batch is straight forward, if you note that:

- The number of CPUs is restricted to powers of 2 (0.25, 0.5, 1, 2, 4, 8, 16)
- The memory is intrinsicially tied to the number of CPUs.

> Note the difference between the between Gigabytes (GB) and Gibibytes (GiB), that:
> | Unit | Standard | Binary |
> | - | ----------- | -------------- |
> | k | kB (1000^1) | kiB (1024^1)   |
> | M | MB (1000^2) | MiB (1024 ^ 2) |
> | G | GB (1000^3) | GiB (1024 ^ 3) |
> | T | TB (1000^4) | TB (1024 ^ 4)  |
> | P | PB (1000^5) | PB (1024 ^ 5)  |

There are 3 categories of machines:

- `lowmem`: ` 1 GB (0.902 GiB) / core
- `standard`: 4 GB (3.8 GiB) / core
- `highmem`: 7 GB (6.5 GiB) / core

| CPUs    |          | 0.25  | 0.5   | 1     | 2     | 4     | 8     | 16     |
| ------- | -------- | ----- | ----- | ----- | ----- | ----- | ----- | ------ |
| **GB**  | lowmem   | 0.25  | 0.5   | 1     | 2     | 4     | 8     | 16     |
| **GB**  | standard | 1     | 2     | 4     | 8     | 16    | 32    | 64     |
| **GB**  | highmem  | 1.75  | 3.5   | 7     | 14    | 28    | 56    | 112    |
|         |          |       |       |       |       |       |       |        |
| **GiB** | lowmem   | 0.226 | 0.451 | 0.902 | 1.804 | 3.608 | 7.216 | 14.432 |
| **GiB** | standard | 0.95  | 1.9   | 3.8   | 7.6   | 15.2  | 30.4  | 60.8   |
| **GiB** | highmem  | 1.625 | 3.25  | 6.5   | 13    | 26    | 52    | 104    |


### Developer deploy

1. Install Hail and login:

   ```bash
   venv hail
   pip install hail
   hailctl auth login
   ```

1. Prepare a change and push it to `$BRANCH` in our Hail fork. Then run a `dev deploy`, which will run the steps you specify as defined in the `build.yaml` file in your branch. The corresponding Kubernetes deployments will be brought up in your own separate namespace, so they won't interfere with the production deployment.

   ```bash
   hailctl dev deploy --branch populationgenomics/hail:$BRANCH --steps deploy_batch
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
      TOKEN=$(jq -r .$NAMESPACE /tmp/tokens.json)
      echo $TOKEN
      ```

   1. You'll now need to add your user to the "auth table" in the SQL instance. First, get a list of all pods, then pick an auth pod, e.g. "auth-6d559bd9b6-npw56".

      ```bash
      kubectl --namespace $NAMESPACE get pod
      ```

   1. Connect to the pod you've selected:

      ```bash
      kubectl --namespace $NAMESPACE exec -it auth-6d559bd9b6-npw56 -- /bin/bash
      ```

   1. On the pod, connect to the SQL instance and set the `$NAMESPACE` variable (the one you exported earlier is not available to the pod). From `sql-config.cnf`, set the variable `$HOST`, and note the `password`. You may need to install the mysql client if the command isn't available, this can be done with `apt update` and `apt install mysql-client`.

      ```bash
      cd /sql-config
      cat /sql-config/sql-config.cnf
      export NAMESPACE="<janedoe>"
      export HOST="<host-from-sql-config.cnf>"
      mysql --ssl-ca=server-ca.pem --ssl-cert=client-cert.pem --ssl-key=client-key.pem --host=$HOST --user=$NAMESPACE-auth-user --password
      ```

   1. Within `mysql>`, run the following, but note that you'll have to replace `$NAMESPACE`, `$EMAIL`, and `$TOKEN` manually:

      ```sql
      use $NAMESPACE-auth;

      INSERT INTO users (state, username, login_id, is_developer, is_service_account, tokens_secret_name, hail_identity, hail_credentials_secret_name, namespace_name) VALUES ('active', '$NAMESPACE', '$EMAIL@populationgenomics.org.au', 1, 0, '$NAMESPACE-dev-tokens', '$NAMESPACE-dev@hail-295901.iam.gserviceaccount.com', '$NAMESPACE-dev-gsa-key', '$NAMESPACE');

      SELECT id, state, username, login_id FROM users;
      ```

      Find the column that contains your new inserted user and note the user_id. Replace that in the following command with the $TOKEN that you saved earlier in your terminal (the env variable will not work here).

      ```sql
      INSERT INTO sessions (session_id, user_id) VALUES ('$TOKEN', '$USER_ID');
      ```

   1. Close the connection to the database and the pod.

   1. Add the correct OAuth redirect url to this page (one-time step).
      On the [Google Cloud Clients Page](https://console.cloud.google.com/auth/clients?project=hail-295901) under `Hail` add the following url:

      ```bash
      https://internal.hail.populationgenomics.org.au/$NAMESPACE/auth/oauth2callback
      ```

   1. Navigate to `https://internal.hail.populationgenomics.org.au/$NAMESPACE/batch/batches` in your browser. Select Batch > Billing Projects and add `$NAMESPACE` to the `test` billing project.

   1. Give your `$NAMESPACE-dev@hail-295901.iam.gserviceaccount.com` Google Service Account the following permissions:

   - _Artifact Registry Reader_ for the `australia-southeast1-docker.pkg.dev/hail-295901/hail` repository (otherwise file localization won't work).
   - _Storage Admin_ permissions for a Hail bucket used for submitting batches, e.g. in your "dev" GCP project.

1. You can now switch to your development namespace like this:

   ```bash
   hailctl dev config set default_namespace $NAMESPACE
   ```

1. Tokens are managed separately for each namespace. To get a token for your developer namespace, run:

   ```bash
   hailctl auth login
   ```

1. You can now run a standard Python script to submit a batch. Use the Hail bucket you've configured earlier, together with the `test` Hail billing project, eg:

   ```python
   #!/usr/bin/env python3

   import hailtop.batch as hb
   from shlex import quote

   name_to_print = "Jane doe"

   b = hb.Batch(
      "my dev deploy job",
      backend=hb.ServiceBackend(
         billing_project="BP in your dev deploy",
         remote_tmpdir="gs://bucket-your-dev-deploy-sa-can-access"
      )
   )

   j1 = b.new_job('first job')
   string_to_print = f'Hello, {name_to_print}'
   j1.command(f'echo {quote(string_to_print)} > {j1.out}')

   j2 = b.new_job('second job')
   # for the second job, using an f-string with the resource file
   # will tell batch to run j2 AFTER j1
   j2.command(f'cat {j1.out}')

   # use wait=False, otherwise this line will hang while the sub-batch runs
   # bad for running hail batch within a hail batch, as preemption
   b.run(wait=False)
   ```

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

Deleting the deployment will not remove the database so to recreate your dev instance you can just run `hailctl dev deploy --branch populationgenomics/hail:$BRANCH --steps deploy_batch` again.


### Debugging

When you need to debug an issue within your namespace, it's often helpful to inspect the logs of the pods that run the service in question. Keep in mind that many services are replicated, so you might have to check multiple pods.

```bash
kubectl --namespace $NAMESPACE get pod
kubectl --namespace $NAMESPACE logs $POD
kubectl --namespace $NAMESPACE exec -it $POD -- /bin/bash

# connect to the database:
apt update && apt install -y mysql-client
mysql --defaults-file=sql-config/sql-config.cnf
```

### Syncing local changes to pod

Instead of manually dev-deploying for every change, you can synchronise your local changes with the k8s pod, using the `devbin/sync.py` script in the Hail repository.

An example usage for making changes to the query API:

- relative path to hail root: `query/query/query.py`
- install location on k8 pod: `/usr/local/lib/python3.7/dist-packages/query/query.py`

```bash
devbin/sync.py \
   --app query \
   --namespace $NAMESPACE \
   --path query/query/query.py /usr/local/lib/python3.7/dist-packages/query/query.py
```

## Merging upstream changes

We try to keep our Hail fork as close as possible to the upstream repository. We merge after each major release, or if there are specific security updates:

1. Check if your .gitconfig includes:

   ```bash
   [merge]
      conflictstyle = diff3
   ```

   or

   ```bash
   [merge]
      conflictstyle = zdiff3
   ```

1. Get the upstream changes into a new branch:
   Set SHA_HASH to the particular hash or upstream/main

   ```bash
   git remote add upstream https://github.com/hail-is/hail.git  # One-time setup.

   git fetch origin
   git fetch upstream
   git checkout -b upstream-XYZ # where XYZ is commit numerical number
   git merge --no-commit SHA_HASH # Commit (SHA_HASH) to be merged, skip the direct commit
   ```

1. Resolve conflicts:
   Use your favourite IDE to resolve conflicts

1. Double check the changes, open two terminals.

   ```bash
   # Terminal ONE run command
   git diff -w da6668bfd58fe915c54f052844db18975ec7abc1..origin/main -- ci/ci/github.py
   ```

   Where da6668bfd58fe915c54f052844db18975ec7abc1 is the last commit when we updated our CPG main branch.
   File 'ci/ci/github.py' is an example, replace with the file you want to check.
   This command shows all the changes done to the file since the last update till now on our CPG main branch

   ```bash
   # Terminal TWO run command
   git diff -w b7bde56d5 -- ci/ci/github.py
   ```

   Where b7bde56d5 is matching the SHA_HASH of the commit we are merging from upstream.
   Again file is just en example, replace with the file you want to check.
   This command shows the changes done to the file with this merging commit after conflict resolution.

   If conflict resolved properly, there should not be much difference between the changes.

1. Create a PR for review

   ```bash
   git push origin upstream-XYZ  # Create a PR as usual.
   ```

1. Before merging (deploy) run terraform script.
   This step only applies if there have been upstream changes to terraform.

   ```bash
   # use gcloud compute ssh command to connect to "hail-setup" VM
   cd ~/hail/infra/gcp  # be sure to be in the right folder on the hail-setup VM
   terraform plan -var-file=populationgenomics/global.tfvars # before apply check what will be changed
   terraform apply -var-file=populationgenomics/global.tfvars # apply the changes
   ```

1. Merge PR, which triggers deploy github action.

   Once the merge creates a CI hail batch, it will send a message to slack #production-announcements, follow the link in the message and check the deploy status. When the whole process finishes (usually around 15 mins), go to the next step.

1. Run smoke test to check basic Hail Batch functionality.

   ```bash
   analysis-runner --access-level test --dataset fewgenomes --description 'Smoke test' --output-dir "$(whoami)/hello-world" hello.py --name-to-print Sparky
   ```

1. After deploying the new version to production, we need to update depending projects with the new hail version:
   - cpg-flow
   - analysis-runner
   - cpg-utils
   - cpg-workflows (will be deprecated)

## Upstreaming changes

Whenever we make a change that isn't purely specific to CPG (like deployment settings), we aim to upstream that change. In general, the process looks like this:

1. Get the change reviewed and deployed locally.
1. Test and double-check everything is working as intended.
1. Create a new branch, based on the current `hail-is/hail:main`, and cherry-pick or rebase your change.
1. Open a standard PR for the `hail-is/hail` repository and coordinate on Zulip to get your PR reviewed.

## Deploying changes to production

After a change has been merged to the `main` branch, it is automatically deployed to the `default` namespace by calling the `prod deploy` API endpoint from a [GitHub workflow](https://github.com/populationgenomics/hail/blob/main/.github/workflows/prod_deploy.yaml). You should therefore only rarely have to start a `prod deploy` manually.

`prod deploy` requires specifying a GitHub commit (SHA), which should generally point at the current `HEAD`, unless you need to roll back. Similar to a `dev deploy`, you can specify the steps from `build.yaml` that should be run (see the [GitHub workflow](https://github.com/populationgenomics/hail/blob/main/.github/workflows/prod_deploy.yaml) for details). Unless there's a good reason to only deploy a particular service, you should replace `$STEPS` below with the same set of steps.

```bash
cd ~/hail
git fetch origin
GITHUB_SHA=$(git rev-parse origin/main)
curl -X POST -H "Authorization: Bearer $(jq -r .default ~/.hail/tokens.json)" \
    -H "Content-Type:application/json" \
    -d "{'sha': '$GITHUB_SHA', 'steps': $STEPS}" \
    https://ci.hail.populationgenomics.org.au/api/v1alpha/prod_deploy
```

This will print a link to the [CI dashboard](https://ci.hail.populationgenomics.org.au/batches) batch.

**Warning**: Some changes that involve a database migration will result in the batch service being shut down. You'll then need to [bring it back up manually](https://github.com/hail-is/hail/blob/main/dev-docs/development-process.md#merge--deploy).

### Hail Batch SQL database

Sometimes there is a need to view SQL content of Hail Batch database. To be able to do that, add the following function to your local .zshrc file:

```bash
kube-hail() {
# Find all pods that match the input name, get the first one
local pod_name=$(kubectl get pods --no-headers=true | grep "$1" | head -n 1 | awk '{print $1}')

# Check if a pod name was found
if [ -z "$pod_name" ]; then
   echo "No matching pod found"
else
   echo "Connecting to $pod_name"
# Execute a shell in the found pod
kubectl exec -it "$pod_name" -- /bin/bash
fi
}
```

Login into the pod:

```bash
kube-hail batch
```

Once in, install mysql-client and open SQL client connection:

```bash
apt update && apt install mysql-client
mysql --defaults-file=sql-config/sql-config.cnf
# execute your SQL command
```

## Infrastructure

The underlying GCP infrastructure is [configured using Terraform](https://github.com/populationgenomics/hail/blob/main/infra/gcp/main.tf). The Terraform state file is stored in the `cpg-hail-terraform` bucket.

Please don't modify any properties for the `hail-295901` project (e.g. permissions for service accounts) using `gsutil` or the GCP Cloud Console UI, as those won't be reflected in the Terraform state. Instead, always modify the Terraform declarations and run the following after your changes have been reviewed:

```bash
cd infra
terraform apply -var-file=global.tfvars
```

### Billing projects

> See [Budgets](budgets.md) for more info

If you have a Hail developer account, you can manage Hail [billing projects](https://batch.hail.populationgenomics.org.au/billing_projects) and [associated budget limits](https://batch.hail.populationgenomics.org.au/billing_limits). It's important to keep in mind that Hail billing projects are completely distinct from GCP projects and are tracked in Hail Batch's database.

When users submit a batch, they specify a billing project which will be charged with the associated resource cost of running the batch. In order to do so, users first need to be [added](https://batch.hail.populationgenomics.org.au/billing_projects) to billing projects. Note that [billing project limits](https://batch.hail.populationgenomics.org.au/billing_limits) are not monthly budgets, but total budgets that don't reset automatically.

Billing projects also determine the visibility of batches. If two users use the same billing project, they can see each other's batches submitted under that billing project.

For each of our [datasets](storage_policies/README.md), we have a dedicated Hail billing project. Whenever someone gets added to the dataset's permission group, they should also be added to the corresponding Hail Batch billing project.

## Updating TLS (HTTPS) certificates

At the moment, this just covers the Google Cloud deployment.

1. Start the [`hail-dev` VM](https://console.cloud.google.com/compute/instancesDetail/zones/australia-southeast1-b/instances/hail-dev?project=hail-295901).
1. Connect to the VM using SSH:

   ```bash
   gcloud compute ssh --zone "australia-southeast1-b" "hail-dev" --project "hail-295901"
   ```

1. Check if your user name is in the `docker` group, if yes skip the next step:

   ```bash
   id
   ```


1. Add yourself to the `docker` group (if not already done previously). Make sure to log out and back in again after running this command:

   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in again
   ```

1. Once connected, you can simply use `curl` or `wget` to fetch the cert renewal script from [Hail Cert Renewal Script](https://github.com/populationgenomics/hail/blob/main/cert_renewal.sh) and run it to automate the next steps with (skip the manual steps, go to step 12 after this command):

   ```bash
   curl -sSL https://raw.githubusercontent.com/populationgenomics/hail/main/cert_renewal.sh | bash
   ```

1. If you wish to do it manually, follow the next steps, clone the GitHub repository (if not already done previously):

   ```bash
   git clone https://github.com/populationgenomics/hail.git
   ```

1. Make sure you're up-to-date on the `main` branch.

   ```bash
   cd hail
   git switch main
   git pull
   ```

1. Make sure the Google Cloud credentials have been set up:

   ```bash
   gcloud config set project hail-295901
   gcloud config set compute/zone australia-southeast1-b
   gcloud auth configure-docker australia-southeast1-docker.pkg.dev
   gcloud components install gke-gcloud-auth-plugin
   gcloud container clusters get-credentials vdc
   ```

1. Now regenerate the certificates, which might take a couple of minutes:

   ```bash
   cd letsencrypt
   make run NAMESPACE=default
   ```

1. Once the above command  has finished successfully, it's time to [restart the Hail services](https://github.com/populationgenomics/hail/blob/main/dev-docs/services/tls-cookbook.md#regenerate-all-the-certificates) to pick up the new certificates. This will cause a very short downtime, but won't interrupt any running batches:

   ```bash
   export HAIL=$HOME/hail

   SERVICES_TO_RESTART=$(python3 -c 'import os
   import yaml
   hail_dir = os.getenv("HAIL")
   x = yaml.safe_load(open(f"{hail_dir}/tls/config.yaml"))["principals"]
   print(",".join(x["name"] for x in x))')

   kubectl delete pods -l "app in ($SERVICES_TO_RESTART)"
   ```

1. Verify that the expiration date for the certificate has been extended:

    ```bash
    echo | openssl s_client -servername batch.hail.populationgenomics.org.au -connect batch.hail.populationgenomics.org.au:443 2>/dev/null | openssl x509 -noout -dates
    ```

1. Don't forget to stop the [`hail-dev` VM](https://console.cloud.google.com/compute/instancesDetail/zones/australia-southeast1-b/instances/hail-dev?project=hail-295901). Please don't delete it!

1. Schedule a Slack message or other reminder to do this again in three months!
