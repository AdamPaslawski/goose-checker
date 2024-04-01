import os
from contextlib import contextmanager

from dotenv import load_dotenv

load_dotenv()


@contextmanager
def temporary_change_dir(destination):
    """
    Change the current working directory to the specified path,
    and then change it back after exiting the block.
    """
    original_directory = os.getcwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(original_directory)
