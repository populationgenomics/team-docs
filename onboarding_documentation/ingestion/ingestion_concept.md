# Why do we ingest?

## Overview

The purpose of this document is to help you understand how the CPG works with genomic data and its associated metadata, with a focus on the initial ingestion of these data. This document is designed to support newcomers at the CPG or for existing staff members who are interested in understanding how ingestion works at our organisation.

The nature of any ingestion process will, by necessity, vary depending on the (meta)data provided and the aim of the ingestion itself. It is therefore very difficult to provide a concise, encapsulated reference document to describe this process. This document is intended to provide a broad foundation that can be used as a jumping off point for further enquiry.

This document is structured loosely in the style of an FAQ. It does not provide a walk-through of how to ingest technically, which exists as a separate tutorial.

## What is ingestion at the CPG?

Ingestion at the CPG is the act of receiving (meta)data, transforming them for storage and uploading them to a storage location. Genomic data and its metadata are combined and stored in the Metamist database using CPG parsing modules to read metadata files and write them as records. This process is best understood as part of a data management continuum, involving human evaluation and intervention that are supported by programmatic tools.

The genomic data we receive and ingest is used in myriad bioinformatics workflows and analysis tools, for both research and clinical interest. A number of different tools used for these workflows have been developed, adapted, or iterated upon to perform analysis on these incredibly complex data. As part of the Centre's data goals, alongside the obvious ones like data integrity, validity, privacy and so on, is reproducibility. We want to make sure analyses are infinitely reproducible if the input data is unchanged. This has implications for the software used in the analysis tools, such as maintaining consistent versioning, but also implications for the data storage mechanisms we use. At the core of this is the metadata storage schema. This schema must remain consistent and fixed, but sufficiently flexible to allow for use with both freshly implemented tools and the old reliable ones.

## Where are ingested (meta)data stored?

Metadata are stored on CPG’s database, [Metamist](https://sample-metadata.populationgenomics.org.au/). Data are stored in [Google Cloud Platform](https://console.cloud.google.com/storage/browser?hl=en-AU&project=cpg-sandbox&prefix=&forceOnBucketsSortingFiltering=true) ‘projects’.

## What happens after (meta)data are ingested?

Ingested (meta)data are accessible using CPG data storage and in the production instance of Metamist. CPG analysts can now access these programmatically to use as input for their analyses using CPG pipelines. Further transformations may also be applied to the original meta(data) through CPG pipeline stages such as Quality Control (QC). The creation of new records in Metamist captures provenance metadata and usage metadata are captured on an ongoing basis to provide a record of how data are used in CPG workflows. Metadata, once uploaded, are not necessarily static and can be updated as required to include newly acquired metadata, for example.

## How are projects initiated?

The catalyst for projects is all context-specific and there is no single specific answer to this question. Projects are supported by the Project Management team, which maintains an [AirTable](https://airtable.com/app62isJvsSz0ziWT/tblFpqx87JOvUlSF6/viwAAW4LjI1hqzIvS?blocks=bipyLQRZiDX3CWVzM) database to track projects. This is an excellent resource that can be used to understand details surrounding a project’s conception, and may include links to external explanatory documents. Background information on a project can help us to understand the importance of the (meta)data that we are working with and their intended use after ingestion has occurred.

‘Projects’ can refer to work where the CPG is collaborating with external organisations to process their genomic data and it can also refer to analysis projects undertaken by the CPG internally.

## How are participants recruited and sequenced for projects?

Depending on the project, participants may be recruited specifically for the study, or may have been recruited into a previous study and consented to reanalysis in future studies. A lot of projects are a mix of old and new data. The scale of the recruitment process varies between small (a few dozen participants, over the course of weeks or months) and large (thousands of participants, over the course of years), depending on the funding and research priority.

## Why do researchers or project leads collaborate with the CPG to store and/or process their (meta)data?

CPG provides genomic storage, processing, analysis and products to collaborators at no additional cost (beyond operating costs). This can allow groups of researchers to access advanced genomic analyses and tools that they would otherwise have access to with the resources they have at hand. The CPG generally does not operate in a for-profit way.

## How does the CPG acquire (meta)data for ingestion?

(Meta)data are received to support projects undertaken by the CPG. The centre does not have a single procedure that specifies how collaborators should share (meta)data with us. As such, there are many potential different processes through which we can receive (meta)data, the most common of which are specified below. Metadata and data are sometimes shared with the CPG simultaneously, sometimes they are shared separately - it all depends on the collaborator.

### Transfer via signed URLs

_Metadata and data_
[Signed URLs](https://cloud.google.com/storage/docs/access-control/signed-urls#overview) are URLs that have permissions applied to them that control who can access the linked resource, and for what duration. They provide an alternative means to access data where the accessor does not have the required credentials to access these in their normal storage locations.

`analysis-runner` contains a script `generic_https_transfer.py` that can be used to download data provided via signed URL.

Signed URLs are often generated and distributed using services, such as [FileSender](https://www.aarnet.edu.au/filesender).

#### Signed URL issues

The use of signed URLs does come with some risk, and if mishandled third parties can download data leading to outcomes such as increased egress fees and/or data breaches.

Anti-virus software can insert text into signed URLs when these are emailed (under certain circumstances). These result in a modified signed URL which will cause the batch download to fail.

Files are zipped using tar.gz, which then require multiple different steps to download and manipulate.

### Transfer via MCRI OwnCloud

_Metadata and data_
[OwnCloud](https://en.wikipedia.org/wiki/OwnCloud) is a free and open source file sharing software solution. MCRI maintains and OwnCloud instance that MCRI/VCGS collaborators will use to transfer (meta)data to the CPG. OwnCloud looks (and behaves) like any browser-based file storage system such as Microsoft Sharepoint.

`analysis-runner` contains a script `owncloud_https_transfer.py` which can be used to assist the download of files using MCRI OwnCloud.

#### OwnCloud issues

There is no way to access (meta)data programmatically that is sent using OwnCloud. At the time of writing, working with bulk transfer in OwnCloud is not possible.

### REDCap

_Metadata_
[REDCap](https://www.project-redcap.org/) is software used to manage participant surveys and databases. REDCap is especially useful as it can aggregate multiple reports into a single ‘final report’ of participant metadata. MCRI maintains an instance of REDCap and this is a common tool that our collaborators use to share metadata with us.

#### REDCap issues

Aggregated reports generated by REDCap can ‘flatten’ multiple surveys into a single tabular representation. Resulting datasets may need to undergo cleaning before their use. Not all rows in this representation will contain meaningful information.

We do not have consistent API access to REDCap and metadata are downloaded manually through the browser-based application.

## What governance processes does the CPG have in place to support ingestion?

(Meta)data ingested at the CPG are human genomics data, which requires stringent legal and ethical agreements to govern their storage and use. The CPG has a range of workflows supported by the Project Management and ‘MAG’ teams that ensure that data is handled securely and is not shared outside of the organisation. Secondary consent forms and other documentation are completed to receive data and to access particular datasets. Forms such as these can also describe return/destruction requirements for the data and other sensitive details.

Even if a collaborator provides you with access to data, you must perform due diligence and ensure that the required agreements are in place before ingesting any data.

Be aware that the majority of the CPG’s software repositories are public. Take care not to commit any (meta)data that contain identifiers that could lead to a data breach.

The CPG only ingests de-identified information.
