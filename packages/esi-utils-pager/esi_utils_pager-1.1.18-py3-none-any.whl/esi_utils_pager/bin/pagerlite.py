#!/usr/bin/env python

# stdlib imports
import argparse
import json
import logging
import pathlib
import sys
import tempfile
from datetime import datetime
from urllib.request import urlopen

# third party imports
import numpy as np
import pandas as pd

# local imports
from esi_utils_pager.calc import calc_pager_event, calc_pager_events
from esi_utils_pager.config import get_config_file, read_config
from mapio.shake import getHeaderData

EVENT_TEMPLATE = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/{eventid}.geojson"
)

TIMEFMT1 = "%Y-%m-%dT%H:%M:%S"
TIMEFMT2 = "%Y-%m-%dT%H:%M:%S.%f"
DATEFMT = "%Y-%m-%d"


def maketime(timestring):
    outtime = None
    try:
        outtime = datetime.strptime(timestring, TIMEFMT1)
    except Exception:
        try:
            outtime = datetime.strptime(timestring, TIMEFMT2)
        except Exception:
            try:
                outtime = datetime.strptime(timestring, DATEFMT)
            except Exception:
                raise Exception("Could not parse time or date from %s" % timestring)
    return outtime


def set_logging(args):
    loglevel = logging.INFO
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s %(message)s",
        handlers=[logging.StreamHandler()],
    )


def check_input_files(args):
    # check to make sure that any input fatality/econ/semi files/folders actually exist
    file_errors = []

    if args.fatality_file is not None:
        fatpath = pathlib.Path(args.fatality).resolve()
        if not fatpath.exists():
            file_errors.append(f"Input file {fatpath} does not exist.")

    if args.economic_file is not None:
        ecopath = pathlib.Path(args.economic).resolve()
        if not ecopath.exists():
            file_errors.append(f"Input file {ecopath} does not exist.")

    if args.semi_folder is not None:
        semipath = pathlib.Path(args.semi_folder).resolve()
        if not semipath.exists() or not semipath.is_dir():
            file_errors.append(
                f"Input file {semipath} does not exist or is not a directory."
            )
        else:
            inventory_file = semipath / "semi_inventory.xlsx"
            collapse_file = semipath / "semi_collapse_mmi.xlsx"
            casualty_file = semipath / "semi_casualty.xlsx"
            workforce_file = semipath / "semi_workforce.xlsx"
            files_present = 0
            files_present += int(inventory_file.exists())
            files_present += int(collapse_file.exists())
            files_present += int(casualty_file.exists())
            files_present += int(workforce_file.exists())
            if files_present < 4:
                file_errors.append(
                    (
                        "One or more of the required semi-empirical "
                        f"files in {args.semi_folder} are missing."
                    )
                )
    if len(file_errors):
        print("The following file errors have been detected:")
        for file_error in file_errors:
            print(file_error)
        print("Exiting.")
        sys.exit(1)


def write_output(args, dataframe):
    if args.outfile:
        print(f"Saving {len(dataframe)} rows to {args.outfile}")
        if args.outfile.endswith(".xlsx"):
            dataframe.to_excel(args.outfile, index=False)
        else:
            dataframe.to_csv(args.outfile, index=False)
        sys.exit(0)
    else:
        print(dataframe.to_string(index=False))


def run_event(args):
    set_logging(args)
    check_input_files(args)
    config = read_config()
    file_or_url = pathlib.Path(args.file_or_url)
    if file_or_url.exists():
        dataframe = calc_pager_event(
            args.file_or_url,
            config,
            args.semi_folder,
            args.fatality_file,
            args.economic_file,
            args.semi_folder,
        )
    else:
        url = EVENT_TEMPLATE.format(eventid=args.file_or_url)
        with tempfile.TemporaryDirectory() as tempdir:
            with urlopen(url) as fh:
                data = fh.read().decode("utf8")
                jdict = json.loads(data)
                if "shakemap" not in jdict["properties"]["types"]:
                    print(f"No ShakeMap for event {args.eventid}. Exiting.")
                    sys.exit(1)
                shakemap = jdict["properties"]["products"]["shakemap"][0]
                grid_url = shakemap["contents"]["download/grid.xml"]["url"]
                with urlopen(grid_url) as fh2:
                    xdata = fh2.read().decode("utf8")

                tmpgridfile = pathlib.Path(tempdir) / "tmp.xml"
                with open(tmpgridfile, "wt") as fout:
                    fout.write(xdata)
                config = read_config()
                dataframe = calc_pager_event(
                    tmpgridfile,
                    config,
                    args.semi_folder,
                    args.fatality_file,
                    args.economic_file,
                    args.semi_folder,
                )
    write_output(args, dataframe)


def run_batch(args):
    set_logging(args)
    check_input_files(args)
    dataframe = calc_pager_events(
        args.folder,
        args.run_semi,
        args.fatality_file,
        args.economic_file,
        args.semi_folder,
        timerange=args.time_range,
        bounds=args.bounds,
        magrange=args.mag_range,
        depthrange=args.depth_range,
    )
    write_output(args, dataframe)


