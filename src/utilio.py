from os import mkdir, remove
from os.path import isfile, isdir
from shutil import rmtree
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename
from typing import List, Tuple


def create_workdir(work_directory: str) -> None:
    # Set up a working directory.
    if not isdir(work_directory):
        mkdir(work_directory)
    else:
        rmtree(work_directory)
        mkdir(work_directory)


def delete_workdir(work_directory: str) -> None:
    if not isdir(work_directory):
        rmtree(work_directory)


def delete_file(filepath: str) -> None:
    if isfile(filepath):
        remove(filepath)


def ask_directry() -> str:
    _root = Tk()
    _root.withdraw()
    result = askdirectory()
    _root.destroy()
    return result


def ask_open_file(filetypes: List[Tuple[str, str]]) -> str:
    _root = Tk()
    _root.withdraw()
    result = askopenfilename(filetypes=filetypes)
    _root.destroy()
    return result