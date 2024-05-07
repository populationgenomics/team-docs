# Hail: Query on Batch Playbook

This playbook will describe some common errors for Hail's Query on Batch, and how to debug them. If you can't find an answer here, please raise an issue on #software-questions, and then come back and update this manual!

Often, you'll use this code snippet (before any Hail Query) to tell Hail Query to use Batch:

```python
from cpg_utils.hail_batch import init_batch
init_batch()
```

This will (as of 2024-05-07), create a second batch (with no title), and you'll see a bunch of jobs labelled like this:

```
execute(...)_driver
execute(...)_stage0_table_coerce_sortedness_job0
execute(...)_stage0_table_coerce_sortedness_job1
execute(...)_stage0_table_coerce_sortedness_job2
```

Note, there are drivers, suffixed with `_driver`, which coordinate work, and workers, which do the work!

## Hail pro tips

> See [Hail prop tips](../hail#hail-query-pro-tips].


## Out of memory

This can manifest in lots of ways:

> - The job exceeds the bounds of the memory available

> ```
> Error summary: OutOfMemoryError: Java heap space
> ```

### Consider re-ordering your analysis

There are lots of ways that Hail Query compute can run out of memory. First, consider if you can restructure your code to reduce the amount of work that's happening. For example, if you can filter a LOT of rows early, before doing work, that's ideal!

```
# this is doing lots of unnecessary work
mt = hl.read_matrix_table("very large table")
mt = mt.annotate_rows(new_col = mt.old_col + 1)
mt = mt.filter_rows(mt.old_col == 1)

# this is doing a lot LESS work!
mt = hl.read_matrix_table("very large table")
mt = mt.filter_rows(mt.old_col == 1)
mt = mt.annotate_rows(new_col = mt.old_col + 1)
```

### Consider checkpointing before a heavy operation

Sometimes Hail just performs better if you checkpoint your analysis, it's not trying to juggle multiple operations. Also a great idea if you're passing an object to a function you don't control, in case it's accidentally causing multiple evaluations.


### Increasing memory

First, you need to work out if your analysis is failing in a worker, or a driver. Look carefully through the failed job to ensure you've got this right.

Please don't keep these as defaults, only apply these settings if you're running out of memory.

Similar for a batch job, you can first specify the memory to be `highmem`:

```python
init_batch(
    driver_memory='highmem',
    worker_memory='highmem',
)
```

Confirm that the job that's failing did actually receive 8GB of memory (per core) before trying the next step. Next, you can increase the number of cores the machine_type gets allocated, again, please don't leave these as the default because it can get expensive. From Batch, cores must be in powers of 2, eg:

```python
init_batch(
    driver_cores=2, # or eventually 4, 8, 16
    worker_cores=2, # or eventually 4, 8, 16
)
```

### File doesn't exist

```
Caused by: is.hail.relocated.com.google.cloud.storage.StorageException: 404 Not Found
GET https://storage.googleapis.com/download/storage/v1/b/<bucket>/o/path%2Fto_file.txt?alt=media
No such object: <bucket>/path/to_file.txt
```

The file (`gs://<bucket>/path/to_file.txt`) didn't exist, or wasn't available to the user running the batch.

*Steps*:

- Check that the file does exist
- Check the user of the failing job (should be `$dataset-$access_level`), and has access to the file.


## The worker failed, but you're looking at a driver job

```
ServiceBackendAPI: ERROR: A worker failed. The exception was written for Python but we will also throw an exception to fail this driver job.
JVMEntryway: ERROR: QoB Job threw an exception.
```

You're looking at the driver for a job (which is sensibly failing), but you need to look at the worker for the actual error.