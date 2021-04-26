# Reference Data

Reference datasets required for bioinformatic analyses are available in our own
`gs://cpg-reference` Google Cloud Storage bucket, which is located in the
`australia-southeast1` region. Most of the files have been copied over from
`gs://gcp-public-data--broad-references` (which is located in the US). It is a
good idea to document how/when the data was generated/copied below.

- `gs://cpg-reference/hg38/v0/Homo_sapiens_assembly38.fasta`:

  - Copied Feb2021 from `gs://gcp-public-data--broad-references/hg38/v0`. FASTA
    file and index files used more commonly for alignment of sequencing reads.
    Size: approximately 3G fasta + 1.1G fasta.bwt.

- `gs://cpg-reference/hg38/v0/sv-resources/`

  - Copied Mar2021 from
    `gs://gcp-public-data--broad-references/hg38/v0/sv-resources`. Used for
    GATK-SV pipeline (see <https://github.com/broadinstitute/gatk-sv>). Also see
    the README inside the folder. Size: approximately 19.5G in total.

  - Apr2021: some of the GATK-SV workflows require files from
    `gs://gatk-sv-resources-public`:

    ```shell
    gsutil cp \
      gs://gatk-sv-resources-public/hg38/v0/sv-resources/resources/v1/delly_human.hg38.excl.tsv \
      gs://cpg-reference/hg38/v0/sv-resources/resources/v1/
    ```

- `gs://cpg-reference/gnomad/gnomad_loadings_90k_liftover.ht`

  - Copied Apr2021 from `gs://cpg-ancestry-temporary/gnomad_loadings_liftover_2.1/v0`. Used for selecting variants for PCA analysis. Variants were lifted over from GRCh37 to GRCh38, using the gnomad version 2.1 loadings (gs://gcp-public-data--gnomad/release/2.1/pca). Size: approximately 20MB.  
