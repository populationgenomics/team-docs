# Hail: Query on Dataproc Playbook

More information about dataproc is available: [here](../cpg-utils/dataproc)

## hail*.whl is not a valid wheel filename

You may see the following error when the `./init_scripts/install_common.sh` script is being executed during cluster initialization:

```log
pip3 install --no-dependencies '/home/hail/hail*.whl'
WARNING: Requirement '/home/hail/hail*.whl' looks like a filename, but the file does not exist
ERROR: hail*.whl is not a valid wheel filename.
```

This is due to the hail wheel not being correctly localised to the image. However, this is likely only a symptom of the root problem:

1. The previous `init_notebook.py` initalisation script does not execute as expected. You'll need to check the `gs://<bucket>/google-cloud-dataproc-metainfo/<job-id>/<cluster-name>-m/dataproc-initialization-script-0_output` file to see exactly what is happening:

    1. In the output log, you'd see something like:

        ```log
        raise ReadTimeoutError(self._pool, None, "Read timed out.")
        pip._vendor.urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
        ```

        It's probably just transient (eg: [https://centrepopgen.slack.com/archives/C030X7WGFCL/p1685164583164109](https://centrepopgen.slack.com/archives/C030X7WGFCL/p1685164583164109))

    1. If the script is empty, the `init_notebook.py` could have timed out. We rely on this hail-provided script to do a bunch of set-up, and this includes copying the `hail*.whl` to the container.

        In this example full log:

        ```log
        ERROR: (gcloud.dataproc.clusters.create) Operation [projects/<dataset>/regions/australia-southeast1/operations/<job-id>] failed: Initialization action timed out. Failed action 'gs://hail-common/hailctl/dataproc/0.2.126/init_notebook.py', see output in: gs://<bucket>/google-cloud-dataproc-metainfo/<job-id>/<cluster-name>-m/dataproc-initialization-script-0_output
        Initialization action failed. Failed action 'gs://cpg-common-main/hail_dataproc/0.2.126/install_common.sh', see output in: gs://<bucket>/google-cloud-dataproc-metainfo/<job-id>/<cluster-name>-m/dataproc-initialization-script-1_output.
        ```

        Very subtly, for `init_notebook.py` the _Initialization action timed out._ That almost certainly means that the python packages we passed to dataproc (in the `--metadata=...|||PKGS=<pkgs>` arg) were challenging for pip to resolve a compatible set of dependencies.

        Long story short, you (+ software team) will need to look at the places python package requirements are specified, and will need to hand resolve some conflicts.

        For example, Hail might specify `botocore==x.x.x`, but also the latest cpg-utils might have `botocore==y.y.y`, so pip will download previous versions of Hail AND cpg-utils looking for two compatible versions, which will almost certainly lead to dataproc timing out the initialization script.

        * [https://centrepopgen.slack.com/archives/C030X7WGFCL/p1715819263267179](https://centrepopgen.slack.com/archives/C030X7WGFCL/p1715819263267179)

1. The hail wheel blob is misconfigured (hence doesn't get copied to the instance, so the wildcard fails to resolve)

    * [https://centrepopgen.slack.com/archives/C030X7WGFCL/p1681793836586189](https://centrepopgen.slack.com/archives/C030X7WGFCL/p1681793836586189)
    * [https://centrepopgen.slack.com/archives/C030X7WGFCL/p1680587094857899?thread_ts=1679886207.438349&cid=C030X7WGFCL](https://centrepopgen.slack.com/archives/C030X7WGFCL/p1680587094857899?thread_ts=1679886207.438349&cid=C030X7WGFCL)
    * [https://centrepopgen.slack.com/archives/C030X7WGFCL/p1669677571568879?thread_ts=1669161375.010299&cid=C030X7WGFCL](https://centrepopgen.slack.com/archives/C030X7WGFCL/p1669677571568879?thread_ts=1669161375.010299&cid=C030X7WGFCL)