def main():
    helpstr = (
        "Render complete empirical/semi-empirical PAGER results.\n\n"
        "Default behavior renders PAGER results for a set of earthquakes\n"
        "as a formatted DataFrame with multiple rows of exposure and loss,\n"
        "one row per country, plus a final row with totals. \n"
        "The empirical models are described in the following papers:\n"
        " - Jaiswal, K. S., and Wald, D. J. (2010c). An Empirical Model \n"
        "for Global Earthquake Fatality Estimation. Earthquake Spectra, 26, No. 4, \n"
        "1017-1037\n\n"
        " - Jaiswal, K. S., and Wald, D. J. (2011). Rapid estimation of the \n"
        "economic consequences of global earthquakes. U.S. Geological Survey \n"
        "Open-File Report 2011-1116, 47p.\n\n"
        "The semi-empirical model is described in the following paper:\n"
        "Jaiswal, K. S., Wald, D. J., and D’Ayala, D. (2011). Developing \n"
        "Empirical Collapse Fragility Functions for Global Building Types. \n"
        "Earthquake Spectra, 27, No. 3, 775-795\n\n"
        "The output columns are (in order):\n"
        "EventID: ComCat event ID\n"
        "Time: UTC Event Time (y-m-d h:m:s)\n"
        "LocalTime: Local Event Time (y-m-d h:m:s)\n"
        "Latitude: Event hypocentral latitude\n"
        "Longitude: Event hypocentral longitude\n"
        "Depth: Event hypocentral depth\n"
        "Magnitude: Event magnitude\n"
        "Location: Event location description\n"
        "EpicentralCountryCode: Country containing earthquake epicenter\n"
        "CountryCode: Country code where exposures/losses occur (or Total)\n"
        "MMI01: Population exposure to shaking at MMI level 1\n"
        "...\n"
        "MMI10: Population exposure to shaking at MMI level 10\n"
        "Fatalities: Fatalities due to shaking\n"
        "EconMMI01: Economic exposure to shaking at MMI level 1\n"
        "...\n"
        "EconMMI10: Economic exposure to shaking at MMI level 10\n"
        "Dollars: Economic losses (USD) due to shaking\n"
        "<BuildingType1>: Many building type columns described in Jaiswal 2011.\n"
        "TotalSemiFatalities: Final column summing fatalities across all building types."
    )
    parser = argparse.ArgumentParser(
        description=helpstr,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--run-semi",
        help="Calculate semi-empirical model results as well.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-o", "--outfile", help="Specify output file (.xlsx for Excel, .csv for CSV)"
    )

    parser.add_argument(
        "-f", "--fatality-file", default=None, help="Path to custom fatality Excel file"
    )
    parser.add_argument(
        "-e", "--economic-file", default=None, help="Path to custom economic Excel file"
    )
    parser.add_argument(
        "--semi-folder",
        default=None,
        help=(
            "Path to folder containing custom semi-empirical Excel files. "
            "These files MUST be named semi_inventory.xlsx, "
            "semi_collapse_mmi.xlsx, semi_casualty.xlsx and "
            "semi_workforce.xlsx."
        ),
    )

    subparsers = parser.add_subparsers(help="Sub-commands are available below.")
    event_cmd = subparsers.add_parser(
        "event", help="Run a single event through pagerlite"
    )
    event_cmd.add_argument(
        "file_or_url", help="Path to local ShakeMap grid XML OR ComCat event ID."
    )
    event_cmd.set_defaults(func=run_event)

    batch_cmd = subparsers.add_parser("batch", help="Run many events through pagerlite")
    batch_cmd.add_argument(
        "-f", "--folder", help="A folder containing many ShakeMap *grid.xml files."
    )

    batch_cmd.add_argument(
        "-t",
        "--time-range",
        help="Only process events within given time range.",
        default=None,
        type=maketime,
        nargs=2,
    )
    helpstr = (
        "Only process events within spatial boundary [lonmin lonmax latmin latmax]."
    )
    batch_cmd.add_argument(
        "-b",
        "--bounds",
        metavar=("lonmin", "lonmax", "latmin", "latmax"),
        dest="bounds",
        type=float,
        nargs=4,
        help=helpstr,
    )
    helpstr = "Only process events within depth range [depthmin depthmax]."
    batch_cmd.add_argument(
        "-d",
        "--depth-range",
        metavar=("depthmin", "depthmax"),
        type=float,
        nargs=2,
        help=helpstr,
    )
    helpstr = "Minimum and maximum (authoritative) magnitude to restrict search."
    batch_cmd.add_argument(
        "-m",
        "--mag-range",
        metavar=("minmag", "maxmag"),
        type=float,
        nargs=2,
        help=helpstr,
    )
    batch_cmd.set_defaults(func=run_batch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
