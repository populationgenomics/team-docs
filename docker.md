# Docker

- [Docker](#docker)
  - [Host in Google Cloud Artifact Registry](#host-in-google-cloud-artifact-registry)
    - [Step 1: Create AR Docker repository](#step-1-create-ar-docker-repository)
    - [Step 2: Build and upload Docker image](#step-2-build-and-upload-docker-image)
      - [Step 2a: Build using only Dockerfile](#step-2a-build-using-only-dockerfile)
      - [Step 2b: Build using Dockerfile and build config](#step-2b-build-using-dockerfile-and-build-config)

Docker is awesome. If you don't know what it is or how to use it, the
[official docs](https://docs.docker.com/get-started/) are a good starting point.

## Host in Google Cloud Artifact Registry

You can host your Docker images in a Google Cloud Artifact Registry (AR)
repository. Here are the basic steps for building a Docker image using
[Cloud Build](https://cloud.google.com/build/docs/quickstart-build) and
subsequently pushing it to AR - the following assume you want to host it in the
`australia-southeast1` region, and that you already have a `Dockerfile`.

### Step 1: Create AR Docker repository

```shell
LOCATION="australia-southeast1"
PROJECT="<project>"
REPO="<repo-name>"

gcloud artifacts repositories create ${REPO} \
    --repository-format "docker" \
    --location ${LOCATION} \
    --description "My awesome Docker repo" \
    --project ${PROJECT}
```

Verify that it was created:

```shell
gcloud artifacts repositories list \
    --project ${PROJECT} \
    --location ${LOCATION}
```

### Step 2: Build and upload Docker image

There are two ways to build Docker images with Cloud Build and upload to AR. For
most cases, a `Dockerfile` is the only file required. For more complex build
workflows, a build config is recommended.

#### Step 2a: Build using only Dockerfile

```shell
IMG="<image-name>"
TAG="<version-tag>"

cd /path/to/Dockerfile

gcloud builds submit \
    --tag ${LOCATION}-docker.pkg.dev/${PROJECT}/${REPO}/${IMG}:${TAG} \
    --region ${LOCATION}
```

#### Step 2b: Build using Dockerfile and build config

- First prepare the build config:

  - The `$PROJECT_ID` variable gets substituted by default.
  - The `steps` field specifies build steps that will be executed by each Docker
    container specified under `name`.
  - The `args` list of arguments get passed to the `name` container.
  - The `images` field specifies the Docker image to be pushed by Cloud Build to
    the AR repo.
  - For more details, see
    [build config overview](https://cloud.google.com/build/docs/build-config)

```text
$ cat cloudbuild.yaml

steps:
- name: 'gcr.io/cloud-builders/docker'
  args: [ 'build', '-t', 'australia-southeast1-docker.pkg.dev/$PROJECT_ID/repo-name/image-name:version-tag', '.' ]
images:
- 'australia-southeast1-docker.pkg.dev/$PROJECT_ID/repo-name/image-name:version-tag'
```

- Next run the build command:

```shell
cd /path/to/Dockerfile

gcloud builds submit \
    --config cloudbuild.yaml \
    --region ${LOCATION}
```
