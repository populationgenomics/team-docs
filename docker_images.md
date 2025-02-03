# Docker Images (Images for short)

## Why would one want to create an image

At CPG we have already set of docker images prepared, if you can't find image you need, then you are able to create your own.
You can consider creating a new image, when you are developing pipelines, you are using third party software
tool.
Immages allow you to compartmentalise and control your environment.

## Getting started

To view the images available for use in CPG you can browse them in
[GCP Artifact Registry](https://console.cloud.google.com/artifacts/docker/cpg-common/australia-southeast1/images?orgonly=true&project=cpg-common&supportedpurview=project)

## How to create an image

1. In repo [images](https://github.com/populationgenomics/images) create new branch

2. Create a new folder, name it according to the name of the tool.

3. Create dockerfile in the newly created folder.

4. TODO When building image based on CPG existing images, do we allow ot use 'latest' or should that be fixed version.
**If do not allow latest, then we need to do a migration tasks for all existing dockerfiles !!!**

5. Commit your changes and create PR.

6. Once CI is completed it creates image in [images-dev folder of Artifact Registry](https://console.cloud.google.com/artifacts/docker/cpg-common/australia-southeast1/images-dev?orgonly=true&project=cpg-common&supportedpurview=project)

7. Test your newly created image depending on your use case.

8. Once tested and approved, merged your PR. This will automatically deploy image to [production version of Artifact Registry](https://console.cloud.google.com/artifacts/docker/cpg-common/australia-southeast1/images?orgonly=true&project=cpg-common&supportedpurview=project)

