# Reproducible analyses

We'd like to be able to reproduce analysis results easily. While that's not
always fully achievable, the strategies below help significantly. Note that this
is only about analyses run on _production_ data, not the development and testing
of new code.

1. _Only run code that has been committed to a repository._

   If locally changed code is used to produce analysis results, those results can't be reproduced if the local changes get lost. To avoid this problem, the [analysis runner](https://github.com/populationgenomics/analysis-runner) runs code from GitHub repositories only.

2. _Link the output data with the exact program invocation of how the data has been generated._

   Even if the code is committed to a repository, it's usually not obvious how a derived dataset was generated. The [analysis runner](https://github.com/populationgenomics/analysis-runner) stores a record in [metamist/analysis-runner](https://sample-metadata.populationgenomics.org.au/analysis-runner/) of every invocation, including an `ar-guid`, the parameters used, and the suggested output directory. NB: Analysis can write files outside this directory.

   Note, as of early 2023, metamist stores an audit log of any metadata changed with an ar-guid if available.


3. _Pin all dependencies of your code to a specific version._

   Docker images, pip, and many other systems let you specify version dependencies. Avoid using "latest", minimum version requirements or version ranges. Instead, always specify an exact version.

   We currently rely on code reviews to spot these issues. Ideally, we'd have a linter that checks the common cases.

4. _Treat output data as immutable._

   If you overwrite (or delete) outputs, any data that has previously been derived from those outputs gets implicitly invalidated. By default we therefore heavily suggest you should only create new data in our [storage policies](storage_policies).
