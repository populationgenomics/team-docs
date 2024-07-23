# Cromwell

We use Cromwell at the CPG to run WDL workflows, a common workflow specification built by the Broad Institute. We currently only have a cromwell instance configured for GCP.

We run Cromwell in a similar way to Terra:

- A single deployed instance (with very restrictive credentials)
- Users submit workflows to our instance, WITH the credentials they want to run as.

This functionality is packaged up into cpg-utils - see [cpg-utils:cromwell](../cpg-utils/cromwell) for the user facing guide.

## Authenticating to Cromwell

Cromwell is deployed behind GCP's Identity Aware Proxy + OAuth, so you can access it in the web browser. This also makes it challenging to authenticate programatically as an end user.

## Configuring Cromwell

On GCP, Cromwell is deployed using an instance template, and a self-healing instance group - this means instances are spun up automatically through GCP, and if it fails a health test / gets preempted, a new one starts.

It's important to note that Cromwell is stateful (using a MySQL instance), so restarts is fine, just during a restart Cromwell will be unable to accept new workflow submissions, start new jobs, take metadata requests, etc. But all running jobs will continue to run, unaffected.

Noting that a submitting workflow submits the following workflow options (noting these are encrypted by cromwell):

```jsonc
{
  // private key for the user-service-account
  "user_service_account_json": "",

  // the service account to run as
  "google_compute_service_account": "cromwell-{access-level}@{gcp_project}.iam.gserviceaccount.com",

  "google_project": "{google_project}",

  // temporary directory for workflow outputs
  "jes_gcs_root": "gs://cpg-{dataset}-{access-level}-tmp/cromwell",
  // directory to copy outputs to:
  "final_call_logs_dir": "gs://cpg-{dataset}-{namespace}-analysis/cromwell_logs/{output-dir}",
  "final_workflow_log_dir": "gs://cpg-{dataset}-{namespace}-analysis/cromwell_logs/{output-dir}",
  // copy all outputs to here
  "final_workflow_outputs_dir": "gs://cpg-{dataset}-{namespace}/{output-dir}",

  // extra labels to attach to every GCP resource
  "google_labels": {
    "compute-category": "cromwell",
    "ar-guid": "<ar-guide>"
  }
}
```

### General configuration

These workflow options are used by Cromwell to perform various actions, like:

```hocon
// pulling metadata about images, or other GCP (non-storage) actions
google {
  application-name = "cromwell"
  auths = [
    {
      // use the service-account provided from workflow-options
      name = "user-service-account"
      scheme = "user_service_account"
    },
    {
      // the cromwell-runner service-account, kind of pointless to put it in here
      name = "application_default"
      scheme = "application_default"
    }
  ]
}
engine {
    // perform actions, like read_string, lookup checksums, etc
  filesystems {
    gcs {
      // use the service-account provided from workflow-options
      auth = "user-service-account"
    }
  }
}

workflow-options {
  // These workflow options will be encrypted when stored in the database
  encrypted-fields: [user_service_account_json, google_compute_service_account]
  base64-encryption-key: "<some-key-to-encrypt-values>"
}
```

### Backends

