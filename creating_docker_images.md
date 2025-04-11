# Creating Docker Images

## Why create docker images?

At CPG, we maintain a set of prebuilt Docker images. If you can't find the image you need, you have the flexibility to create a custom one. Consider creating a new image when developing pipelines or working with third-party software that requires a specific environment. Docker images help you standardize, isolate, and control dependencies, ensuring consistency across development and production environments.

## Getting started

To view the images available for use in CPG you can browse them in
[GCP Artifact Registry](https://console.cloud.google.com/artifacts/docker/cpg-common/australia-southeast1/images?orgonly=true&project=cpg-common&supportedpurview=project)

## How to create an image

1. **Create a Branch**

    In the [images](https://github.com/populationgenomics/images) repository, create a new branch for your image.

2. **Set Up the New Image Directory**

    Create a new folder named after the tool or software you are packaging.

3. **Write the Dockerfile**

    Inside the newly created folder, create a Dockerfile and define the necessary instructions to build your image.

4. **Commit and Push Your Changes**

    Once your Dockerfile is ready, commit the changes and create a pull request (PR) in the repository.

5. **Continuous Integration (CI) and Image Deployment**

    When CI completes, the new image is automatically built and pushed to the [images-dev folder of Artifact Registry](https://console.cloud.google.com/artifacts/docker/cpg-common/australia-southeast1/images-dev?orgonly=true&project=cpg-common&supportedpurview=project).

6. **Test Your Image**

    Depending on your use case, thoroughly test your newly built image to ensure it functions as expected.

7. **Merge and Deploy**

    Once testing is complete and the image is approved, merge the PR. This triggers an automatic deployment to the production version of the Artifact Registry.

By following this process, you ensure a structured, repeatable, and efficient way to manage Docker images within CPG.
