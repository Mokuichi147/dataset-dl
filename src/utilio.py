from os import mkdir
from os.path import exists
from shutil import rmtree


def create_workdir(work_directory: str) -> None:
    # Set up a working directory.
    if not exists(work_directory):
        mkdir(work_directory)
    else:
        rmtree(work_directory)
        mkdir(work_directory)


def delete_workdir(work_directory: str) -> None:
    if not exists(work_directory):
        rmtree(work_directory)
