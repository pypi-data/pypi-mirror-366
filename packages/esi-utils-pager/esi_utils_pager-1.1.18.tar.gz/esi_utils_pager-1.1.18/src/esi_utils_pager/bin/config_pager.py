#!/usr/bin/env python

import argparse
import logging
import pathlib
import zipfile

# local imports
from esi_utils_pager.configurator import Configurator


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawTextHelpFormatter,
):
    pass


def configure(args):
    configurator = Configurator(
        args.pager_folder, args.zipfile, pop_zipfile=args.population_file
    )
    cfg_dict, extract_files = configurator.configure()
    configurator.write(cfg_dict, extract_files)


def main():
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
    desc = """Program to automate initial PAGER configuration.

     
    """
    parser = argparse.ArgumentParser(description=desc, formatter_class=CustomFormatter)
    parser.add_argument(
        "zipfile", help="Path to zip file containing all necessary PAGER data."
    )
    dhelp = (
        "Path to top level folder for PAGER data. \n"
        "This folder will contain a 'data' sub-folder \n"
        "with all of the data files \n"
        "from the model data zipfile. Population data \n"
        "will be stored in a 'population' sub-directory under 'data'.\n"
    )
    parser.add_argument(
        "pager_folder",
        default=None,
        help=dhelp,
    )
    parser.add_argument(
        "-p",
        "--population-file",
        help=(
            "Path to zip file containing many years of landscan population data. "
            "Useful only if use case includes running many historical events."
        ),
        default=None,
    )

    args = parser.parse_args()
    configure(args)


if __name__ == "__main__":
    main()
