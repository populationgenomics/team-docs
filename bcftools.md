# BCFtools

BCFtools is a widely used, open-source command-line software suite for variant calling and manipulating genomic data in the Variant Call Format (VCF) and its binary counterpart (BCF). [bcftools repository](https://github.com/samtools/bcftools).

A local installation of BCFtools can be useful when interrogating VCF-format files. HTSlib, which BCFtools is built on top of, can be installed in a way which enables reading from files in GCP (or S3...) without having to localise the full file.

This guide walks through the steps required to install a GCS-compatible BCFtools install, avoiding pitfalls like a reliance on MacOS' standard libcurl install which doesn't play nicely with HTSlib.

* install XCode from App store (general purpose build utilities). This installs gcc and other compilers

* run `gcc` to open the xcode license agreement. This will prompt you to run the xcode license agreement in sudo, scroll through and agree to terms:

```commandline
sudo xcodebuild -license
```

* clone the bcftools and htslib repositories, these must be adjacent to each other.

```commandline
git clone --recurse-submodules https://github.com/samtools/bcftools.git
git clone https://github.com/samtools/htslib.git
```

* use homebrew to install `autoconf`, required by the bcftools compilation process, and not available by default on MacOS. May also be provided by XCode?

```commandline
brew install autoconf
```

* use homebrew to install `libcurl`, note that homebrew does not install this as the main curl/libcurl, so the installation needs to be referenced explicitly when the build process takes place, which is done using the export commands*

```commandline
brew install curl xz libdeflate
export PKG_CONFIG_PATH="/opt/homebrew/opt/curl/lib/pkgconfig:$PKG_CONFIG_PATH"
export LDFLAGS="-L/opt/homebrew/opt/curl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/curl/include"
```

* enter the htslib repository, and run configure with libcurl

```commandline
cd htslib
./configure --enable-libcurl
make
```

* enter the bcftools repository, configure and install

```commandline
autoheader
autoconf
./configure --enable-libcurl --enable-gcs --enable-plugins --enable-perl-filters --prefix=/path/to/install/dir
make
make install
```

* validate performance against a public resource

```commandline
bcftools view -h gs://gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr22.vcf.bgz | head
```

* validate performance against a private resource

```commandline
GCS_OAUTH_TOKEN=$(gcloud auth application-default print-access-token) bcftools view -h gs://path-to-a-cpg-vcf/permission/required
```

\* Using a homebrew-sources libcurl was essential for me, the MacOS bundled curl didn't work well with HTSlib. Whilst it was usually able to communicate with GCS, the terminal was filled with `[W::libcurl_open] Retrying open (attempt 1/3)` statements and multiple retries before any data was returned. With the homebrew version
