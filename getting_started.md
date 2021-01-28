# Welcome to the CPG

This document describes the commonly used technologies at the Centre, together
with some hints on how to use various tools.

## GitHub

All source code is managed in GitHub repositories in the [populationgenomics
organization](https://github.com/populationgenomics). Please let your manager
know if you're not a member of either the [software or analysis
team](https://github.com/orgs/populationgenomics/teams) yet.

We manage projects using GitHub's [project
boards](https://github.com/orgs/populationgenomics/projects) that link to
issues across the different repositories.

If you need a new repository, please reach out to the software team. As a
principle, we try to use public repositories whenever possible.

Please add your `@populationgenomics.org.au` email address in your GitHub
account settings and use this address when setting up your `git` user config.
It's also a good idea to send any notifications for the populationgenomics
organization to your work email address. This can be configured in your GitHub
settings under Notifications.

## Code reviews

There are many advantages of having code reviews:

- Catch bugs and bad design decisions earlier.
- Improve the overall readability and maintainability of the code.
- Spread knowledge about the code base within the team.
- Learn from others by reading their code.

If you're not used to code reviews, don't be intimidated. After a short period
of time, they'll feel very natural. It's one of the best ways to truly work
together on a shared code base.

For code reviews to work well, it's helpful to follow a few general guidelines:

- Don't interpret review comments as criticism of your code. Instead,
  consider them an opportunity to improve the code and learn new techniques.
- It's really important that reviews are done in a timely fashion. Try to
  respond to review requests within 24 hours. If you don't hear back from a
  reviewer, feel free to "ping" them on Slack.
- In order for people to respond quickly to reviews, individual pull requests
  (PRs) need to be small. Don't send thousands of lines of code for review:
  that's not fun for the reviewer, and it's unlikely you'll get good review
  feedback. Instead, send small PRs frequently, so the reviewer can really
  focus on the change.
- If a reviewer doesn't understand the code or has a question about it, it's
  likely that a future maintainer will have a similar problem. Therefore,
  don't just respond to the question using the review comment UI, but think
  about how to make the code more readable. Should there be a clarifying code
  comment, could you change the structure of the code, or rename a function
  or variable to avoid the confusion?
- Code reviews are very different from pair programming. It's an asynchronous
  activity. Make sure to prepare your PR in a way that preempts any questions
  you can anticipate, to speed up the overall process.
- It's normal that there might be a few rounds of back-and-forth. However, a
  review should always be a technically focussed conversation, with the
  common goal to improve the quality of the code. As a reviewer, make
  concrete suggestions on how to improve the code.

It's okay to spend a lot of time on reviews! This is a big part of your
responsibilities, and we really care about high code quality.

To review someone else’s PR, click on "Files changed". This will show the diff
between the old code and the new proposed changes. You can make comments on
specific lines of the code. Feel free to ask questions here, especially if you
don’t understand something! It’s a good idea to think critically about the
changes. There should also be tests either added or existing to make sure the
code changes do not break any existing functionality and actually implement
what was intended.

If there are items for the author to address, then submit your review with
"Request Changes". Otherwise, once you are happy with the changes and all
comments have been addressed, you can "Approve" the PR.

After approving, you can also merge the PR, unless you left any feedback 
during the latest round (even minor one): in this case, it's preferrable to 
leave merging to the author in case the author wants to act on your feedback.

When merging, preferably use "squash merging" to keep the history clean; the 
exception to this are upstream merges where you want to keep all commits.

If you are the person whose code is being reviewed, and your PR is in the
"Request Changes" state, then you’ll need to address their comments by pushing
new commit changes or answering questions. Once you are done, then you can
dismiss their review towards the bottom of the Conversation page.

We set up repositories in a way that requires at least one code review before
you can merge a pull request into the `main` branch. You can freely commit to
any development branches.

## Google Cloud Platform

To make sure we don't run into scalability limits with increasing dataset
sizes, we run all analyses at the Centre in a cloud computing environment. For
now, we're using Google Cloud Platform (GCP), since projects like Terra and
Hail so far work best on GCP.

To install the Google Cloud SDK:

1. Install
   [Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
2. Run the following to create a conda environment called `gcp`:

   ```bash
   conda create --name gcp -c conda-forge google-cloud-sdk
   conda activate gcp
   ```

If you're new to GCP, read the excellent [How to
Cloud](https://github.com/danking/hail-cloud-docs/blob/master/how-to-cloud.md)
guide first.

For better isolation and cost accounting, we create separate GCP projects for
each effort within the Centre. For example, the TOB-WGS effort would have a
dedicated GCP project called `tob-wgs`. It's important to keep in mind that the
GCP project *name* can be distinct from the project *ID*. In general, when you
specify projects, you'll have to use the project ID (e.g.
`gcloud config set project <project-id>`).

Permissions to projects and resources like Google Cloud Storage (GCS) buckets
are managed using Google Groups that are linked to IAM permission roles. Take a
look at our [storage policies](storage_policies) for a much more detailed
description.

It's very important to avoid [network egress
traffic](https://cloud.google.com/vpc/network-pricing#internet_egress) whenever
possible: for example, copying 1 TB of data from the US to Australia costs 190
USD. To avoid these costs, always make sure that the GCP buckets that store
your data are colocated with the machines that access the data (typically in
the `australia-southeast1` region).

The exception to this rule are public buckets that don't have the [Requester
Pays](https://cloud.google.com/storage/docs/requester-pays) feature enabled,
such as `gs://genomics-public-data`, `gs://gcp-public-data--broad-references`,
or `gs://gcp-public-data--gnomad`. Even though data is copied from the US to
Australia when accessing these buckets, we don't get charged for the egress
traffic.

Please avoid storing any non-public data on your laptop, as that increases the
risk of data breaches. Keep in mind that any non-public genomic data is highly
sensitive. Keeping the data in the cloud also avoids incurring any egress costs
that apply when downloading the data.

## Hail

[Hail](https://hail.is) is an amazing open source library and platform for
genomic data analysis, developed at the Broad Institute. Given its proven
scalability and our good relationship with the Hail development team, it's the
Centre's main analysis platform.

To install Hail, use the
[package](https://github.com/populationgenomics/hail/tree/main/conda) in
CPG's conda channel:

1. Install
   [Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
2. Run the following to create a conda environment called `hail`:

   ```bash
   conda create --name hail -c cpg -c bioconda -c conda-forge hail
   conda activate hail
   ```

The Hail [documentation](https://hail.is/docs/0.2/index.html) is a good
starting point. In particular, the
[tutorials](https://hail.is/docs/0.2/tutorials-landing.html) are worth looking
into.

Don't feel discouraged if the "lazy evaluation" model of Hail feels unintuitive
at first. It takes some time getting used to, but it's extremely powerful.

To understand how Hail works on GCP, read the [How to Cloud with
Hail](https://github.com/danking/hail-cloud-docs/blob/master/how-to-cloud-with-hail.md)
guide.

At the moment, using Hail requires launching a Dataproc (Spark) cluster. Please
always set a maximum age for the cluster (`--max-age` below), to avoid
accidental spending in case you forget to stop the cluster after your job has
completed:

```bash
hailctl dataproc start --max-age 2h --region australia-southeast1 my-cluster
```

There's also a [workshop
recording](https://drive.google.com/file/d/1c5us8YSApSGl81CrojeR426wTS2QA53d/view?usp=sharing)
that contains a lot of useful tips, although not everything is applicable to
the Centre.

If you have any Hail related questions, feel free to ask on Slack in the
`#team-analysis` channel. The Hail team is also very responsive in the [Zulip
chat](https://hail.zulipchat.com), but you'll have to take the time zone
difference into account. Finally, there's also an official [discussion
forum](https://discuss.hail.is/).

If you're interested in the Hail internals, this developer focussed
[overview](https://github.com/hail-is/hail/blob/main/dev-docs/hail-overview.md)
is very helpful.

## Hail Batch

[Hail Batch](https://hail.is/docs/batch/service.html) is a generic job
scheduling system: you describe a workflow using a Python API as a series of
jobs consisting of Docker container commands, input and output files, and job
interdependencies. Hail Batch then runs that workflow in GCP using a
dynamically scaled pool of workers.

In the near future, Hail Batch will integrate nicely with the Hail *Query*
component, which means that you won't need to run a Dataproc cluster anymore.
Instead, you'll be able to run scalable Hail analyses directly from Batch,
using a shared pool of worker VMs that also process your other jobs.

To avoid network egress costs, we run our own Hail Batch deployment in
Australia using the `hail.populationgenomics.org.au` domain. Consequently, the
worker VMs are located in the `australia-southeast1` region, which is typically
colocated with the buckets that store our datasets.

The `hailctl` tool you've installed previously can also be used to interact
with Hail Batch. To point it at the correct domain, you have to set up a
deployment configuration:

```bash
mkdir ~/.hail

echo '{"location": "external", "default_namespace": "default", "domain": "hail.populationgenomics.org.au"}' > ~/.hail/deploy-config.json
```

To create a Hail Batch account, visit the [sign-up
page](https://auth.hail.populationgenomics.org.au/signup) using your
@populationgenomics.org.au Google Workspace account. Ignore the redirect to the
notebook page, which currently isn't running. Instead, navigate to the [user
page](https://auth.hail.populationgenomics.org.au/user) to see your account
details.

You should now be able to authenticate from the commandline:

```bash
hailctl auth login
```

To get familiar with the Hail Batch API, check out the
[tutorial](https://hail.is/docs/batch/tutorial.html). There's also a [workshop
recording](https://drive.google.com/file/d/1_Uo_OlKw6dJsBsa6bH5NwMinfLahDX6U/view?usp=sharing)
that explains how to run workflows in Hail Batch.

Note that billing projects in Hail are distinct from GCP projects. Initially,
you're assigned a small trial project. Let the software team know in case your
user needs to have access to an existing billing project or if you need to
create a new billing project.

At the moment, you can submit jobs to Hail Batch by running the "driver"
program (which defines the batch) locally. However, since that's problematic in
terms of reproducibility, we're currently looking into ways to run the driver
itself on Hail Batch, too.

## Terra / Cromwell

While Hail Batch is a very powerful way to define workflows especially when
using Hail Query functionality, a lot of existing genomic pipelines (like
Broad's GATK Best Practices Workflows) run on Cromwell.

While [Terra](https://terra.bio/) is a great way to run such workflows, there
are still a few features missing that would allow us to run production
workflows in Australia.

For now, the best way to run workflows written in CWL or WDL is therefore to
set up your own Cromwell server, which is fairly straightforward using our
[config templates](https://github.com/populationgenomics/cromwell-configs).
