from pathlib import Path

from importlib_resources import files

# example_a3m_files = [
#     i for i in files("a3mcat.test_data").iterdir() if i.stem != "__init__" # type: ignore
# ]

a3m_file1 = Path(
    files("a3mcat.test_data")
    .joinpath("test_msa_1.a3m")
    .__fspath__()  # type: ignore
)
a3m_file2 = Path(
    files("a3mcat.test_data")
    .joinpath("test_msa_2.a3m")
    .__fspath__()  # type: ignore
)
fasta_file1 = Path(
    files("a3mcat.test_data")
    .joinpath("test_msa_3.fasta")
    .__fspath__()  # type: ignore
)
