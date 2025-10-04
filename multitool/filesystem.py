"""Some usefull operations with files and file systems."""

import os


def create_dir_for_file(path):
    """Create directory if it doesn't exist.

    :type path: str
    :param path: Full path to file.
    """
    path_dir = os.path.dirname(os.path.realpath(path))
    if not os.path.isdir(path_dir):
        os.makedirs(path_dir)


def same_filesystem(paths):
    """Check that all files are belongs to the same file system.

    :type path: list
    :param path: List of files to check.

    :rtype: bool
    """
    first_dev = os.stat(os.path.realpath(paths[0])).st_dev
    for path in paths[1:]:
        if os.stat(path).st_dev != first_dev:
            return False
    return True
