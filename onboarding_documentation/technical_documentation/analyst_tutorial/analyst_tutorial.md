As an analyst you will be running analysis jobs via the `analysis-runner`, producing output, and then analysing the output. This tutorial will walk you through the process of running an analysis job, and then analysing the output.

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
As an analyst, it's crucial to initially run our analysis jobs on test data before executing them on the actual data. The primary reason for this approach is cost efficiency. Large datasets can be incredibly expensive to process and debug. By using test data, we can estimate the time and cost of running the job on the full dataset, allowing us to optimise resources. Additionally, this process helps us ensure that the pipeline is functioning correctly and producing the expected output. While these checks can also be performed on the main dataset, using test data allows for quicker iterations and adjustments. It's also a good practice to run the analysis job on test data whenever the pipeline is updated, to verify that the updates haven't introduced any issues.

In this tutorial, we will be working with the bioheart project dataset. The BiohEART project aims to identify individuals at risk of atherosclerosis by detecting genetic markers in blood before the disease manifests. Our first step is to verify your access to the bioheart dataset. To do this, execute the following command:

```bash
gsutil ls gs://cpg-bioheart-main-upload/
```

The output of the above command should list a number of files ending in .fastq.gz. These are read files, which serve as the input to the pipeline. If instead you encounter an AccessDeniedException: 403, it means you do not have the necessary access to the bioheart dataset. The error message will look something like this:
```
AccessDeniedException: 403 your.username@populationgenomics.org.au does not have storage.objects.list access to the Google Cloud Storage bucket. Permission 'storage.objects.list' denied on resource (or it may not exist).
```

### Subsetting the bucket
Our goal is to validate the pipeline's functionality and output by running it on a subset of a dataset. For this tutorial, we'll use a subset of the `bioheart` dataset. We'll employ the [create_test_subset.py](https://github.com/populationgenomics/metamist/blob/f6c226d08a8ee9875014d8c99cfe119742221efb/scripts/create_test_subset.py) script from the `metamist` repository to achieve this. It's important to note that this script is not specific to the bioheart project and can be used with any dataset. The script selects a random set of samples from the specified dataset and copies their read files to a test bucket.

Before executing this script, ensure that you have installed all necessary dependencies, which include `gsutil` and `analysis-runner`. The `analysis-runner` is a command-line tool that facilitates the submission of analysis jobs to the cloud. It is instrumental in tracking analysis runs, guaranteeing the reproducibility of analyses, and simplifying the process of conducting analyses. In our setup, direct execution of scripts on production data is not permitted. Instead, we mandate that code be committed, reviewed, and subsequently executed. The `analysis-runner` is the tool that enables this process, acting as a bridge between the user and the cloud resources. It operates by allowing an analyst to submit a request for an analysis via the CLI. The `analysis-runner` server then processes this request, verifies the user's authorisation, creates a Batch pipeline from a specific commit in a GitHub repository, and initiates the analysis on behalf of the user. 

