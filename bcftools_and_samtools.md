# BCFtools & SAMtools

[BCFtools](https://github.com/samtools/bcftools) is a widely used, open-source command-line software suite for variant calling and manipulating genomic data in the Variant Call Format (VCF) and its binary counterpart (BCF). A local installation of BCFtools can be useful when interrogating VCF-format files. HTSlib, which BCFtools is built on top of, can be installed in a way which enables reading from files in GCP (or S3...) without having to localise the full file.

[SAMtools](https://github.com/samtools/SAMtools) is a similar tool, aimed at reading and manipulating read files (SAM/BAM/CRAM).

This guide walks through the steps required to install a GCS-compatible BCFtools & SAMtools install, avoiding pitfalls like a reliance on MacOS' standard libcurl install which doesn't play nicely with HTSlib.

## Prerequisites

* install XCode from App store (general purpose build utilities). This installs gcc and other compilers

* run `gcc` to open the xcode license agreement. This will prompt you to run the xcode license agreement in sudo, scroll through and agree to terms:

```commandline
sudo xcodebuild -license
```

* use homebrew to install `autoconf`, required by the bcftools compilation process, and not available by default on MacOS. May also be provided by XCode?

```commandline
brew install autoconf
```

* use homebrew to install `libcurl`. Note that homebrew does not install this as the main curl/libcurl, so the installation needs to be referenced explicitly when the build process takes place, which is done using the export commands

```commandline
brew install curl xz libdeflate
export PKG_CONFIG_PATH="/opt/homebrew/opt/curl/lib/pkgconfig:$PKG_CONFIG_PATH"
export LDFLAGS="-L/opt/homebrew/opt/curl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/curl/include"
```

* clone the HTSlib repository, including all nested submodules

```commandline
git clone --recurse-submodules https://github.com/samtools/htslib.git
```

* enter the htslib repository, and run configure with libcurl

```commandline
cd htslib
./configure --enable-libcurl
make
cd ..
```

> nb. Using a homebrew-sourced libcurl was essential for me, the MacOS bundled curl didn't work well with HTSlib. Whilst it was eventually able to communicate with GCS, the terminal was filled with `[W::libcurl_open] Retrying open (attempt 1/3)` statements and multiple retries before any data was returned. With the homebrew version there were no fail/retries, and GCS access was smooth.

## BCFtools install

* clone the BCFtools repository, this must be adjacent to HTSlib.

```commandline
git clone https://github.com/samtools/bcftools.git
```

* enter the BCFtools repository, configure and install

```commandline
cd bcftools
autoheader
autoconf
./configure --enable-libcurl --enable-gcs --enable-plugins --enable-perl-filters --prefix=/path/to/install/dir --with-htslib=/path/to/htslib/repository
make
make install
cd ..
```

* validate performance against a public resource

```commandline
bcftools view -h gs://gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr22.vcf.bgz | head
```

* validate performance against a private resource

```commandline
GCS_OAUTH_TOKEN=$(gcloud auth application-default print-access-token) bcftools view -h gs://path-to-a-cpg-vcf/permission/required
```

## SAMtools install

This follows the exact same protocol as before, with the same pre-requisites. If you keep the same terminal open after the BCFtools install, all prior installs/exports will still be correctly set.

* download the SAMtools repository

```commandline
git clone https://github.com/samtools/samtools.git
```

* enter the repository, and install the contents

```commandline
cd samtools
autoheader
autoconf
./configure --enable-libcurl --enable-gcs --enable-plugins --enable-perl-filters --prefix=/path/to/install/dir --with-htslib=/path/to/htslib/repository
make
make install
cd ..
```

* validate the installation

```commandline
GCS_OAUTH_TOKEN=$(gcloud auth application-default print-access-token) samtools view -h gs://path-to-a-cpg-bam/permission/required
```

## Auth Token

`GCS_OAUTH_TOKEN` is the environment variable used by HTSlib to find an authentication token for interacting with `GCS`. The example command above shows how you can create a new token and assign it to `GCS_OAUTH_TOKEN` as part of the command, but you can also generate it once and use across multiple commands:

```commandline
export
```

You can also create a helper method in your `~/.bashrc` or `~/.zshrc` with a tidy alias:

```commandline
gcs_auth() {
  export GCS_OAUTH_TOKEN=$(gcloud auth print-access-token)
}
```

Calling this within a terminal session will set an authentication token until the end of your session/tab. You can also add the export directly to your `.bashrc/.zshrc`, with the caveat that it will run every time you open a new tab, even if you don't plan to use it.
