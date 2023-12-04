import subprocess

# Run FastQC on the input FASTQ file
fastqe_command = [
    "fastqe",
    "test_fq_r1.fq",
    "test_fq_r2.fq",
    # "--html",
    # ">",
    # "test_fastqe.html",
]
# output = subprocess.run(fastqe_command, stdout=subprocess.PIPE, text=True)

# Run the command and redirect output to a file
with open("test_fastqe.html", "w") as output_file:
    subprocess.run(fastqe_command, stdout=output_file, text=True)

# # Print the output to the console
# print(output.stdout)
