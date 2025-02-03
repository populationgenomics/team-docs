# Docker Images

## Why create docker images?

At CPG, we maintain a set of prebuilt Docker images. If you can't find the image you need, you have the flexibility to create a custom one. Consider creating a new image when developing pipelines or working with third-party software that requires a specific environment. Docker images help you standardize, isolate, and control dependencies, ensuring consistency across development and production environments.

## Getting started

To view the images available for use in CPG you can browse them in
[GCP Artifact Registry](https://console.cloud.google.com/artifacts/docker/cpg-common/australia-southeast1/images?orgonly=true&project=cpg-common&supportedpurview=project)

## How to create an image

1. In repo [images](https://github.com/populationgenomics/images) create new branch

2. Create a new folder, name it according to the name of the tool.

3. Create dockerfile in the newly created folder.

4. TODO When building image based on CPG existing images, do we allow to use 'latest' or should that be fixed version.
**If do not allow latest, then we need to do a migration tasks for all existing dockerfiles !!!**

5. Commit your changes and create PR.

6. Once CI is completed it creates image in [images-dev folder of Artifact Registry](https://console.cloud.google.com/artifacts/docker/cpg-common/australia-southeast1/images-dev?orgonly=true&project=cpg-common&supportedpurview=project)

7. Test your newly created image depending on your use case.

8. Once tested and approved, merged your PR. This will automatically deploy image to [production version of Artifact Registry](https://console.cloud.google.com/artifacts/docker/cpg-common/australia-southeast1/images?orgonly=true&project=cpg-common&supportedpurview=project)
