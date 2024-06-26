import os
from argparse import ArgumentParser

from cpg_utils.config import get_config
from cpg_utils.hail_batch import command, get_batch, image_path, output_path
from metamist.graphql import gql, query

SG_ASSAY_QUERY = gql(
    """
    query ($project: String!, $sgids: [String!]) {
        sequencingGroups(
            project: {eq: $project},
            id: {in_: $sgids}
        ) {
            id
            assays {
                id
                meta
            }
        }
    }
    """
)


def get_assays(project: str, sgids: list) -> dict[str, list[str]]:
    """
    Queries the specified project for sequencing groups and assays, and returns a dictionary mapping sequencing group IDs to read locations.

    Args:
        project (str): The name of the project to query.

    Returns:
        dict: A dictionary where each key is a sequencing group ID and each value is a list of read locations for that sequencing group.
    """
    sg_assay_map = {}

    # Use the query template above to query the sequencing groups and assays
    query_response = query(SG_ASSAY_QUERY, {"project": project, "sgids": sgids})
    for sg in query_response["sequencingGroups"]:
        sg_id = sg["id"]
        for assay in sg["assays"]:
            assay_meta = assay["meta"]
            reads = assay_meta.get("reads")
            if reads is None:
                continue
            sg_assay_map[sg_id] = [read["location"] for read in reads]

    return sg_assay_map


def create_analysis_entry(
    sgid: str,
    last_name: str,
    active: bool = True,
):
    from cpg_utils import to_path
    from cpg_utils.config import get_config
    from cpg_utils.hail_batch import output_path
    from metamist.apis import AnalysisApi
    from metamist.model.analysis import Analysis
    from metamist.model.analysis_status import AnalysisStatus

    # Replace instances of get_config with one config = get_config() at the top of the file
    config = get_config()
    project = config["workflow"]["dataset"]
    if config["workflow"]["access_level"] == "test" and "test" not in project:
        project = f"{project}-test"
    out_web_path = output_path(f"{sgid}-{last_name}.html", "web")
    out_display_path = output_path(f"{sgid}-{last_name}.html", "web_url")

    AnalysisApi().create_analysis(
        project=project,
        analysis=Analysis(
            type="web",
            status=AnalysisStatus("completed"),
            meta={"display_url": out_display_path},
            sequencing_group_ids=[sgid],
            output=out_web_path,
            active=active,
        ),
    )


def main(project: str, sgids: list[str], last_name: str):
    # region: metadata queries
    # This section is all executed prior to the workflow being scheduled,
    # so we have access to all variables

    # Metamist query for files
    file_dict = get_assays(project, sgids)
    # endregion

    # region: Batch time
    b = get_batch("Schedule some worker tasks")
    for sg, files in file_dict.items():
        # check that we have 2 files (assuming FQ, rather than BAM)
        assert len(files) == 2

        # Create a job for each sample
        j = b.new_job("FastQE", {"tool": "fastqe"})

        # Set the docker image to use in this job
        # this pulls the image path from the portion of the config
        # populated by the images repository
        j.image(image_path("fastqe"))
        j.storage("2Gi")

        # read data into the batch tmp resource location
        file_1 = b.read_input(files[0])
        file_2 = b.read_input(files[1])

        # Set the command to run
        # batch.read_input will create a new path like /io/batch/75264c/CPGAAAA_1.fq.gz
        # accessible from inside the job container, and unique to this batch/job
        cmd = f"fastqe {file_1} {file_2} --html > {j.out_fastqe}"
        j.command(
            # f'echo "Hello world, I am a job for {sg}!, using {file_1} and {file_2}"'
            # f'I\'m also creating an output file at {j.output}'
            # f'echo "Some outputs" > {j.output}'
            command(cmd)
        )
        j2 = b.new_python_job(f"Register analysis output for {sg}")
        j2.image(get_config()["workflow"]["driver_image"])
        j2.call(create_analysis_entry, sg, last_name)
        j2.depends_on(j)
        # read the output out into GCP
        # The helper method output_path() will create a new path based on the current project,
        # test/main, and the output prefix provided to analysis_runner
        # -o my_output
        # --dataset my-dataset
        # --access_level test
        # output_path('this_file.txt')
        # -> gs://cpg-my-dataset-test/my_output/this_file.txt
        b.write_output(
            j.out_fastqe, output_path(f"{sg}-{last_name}.html", category="web")
        )  # category='web' writes it to the web bucket
    b.run(wait=False)

    # endregion


if __name__ == "__main__":
    # optional direct input of samples
    parser = ArgumentParser(description="Hail Batch FastQE")
    parser.add_argument("--project", help="Project name", required=True)
    parser.add_argument(
        "--sgids", nargs="+", help="Sequencing group IDs", required=True
    )
    parser.add_argument("--last-name", help="Last name", required=True)
    args, fails = parser.parse_known_args()

    if fails:
        raise ValueError(f"Failed to parse arguments: {fails}")
    main(project=args.project, sgids=args.sgids, last_name=args.last_name)
