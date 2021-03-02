# Reference Data

Reference datasets required for bioinformatic analyses are available in our own
`gs://cpg-reference` Google Cloud Storage bucket, which is located in the
`australia-southeast1` region. Most of the files have been copied over from
`gs://gcp-public-data--broad-references` (which is located in the US). For more
details about that (and other) resource buckets, see the GATK bundle
[documentation](https://gatk.broadinstitute.org/hc/en-us/articles/360035890811).
It is a good idea to document how/when the data was generated/copied below.

- `gs://cpg-reference/hg38/v0/Homo_sapiens_assembly38.fasta`:

  - Copied Feb2021 from `gs://gcp-public-data--broad-references/hg38/v0`. FASTA
    file and index files used more commonly for alignment of sequencing reads.
    Size: approximately 3G fasta + 1.1G fasta.bwt.

- `gs://cpg-reference/hg38/v0/sv-resources/`

  - Copied Mar2021 from
    `gs://gcp-public-data--broad-references/hg38/v0/sv-resources`. Used for
    GATK-SV pipeline (see <https://github.com/broadinstitute/gatk-sv>). Also see
    the README inside the folder. Size: approximately 19.5G in total.
