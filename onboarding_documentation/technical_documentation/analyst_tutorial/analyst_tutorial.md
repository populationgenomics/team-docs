As an analyst you will be running analysis jobs via `analysis-runner`, producing output, and then analysing the output. This tutorial will walk you through the process of running an analysis job, and then analysing the output.

In this tutorial, we will begin with raw fastq files and process them using the large-cohort pipeline. This pipeline performs several steps:

1. Aligns the reads to the reference genome.
2. Conducts quality control checks.
3. Calls variants and combines these variant calls.
4. Performs an ancestry analysis.
5. Plots the results of the ancestry analysis.

While the large-cohort pipeline includes additional stages, for the purpose of this tutorial, we will only execute up to and including the Ancestry stage, which carries out Principal Component Analysis (PCA).

For a description of what each stage of the `large-cohort` pipeline does, please see the `large-cohort` pipeline documentation [here](https://github.com/populationgenomics/production-pipelines#large-cohort-workflow)

## Table of Contents
- [1. Getting test data](#getting-test-data)
- [2. Writing a config file](#writing-a-config-file)
- [3. Submitting an analysis job](#submitting-an-analysis-job)
- [4. Analysing the output](#analysing-the-output)

## 1. Getting test data
As an analyst it is vitally important we run our analysis jobs on test data before running them on real data. This is to ensure that the analysis job is working as expected, and that the output is as expected. This is also important to ensure that the analysis job is not going to take too long (and therefore cost too much!) to run on real data. As pipelines are constantly being updated, it is also important to run the analysis job on test data to ensure that the pipeline has not been broken by a recent update.

For this tutorial we will be using the `bioheart` dataset, which is a collection of genomes from different sources. First things first, let's check if you have access to the `bioheart` dataset. To do this, run the following command:

```bash
gsutil ls gs://cpg-bioheart-main/
```

The output of the above should list a number of files ending in `.fastq.gz`. These are read files, which are the input to the pipeline. If you do not see these files, then you do not have access to the `bioheart` dataset, please contact your manager.

### Subsetting the bucket
Our aim is to validate the pipeline's functionality and output by running it on a subset of the bioheart dataset. To do this we will use the script [create_test_subset.py](https://github.com/populationgenomics/metamist/blob/f6c226d08a8ee9875014d8c99cfe119742221efb/scripts/create_test_subset.py) in the metamist repository. This script selects a random set of samples from `bioheart` and copies their read files to the `bioheart-test` bucket. Execute the following command after navigating to the main branch of your metamist repository in the CLI.

To run this script we must first be in the `metamist` repository. So navigate to your `metamist` repository, ensure you're on the `main` branch of `metamist` and then run the following command from CLI:

**Note: We will need to set up more genomes in the actual bucket we're using**
```bash
analysis-runner \                     
--dataset bioheart --description "populate bioheart test subset" --output-dir "bioheart-test" \
--access-level full \
scripts/create_test_subset.py --project bioheart --samples XPG280371 XPG280389 XPG280397 XPG280405 XPG280413 --skip-ped
```
**FOR REFERENCE: The above was taken from [this](https://centrepopgen.slack.com/archives/C03FA2M1MR9/p1700020527448029?thread_ts=1699935103.776929&cid=C03FA2M1MR9) Slack thread**


## 2. Writing a config file

Config files are used to specify the parameters of an analysis job. They are written in TOML format. There is already a great description of config files and how they're used in the `team-docs` repo [here](https://github.com/populationgenomics/team-docs/blob/13755bd51356b50ce11e6be78a76e53ed0a3ccb1/cpg_utils_config.md).

In short; config files contain all the parameters needed to run the job we want such as images, references, specific stages of the pipeline to run, and the input data. They are required for the `analysis-runner` to start.

When running stages in the `large cohort` pipeline there are default config files that are automatically chosen (see the default [here](https://github.com/populationgenomics/production-pipelines/blob/0bcf9775206f10ee91ac197c8c178f844ecad447/cpg_workflows/defaults.toml)) with subsequent user-defined parameters overriding these defaults as necessary. The default config file for the `large cohort` pipeline can be found [here](https://github.com/populationgenomics/production-pipelines/blob/main/configs/defaults/large_cohort.toml) and in it you can see a description of some of the parameters and what they're used for. 

#### Task: Write a config file
- If we are wanting to run the `large cohort` pipeline on the `bioheart-test` dataset, we will need to create a config file that is capable of doing this.
- Have a go at writing your own config file capable of running the `large cohort` pipeline on `bioheart-test` up until the `Combiner` stage. 
- You can use the default config file as a starting point, and then override the necessary parameters to run the pipeline on `bioheart-test`.
- *Hint*: You will **not** need to change anything in the default `large cohort` config file.

<details>
<summary>Click to reveal the config file</summary>

```TOML
[workflow]
input_datasets = ['bioheart-test']
sequencing_type = 'genome'
output_version = '1.0' # Do we want them to specify output_version?
only_sgs = [<list of sequencingGroup IDs>] # to be used to demonstrate how to run on a subset of samples
```

</details>

Once the config file has been written, save it with an appropriate name (e.g. `bioheart-test.toml`) in a directory that makes sense on your local machine. In the following step we will be using `analysis-runner` to submit the job and point it to the config file we have just written.

## 3. Submitting an analysis job
Now that we have a config file, we can submit an analysis job. To do this we will use the `analysis-runner` tool. The `analysis-runner` tool is a command line tool that is used to submit analysis jobs to the cloud.

Because we are running the `large cohort` pipeline we will need to be inside the `Production-pipelines` repository. So in a directory you want to keep `Production-pipelines` in, run the following command:

```bash
git clone --recurse-submodules git@github.com:populationgenomics/production-pipelines.git
cd production-pipelines
```

Ensure you are on the `main` branch.

For guidance on how to use the `analysis-runner` tool, please see the `analysis-runner` documentation [here](https://github.com/populationgenomics/analysis-runner). It will need to be `pip` installed before use.

It is generally good practice to create a bash script that contains the `analysis-runner` command to submit the job. This is so that the command can be easily re-run if necessary.

#### Task: Submit an analysis job
- Using the instructions in the `analysis-runner` repo linked above as well as the config file you have just written, write the command to submit analysis job to the cloud using the `analysis-runner` tool.

<details>
<summary>Click to reveal the command</summary>

```bash
analysis-runner \
--dataset bioheart-test \
--description "Running large cohort up to Combiner stage on bioheart" \
--output-dir "bioheart-test-YOUR-NAME" \
--access-level test \
--config configs/genome.toml \
--config configs/defaults/large_cohort.toml \
--config path/to/you/config/config_filename.toml \
--image australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_workflows:latest \
main.py large_cohort
```
</details>



## 4. Analysing the output

Now that we have some output to work with, lets begin analysing.

Analysis is best done within a Jupyter Notebook. However, in order to interact with our data in the cloud using Hail and jupyter notebooks we need to do some set up first. 

Instructions on setting up a Jupyter Notebook in the cloud can be found [here](https://github.com/populationgenomics/team-docs/blob/main/notebooks.md)

Please continue this tutorial once you have a Jupyter Notebook running in the cloud, good luck!