Cromwell runs _compute_ on a [_backend_](https://cromwell.readthedocs.io/en/develop/backends/Backends/). A backend is written for each compute environment, eg: local, HPC (Slurm, SGE, etc), Google Cloud (Pipelines API / Batch), AWS (Batch), GA4GH (for which Microsoft Azure is compatible).

Note that the name of the backends explicitly match code in cpg-utils, so don't change these without further consideration.

The general structure for configuring a backend in Cromwell looks like:

```hocon
backend {
  default = YourNameForTheBackend

  providers {
    YourNameForTheBackend {
      actor-factory = "cromwell.backend.google.pipelines.v2beta.PipelinesApiLifecycleActorFactory"
      config {
        // backend flavour specific config
      }
      filesystems {
        // filesystems to use for the backend
      }
      default-runtime-attributes {
        // stuff like default cpu, regions, zones, etc
      }
    }
  }
}
```

#### Configurable in cpg-utils

We allow a user to configure which backend they want to run (provided as a workflow option). The code for workflow option organisation is aware of this backend attribute, and changes the workflow options depending on the backend.

https://github.com/populationgenomics/cpg-utils/blob/214958b7be037e5153ef60f5d4b71b5be8409db8/cpg_utils/cromwell.py#L39-45

#### Life Science Pipelines API (current)

By default, we currently use the [Google Pipelines API (PAPI)](https://cloud.google.com/life-sciences/docs/reference/rest) which is effectively Docker as a service - you submit a [job spec](https://cloud.google.com/life-sciences/docs/reference/rest/v2beta/projects.locations.pipelines/run#Action) (an image, machine spec, script to run) and GCP does the rest. Note that Cromwell implements this, including copying files in and out.

GCP have deprecated the pipelines API, so we'll soon have to configure Cromwell to use the Batch API.

```hocon
papi {
  actor-factory = "cromwell.backend.google.pipelines.v2beta.PipelinesApiLifecycleActorFactory"
  config {
    project = "<cromwell-gcp-project>"

    # Base bucket for workflow executions, this is unused though
    root = "gs://non-existent-bucket/cromwell/executions"

    # Make the name of the backend used for call caching purposes insensitive to the PAPI version.
    name-for-call-caching-purposes: PAPI

    # Emit a warning if jobs last longer than this amount of time. This might indicate that something got stuck in PAPI.
    slow-job-warning-time: 24 hours

    # Number of workers to assign to PAPI requests
    request-workers = 3

    genomics {
      # A reference to an auth defined in the `google` stanza at the top. This auth is used
      # to create pipelines and manipulate auth JSONs.
      auth = "user-service-account"

      # Endpoint for APIs, no reason to change this unless directed by Google.
      endpoint-url = "https://lifesciences.googleapis.com/"

      # Currently Cloud Life Sciences API is available only in the US, Europe and Asia regions.
      # This might change in the future, the most up-to-date list is available here:
      # https://cloud.google.com/life-sciences/docs/concepts/locations
      # Note that this is only used to store metadata about the pipeline operation.
      # Worker VMs can be scheduled in any region (see default-zones).
      location = "us-central1"
    }

    filesystems {
      gcs {
        auth = "user-service-account"
      }
    }

    default-runtime-attributes {
      cpu: 1
      failOnStderr: false
      continueOnReturnCode: 0
      memory: "2048 MB"
      bootDiskSizeGb: 10
      # Allowed to be a String, or a list of Strings
      disks: "local-disk 10 SSD"
      noAddress: false
      preemptible: 1

      # The zones to schedule worker VMs in. These should be colocated with
      # the regions of your data buckets.
      # https://cromwell.readthedocs.io/en/stable/RuntimeAttributes/#zones
      zones = "australia-southeast1-a australia-southeast1-b australia-southeast1-c"
    }
  }
}

```

#### Batch API (action by July, 2025)

The [Google Batch API](https://cloud.google.com/batch?hl=en) is very similar to the Pipelines API, .... Cromwell support for the [Google Cloud Batch Backend](https://cromwell.readthedocs.io/en/develop/backends/GCPBatch/) is in Alpha.

Preparation plans:

- This batch backend config has already been added to our Cromwell config, but it currently does not work.
- There should be updated in Cromwell-88 that should fix the configuration

This is how we've currently configured GCP Batch in Cromwell:

```hocon
batch {
  actor-factory = "cromwell.backend.google.batch.GcpBatchBackendLifecycleActorFactory"
  config {
    project = "<cromwell-gcp-project>"

    # Base bucket for workflow executions, this is unused though
    root = "gs://non-existent-bucket/cromwell/executions"

    batch-timeout: 14 days

    genomics {
      # A reference to an auth defined in the `google` stanza at the top.  This auth is used to create
      # Batch Jobs and manipulate auth JSONs.
      auth = "user-service-account"

      # https://cloud.google.com/batch/docs/locations
      # Worker VMs can be scheduled in any region (see default-zones).
      location = "australia-southeast1"

      # Specifies the minimum file size for `gsutil cp` to use parallel composite uploads during delocalization.
      # Parallel composite uploads can result in a significant improvement in delocalization speed for large files
      # but may introduce complexities in downloading such files from GCS, please see
      # https://cloud.google.com/storage/docs/gsutil/commands/cp#parallel-composite-uploads for more information.
      #
      # If set to 0 parallel composite uploads are turned off. The default Cromwell configuration turns off
      # parallel composite uploads, this sample configuration turns it on for files of 150M or larger.
      parallel-composite-upload-threshold = 150M
    }

    filesystems {
      gcs {
        auth = "user-service-account"
      }
    }

    default-runtime-attributes {
      cpu: 1
      failOnStderr: false
      continueOnReturnCode: 0
      memory: "2048 MB"
      bootDiskSizeGb: 10
      # Allowed to be a String, or a list of Strings
      disks: "local-disk 10 SSD"
      noAddress: false
      preemptible: 1

      # The zones to schedule worker VMs in. These should be colocated with
      # the regions of your data buckets.
      # https://cromwell.readthedocs.io/en/stable/RuntimeAttributes/#zones
      zones = ["australia-southeast1-a", "australia-southeast1-b", "australia-southeast1-c"]
    }
  }
}
```

### Call caching and Metadata

> See Cromwell's guide on [Call caching](https://cromwell.readthedocs.io/en/develop/cromwell_features/CallCaching/) for more information.

Tl;dr: Cromwell looks at your inputs, command, and job spec, and if it's seen an identical run, it uses those results. Noting that we only store files in the temp bucket for 7 days, we've set call-caching results and metadata to expire after 7 days.

Note, we archive all metadata to `gs://cromwell-metadata-archive`.

```hocon
call-caching {
  enabled = true
  invalidate-bad-cache-results = false
}
services.MetadataService {
  config {
     archive-metadata {
       # A filesystem able to access the specified bucket:
       filesystems {
         gcs {
           # A reference to the auth to use for storing and retrieving metadata:
           auth = "application_default"
         }
       }

       # Which bucket to use for storing the archived metadata
       bucket = "cromwell-metadata-archive"

       # How long to pause between archive attempts with either fail or have nothing to archive:
       backoff-interval = 10 seconds

       # How long to require after workflow completion before going ahead with archiving:
       archive-delay = 3 days

       # How often to send instrumentation metrics. Currently used for workflows left to archive metric
       instrumentation-interval = 1 minute

       # Turn on debug logging from the archiver classes:
       debug-logging = false

       # How many workflows to archive in parallel
       batch-size = 1
     }
    delete-metadata {
      # How long to pause between deletion attempts which fail, or if there's nothing to delete:
      backoff-interval = 10 seconds
      # How long to require after workflow completion before going ahead with deletion:
      deletion-delay = 7 days
      # How often to send instrumentation metrics. Currently used for workflows left to delete metric
      instrumentation-interval = 1 minute
      # Turn on debug logging for the deleter classes:
      debug-logging = false
    }
  }
}
```

### Database

We use a MySQL database (configured with Cloud SQL) for a stateful instance. Note,

## Interacting with Cromwell

> Doc: https://github.com/populationgenomics/cpg-utils/blob/main/cpg_utils/cromwell.py

```hocon
database {
  profile = "slick.jdbc.MySQLProfile$"
  db {
    driver = "com.mysql.cj.jdbc.Driver"
    user = "cromwell"
    url = "jdbc:mysql://<ip-of-database>/cromwell?rewriteBatchedStatements=true&useLegacyDatetimeCode=false&serverTimezone=UTC"
    password = "<password>"
    connectionTimeout = 5000
  }
}
```