For more information on the analysis-runner please check the repo [here](https://github.com/populationgenomics/analysis-runner) and an exercise [here](https://github.com/populationgenomics/team-docs/tree/main/exercise-analysis-runner). 

If you haven't done so already, clone the `metamist` repository to your local machine. Once you've done that, navigate to your `metamist` repository. Make sure you're on the `main` branch of `metamist`, then execute the following command from the CLI:

**TODO: We will need to set up more genomes in the actual bucket we're using**
```bash
analysis-runner \                     
--dataset bioheart --description "populate bioheart test subset" --output-dir "bioheart-test" \
--access-level full \
scripts/create_test_subset.py --project bioheart --samples XPG280371 XPG280389 XPG280397 XPG280405 XPG280413 --skip-ped
```
**FOR REFERENCE: The above was taken from [this](https://centrepopgen.slack.com/archives/C03FA2M1MR9/p1700020527448029?thread_ts=1699935103.776929&cid=C03FA2M1MR9) Slack thread**


## 2. Writing a config file

Config files, written in TOML format, are used to specify the parameters of an analysis job for the large cohort pipeline. They contain all the necessary parameters to run the job, such as images, references, specific stages of the pipeline to run, and the input data. You can find a comprehensive description of config files and their usage in the `team-docs` repo [here](https://github.com/populationgenomics/team-docs/blob/13755bd51356b50ce11e6be78a76e53ed0a3ccb1/cpg_utils_config.md).

Please note that while config files are essential for the large cohort pipeline, they are not required to start the `analysis-runner`, which is a wrapper that can be used independently.

When running stages in the large cohort pipeline, there are set config files that are used, one of which is the defaults file you can see [here](https://github.com/populationgenomics/production-pipelines/blob/0bcf9775206f10ee91ac197c8c178f844ecad447/cpg_workflows/defaults.toml). It's important to understand that this defaults file does not cover all possible parameters. It provides a base set of parameters, but it may not include every parameter that could be relevant for your specific analysis. User-defined parameters in your specific config file can override these defaults as necessary. You can find the default config file for the large cohort pipeline [here](https://github.com/populationgenomics/production-pipelines/blob/main/configs/defaults/large_cohort.toml), where you can see a description of some of the parameters and their uses.

#### Guide: Write a config file
If we want to run the `large cohort `pipeline on the `bioheart-test` dataset, we need to create a config file that is capable of doing this. Here's a step-by-step guide on how to do it:

Since the default config file serves as our base, we only need to define the parameters that deviate from these defaults. This includes parameters that are left undefined in the default file due to their dataset-specific nature. In this case, we need to specify the input dataset, the sequencing type, and the output version. We also need to specify the sequencing groups we want to run on. We can do this by creating a new config file specifying the following paramters in the `[workflow]` of the `toml` file:

```TOML
[workflow]
input_datasets = ['bioheart-test']
sequencing_type = 'genome'
output_version = '1.0' # TODO: Do we want them to specify output_version?
only_sgs = [<list of sequencingGroup IDs>] # to be used to demonstrate how to run on a subset of samples
```
- `input_datasets`: This parameter specifies the datasets to be loaded as inputs for the analysis. If this parameter is not provided, the datasets will be determined automatically based on the input of `analysis-runner`. It's an array that can contain multiple dataset names e.g. `['bioheart', 'tob-wgs']`.
- `only_sgs`: This parameter is used to limit the analysis to specific `sequencingGroups`. If you want to run the analysis on a subset of sequencing groups, you can specify their IDs in this array.
- `sequencing_type`: This parameter is used to limit the data to a specific sequencing type. The default value is 'genome', but it can be changed to other sequencing types like 'exome' depending on the analysis.
- `output_version`: This parameter is used to suffix the location of the workflow outputs (get_workflow().prefix) with a specific string. By default, the hash of all input paths will be used. This can be useful for versioning your outputs, especially when you run the same analysis multiple times with different parameters or input data.

- Please note that you do not need to change anything in the default `large cohort` config file. The changes you make should be in the new config file you're creating for the `bioheart-test` analysis.

Once the config file has been written, save it with an appropriate name (e.g. `bioheart-test.toml`). Instead of saving it on your local machine, push it to the `production-pipelines-configuration` repository, which is a private repository. In the following step, we will use the `analysis-runner` to submit the job and point it to the config file we have just pushed.

## 3. Submitting an analysis job
Now that we have a config file, we can submit an analysis job. To do this we will use the `analysis-runner` tool. The `analysis-runner` tool is a command line tool that is used to submit analysis jobs to the cloud.

Remember, we are using the `large cohort` pipeline to conduct an analysis of several genomes in the `Bioheart` dataset. As the `large cohort` pipeline is a component of the `Production-pipelines` repository, we need to be within this repository to run it. This means that our current working directory should be the `Production-pipelines` repository when executing the pipeline. So our next step is to clone the `Production-pipelines` repository to our local machine. To do this, execute the following command in a directory of your choosing:

```bash
git clone --recurse-submodules git@github.com:populationgenomics/production-pipelines.git
cd production-pipelines
```

Ensure you are on the `main` branch.

#### Guide: Submit an analysis job
When working in any pipeline with many moving parts, it's important to be able to track the progress of your analysis. As mentioned previously, the `analysis-runner` is our tool of choice for this purpose. Therefore, in order to start our analysis, we point the `analysis-runner` to our config file with parameters specific to our analysis. 

The `analysis-runner` tool is a powerful utility for submitting analysis jobs. Detailed instructions on its usage can be found in the [official documentation](https://github.com/populationgenomics/analysis-runner) (also linked earlier). Before you can use it, ensure it's installed via `pip`.

You have the option to either encapsulate the `analysis-runner` command within a bash script or run it directly from the command line, based on your preference.

Let's break down the structure of an `analysis-runner` command:
- `--dataset`: This parameter specifies the dataset to be loaded as input for the analysis.
- `--description`: This parameter is used to provide a description of the analysis job.
- `--access-level`: This parameter is used to specify the access level of the analysis job. The access level can be either `test` or `full`. The `test` access level is used for test data, while the `full` access level is used for production data.
- `--output-dir`: This parameter is used to specify the output directory for the analysis job. The output directory is where the output files will be stored in the bucket of `dataset` provided (in this case `bioheart-test`)
    - Because we specified the `access-level` as `test`, the output directory will be in the `bioheart-test` bucket. Had we specified `full` as the `access-level`, the output directory would be in the `bioheart-main` bucket.
- `--config`: This parameter is used to specify the config files to be used for the analysis job. The config files are used to specify the parameters of the analysis job. You can specify multiple config files by repeating this parameter.
    - **IMPORTANT:** *The order of the config files is important. The config files are read in the order they are specified. This means that if you specify the same parameter in multiple config files, the value of the parameter in the last config file will be used. This is why the config file we created is listed last as an input.*
- `--image`: This parameter is used to specify the docker image to be used for the analysis job. The docker image is used to specify the environment in which the analysis job will be run.
    - TODO: what else should we say about this?
- `main.py`: This is the Python script that initiates the pipeline. In our scenario, the `large cohort` pipeline is started by this script.
- `large_cohort`: This argument identifies the specific pipeline to execute. Here, it's set to `large_cohort`, indicating that we're running the `large cohort` pipeline, which is initiated by the `main.py` script.

Putting it all together, we get the following:

```bash
analysis-runner \
--dataset bioheart \
--description "Running large cohort up to Combiner stage on bioheart" \
--output-dir "bioheart-test-YOUR-NAME" \
--access-level test \
--config configs/defaults/large_cohort.toml \
--config path/to/you/config/config_filename.toml \
--image australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_workflows:latest \
main.py large_cohort
```


The output of the `analysis-runner` command is link to the Hail Batch driver job. Something like this:
```
Submitting analysis-runner@<commit-sha> for dataset "bioheart"
Request submitted successfully: https://batch.hail.populationgenomics.org.au/batches/<driver-batch-id>
```
This driver job is responsible for setting up all the subsequent jobs to run the analysis. When this driver job is complete, a link to another Hail Batch service will be provided. This is where all the individual jobs of the pipeline will be listed as well as their status. Once this secondary Batch is completed, the output will be available in `bioheart-test`.

## 4. Analysing the output

Now that we have some output to work with, lets begin analysing.

Analysis is best done within a Jupyter Notebook. However, in order to interact with our data in the cloud using Hail and jupyter notebooks we need to do some set up first. 

Instructions on setting up a Jupyter Notebook in the cloud can be found [here](https://github.com/populationgenomics/team-docs/blob/main/notebooks.md).

Once you have your notebook setup on GCP follow along with the instructions in this tutorials accompanying notebook, copying over code as required, good luck!
