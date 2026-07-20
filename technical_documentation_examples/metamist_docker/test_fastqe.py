"""
Jobs to run FastQE.
"""

from os.path import basename

import hailtop.batch as hb
from hailtop.batch.job import Job

from cpg_utils import Path
from cpg_utils.hail_batch import command
from cpg_utils.hail_batch import image_path
from cpg_workflows.filetypes import (
    BamPath,
    FastqPath,
)
from cpg_workflows.resources import STANDARD


def fastqe(
    b: hb.Batch,
    output_html_path: Path,
    output_zip_path: Path,
    input_path1: BamPath | FastqPath,
    input_path2: BamPath | FastqPath,
    job_attrs: dict | None = None,
) -> Job:
    """
    Adds FastQE jobs. If the input is a set of fqs, runs FastQE on each fq file.
    """
    j = b.new_job("FASTQE", (job_attrs or {}) | {"tool": "fastqe"})
    j.image(image_path("fastqe"))
    threads = STANDARD.set_resources(j, ncpu=16).get_nthreads()

    cmd = ""
    input_file1: str | hb.ResourceFile = b.read_input(str(input_path1))
    input_file2: str | hb.ResourceFile = b.read_input(str(input_path2))
    fname1 = basename(str(input_path1))
    fname2 = basename(str(input_path2))

    cmd += f"""\
    mkdir -p $BATCH_TMPDIR/outdir
    fastqe {input_file1} {input_file2} \\
    --outdir $BATCH_TMPDIR/outdir
    ls $BATCH_TMPDIR/outdir
    ln $BATCH_TMPDIR/outdir/*_fastqe.html {j.out_html}
    ln $BATCH_TMPDIR/outdir/*_fastqe.zip {j.out_zip}
    unzip $BATCH_TMPDIR/outdir/*_fastqe.zip
    """
    j.command(command(cmd, monitor_space=True))
    b.write_output(j.out_html, str(output_html_path))
    b.write_output(j.out_zip, str(output_zip_path))
    return j
