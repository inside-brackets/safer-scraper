"""
This script creates specific files necessary to run scraper.

The script defines a list of file parameters, and you can create these files in the "files" folder
at the project root. You can choose to overwrite existing files if needed.

Usage:
    Run this script from the command line with an optional '-o' or '--overwrite' flag to control
    whether to overwrite existing files.

Example:
    python create_files_for_scraper.py -o
"""

import os
import argparse

from util import create_file, create_folder_if_not_exist

# List of file parameters
file_params = [
    {
        "file_name": "carrier.csv",
        "headers": "mc_number,company_name,dba_name,address,phone_number,usdot_number,power_units,email,c_status,cargo_carried\n",
    },
    {
        "file_name": "limit.txt",
        "headers": "100000",
    },
    {
        "file_name": "start_mc.csv",
        "headers": "MC,Status\n",
    },
    {
        "file_name": "temp.txt",
        "headers": None,
    }
]


def create_files_for_scraper(overwrite=False):
    """
    Create specified files in the 'files' folder at the project root.

    Args:
        overwrite (bool): If True, existing files will be overwritten; if False, existing files are
            preserved.

    Returns:
        None
    """
    project_root = os.getcwd()

    # Create the "files" folder at the project root
    files_folder = os.path.join(project_root, "files")
    create_folder_if_not_exist(files_folder)

    for params in file_params:
        file_path = os.path.join(files_folder, params["file_name"])
        create_file(file_path, params["headers"], overwrite)


def main():
    """
    Main function for running the script. It accepts an optional '-o' or '--overwrite' flag to
    control whether to overwrite existing files.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="Create files in the project root directory")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite existing files")

    args = parser.parse_args()
    create_files_for_scraper(args.overwrite)

if __name__ == "__main__":
    main()
