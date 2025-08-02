# stdlib imports
import logging
import pathlib
import sys
import warnings
from datetime import datetime

# third party imports
import pandas as pd
import rasterio
from esi_utils_time.timeutils import LocalTime
from mapio.shake import getHeaderData
from rasterio.sample import sample_gen

# local imports
from esi_utils_pager.config import get_config_file, read_config
from esi_utils_pager.country import Country
from esi_utils_pager.econexposure import EconExposure
from esi_utils_pager.emploss import EmpiricalLoss
from esi_utils_pager.exposure import Exposure
from esi_utils_pager.semimodel import SemiEmpiricalFatality


def get_pop_year(config, event_year):
    # find the population data collected most closely to the event_year
    pop_year = None
    tmin = 10000000
    popfile = None
    for popdict in config["model_data"]["population_data"]:
        popyear = popdict["population_year"]
        popgrid = pathlib.Path(popdict["population_grid"])
        if not popgrid.is_file():
            print("Population grid file %s does not exist." % popgrid)
            sys.exit(1)
        if abs(popyear - event_year) < tmin:
            tmin = abs(popyear - event_year)
            pop_year = popyear
            popfile = popgrid

    return (pop_year, popfile)


def get_exposure(master_row, isofile, popfile, pop_year, gridfile):
    # Get exposure results

    expomodel = Exposure(popfile, pop_year, isofile)
    exposure = expomodel.calcExposure(gridfile)
    exp_rows = []
    for key, value in exposure.items():
        if key != "TotalExposure" and len(key) != 2:
            continue
        row = {}
        ccode = key
        if key == "TotalExposure":
            ccode = "Total"
        row["CountryCode"] = ccode
        headers = [f"MMI{i:02d}" for i in range(1, 11)]
        mmi_dict = dict(zip(headers, value))
        row.update(mmi_dict)
        exp_rows.append(row)

    expframe = pd.DataFrame(data=exp_rows)
    for key, value in master_row.items():
        expframe[key] = value
    allcols = expframe.columns
    remainder = set(allcols) - set(master_row.keys())
    newcols = list(master_row.keys()) + sorted(list(remainder))
    expframe = expframe[newcols].copy()
    maxmmi_array = []
    for _, row in expframe.iterrows():
        mmi_idx = row[headers] > 1000
        if not len(mmi_idx[mmi_idx].index):
            maxmmi_array.append(0)
            continue
        maxmmi_col = mmi_idx[mmi_idx].index[-1]
        maxmmi_array.append(headers.index(maxmmi_col) + 1)
    expframe["MaxMMI1000"] = maxmmi_array
    return (expframe, exposure)


def get_fatalities(expframe, exposure, fatality_file):
    if fatality_file is None:
        fatmodel = EmpiricalLoss.fromDefaultFatality()
    else:
        fatmodel = EmpiricalLoss.fromExcel(fatality_file)

    fatdict = fatmodel.getLosses(exposure)
    fatdict["Total"] = fatdict.pop("TotalFatalities")
    fatframe = expframe.copy()
    fatframe["Fatalities"] = 0
    for key, value in fatdict.items():
        fatframe.loc[fatframe["CountryCode"] == key, "Fatalities"] = value
    return fatframe


def get_econ_losses(fatframe, popfile, popyear, isofile, gridfile, economic_file):
    if economic_file is None:
        ecomodel = EmpiricalLoss.fromDefaultEconomic()
    else:
        ecomodel = EmpiricalLoss.fromExcel(economic_file)
    econexpmodel = EconExposure(popfile, popyear, isofile)
    econexposure = econexpmodel.calcExposure(gridfile)
    rows = []
    for key, value in econexposure.items():
        if key != "TotalEconomicExposure" and len(key) != 2:
            continue
        row = {}
        ccode = key
        if key == "TotalEconomicExposure":
            ccode = "Total"
        row["CountryCode"] = ccode
        headers = [f"EconMMI{i:02d}" for i in range(1, 11)]
        mmi_dict = dict(zip(headers, value))
        row.update(mmi_dict)
        rows.append(row)
    econframe = pd.DataFrame(data=rows)
    econframe = pd.merge(fatframe, econframe, on="CountryCode")
    ecodict = ecomodel.getLosses(econexposure)
    ecodict["Total"] = ecodict.pop("TotalDollars")
    econframe["Dollars"] = 0
    for key, value in ecodict.items():
        econframe.loc[econframe["CountryCode"] == key, "Dollars"] = value
    return econframe


def get_local_time(etime, timezone_file, lat, lon):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ltime = LocalTime(timezone_file, etime, lat, lon)
        localtime = ltime.getLocalTime()
    return localtime


def get_semi_losses(gridfile, popfile, popyear, isofile, urbanfile, semi_folder):
    if semi_folder is None:
        semimodel = SemiEmpiricalFatality.fromDefault()
    else:
        semi_folder = pathlib.Path(semi_folder)
        inventory_file = semi_folder / "semi_inventory.xlsx"
        collapse_file = semi_folder / "semi_collapse_mmi.xlsx"
        casualty_file = semi_folder / "semi_casualty.xlsx"
        workforce_file = semi_folder / "semi_workforce.xlsx"
        semimodel = SemiEmpiricalFatality.fromFiles(
            inventory_file, collapse_file, casualty_file, workforce_file
        )
    semimodel.setGlobalFiles(popfile, popyear, urbanfile, isofile)
    # Tuple of:
    #         1) Total number of fatalities
    #         2) Dictionary of residential fatalities per building type, per country.
    #         3) Dictionary of non-residential fatalities per building type, per country.
    semifat, resfat, nonresfat = semimodel.getLosses(gridfile)
    return (semifat, resfat, nonresfat)


def calc_pager_event(
    gridfile,
    config,
    run_semi,
    fatality_file,
    economic_file,
    semi_folder,
):
    # get all the basic event information and print it, if requested
    shake_tuple = getHeaderData(gridfile)
    local_time = get_local_time(
        shake_tuple[1]["event_timestamp"],
        config["model_data"]["timezones_file"],
        shake_tuple[1]["lat"],
        shake_tuple[1]["lon"],
    )
    eventid = shake_tuple[1]["event_id"]
    master_row = {}
    master_row["EventID"] = shake_tuple[1]["event_id"]
    master_row["Time"] = shake_tuple[1]["event_timestamp"]
    master_row["LocalTime"] = local_time
    master_row["Latitude"] = shake_tuple[1]["lat"]
    master_row["Longitude"] = shake_tuple[1]["lon"]
    master_row["Depth"] = shake_tuple[1]["depth"]
    master_row["Magnitude"] = shake_tuple[1]["magnitude"]
    master_row["Location"] = shake_tuple[1]["event_description"]
    event_year = shake_tuple[1]["event_timestamp"].year
    isofile = config["model_data"]["country_grid"]
    country = Country()
    with rasterio.open(isofile, "r") as dataset:
        xy = [(shake_tuple[1]["lon"], shake_tuple[1]["lat"])]
        isocode = list(sample_gen(dataset, xy))[0][0]
        ccode = country.getCountry(isocode)["ISO2"]
    master_row["EpicentralCountryCode"] = ccode
    pop_year, popfile = get_pop_year(config, event_year)
    expframe, exposure = get_exposure(master_row, isofile, popfile, pop_year, gridfile)
    fatframe = get_fatalities(expframe, exposure, fatality_file)
    ecoframe = get_econ_losses(
        fatframe, popfile, pop_year, isofile, gridfile, economic_file
    )

    if run_semi:
        urbanfile = config["model_data"]["urban_rural_grid"]
        semifat, resfat, nonresfat = get_semi_losses(
            gridfile, popfile, pop_year, isofile, urbanfile, semi_folder
        )
        resframe = pd.DataFrame(resfat).transpose()
        nonresframe = pd.DataFrame(nonresfat).transpose()
        final_frame = resframe.add(nonresframe)
        final_frame = final_frame.round()
        ny, nx = final_frame.shape
        if nx > 0 and ny > 0:
            ftotal = final_frame.sum(axis="rows")
            final_frame.loc["Total"] = ftotal
            btotal = final_frame.sum(axis="columns")
            final_frame["TotalSemiFatalities"] = btotal
            ecoframe = ecoframe.join(final_frame, on=["CountryCode"])

    return ecoframe


def calc_pager_events(
    gridfolder,
    run_semi,
    fatality_file,
    economic_file,
    semi_folder,
    timerange=None,
    bounds=None,
    magrange=None,
    depthrange=None,
):
    gridfolder = pathlib.Path(gridfolder)
    # read config file
    config = read_config()
    # Make sure grid.xml file exists
    if not gridfolder.is_dir():
        print(f"ShakeMap Grid folder {gridfolder} does not exist.")
        sys.exit(1)

    gridfiles = list(gridfolder.glob("**/*grid.xml"))
    config_dir = pathlib.Path(get_config_file()).parent
    index_file = config_dir / (str(gridfolder).lstrip("/").replace("/", "_") + ".csv")

    if index_file.exists():
        grid_index = pd.read_csv(index_file, parse_dates=["time"])
    else:
        logging.info(f"Building index of input folder {gridfolder}...")
        events = []
        for gridfile in gridfiles:
            # On some systems, there may be backup directories - we don't want these
            # by default, so we'll skip them if we detect backup000 in the path
            if "backup000" in str(gridfile):
                continue
            # get all the basic event information and print it, if requested
            shake_tuple = getHeaderData(gridfile)
            etime = shake_tuple[1]["event_timestamp"]
            eventid = shake_tuple[1]["event_id"]
            elat = shake_tuple[1]["lat"]
            elon = shake_tuple[1]["lon"]
            edepth = shake_tuple[1]["depth"]
            emag = shake_tuple[1]["magnitude"]
            row = {
                "eventid": eventid,
                "time": etime,
                "latitude": elat,
                "longitude": elon,
                "depth": edepth,
                "magnitude": emag,
                "gridfile": gridfile,
            }
            events.append(row)

        grid_index = pd.DataFrame(data=events)
        grid_index["time"] = grid_index["time"].astype("datetime64[ns]")
        grid_index.to_csv(index_file, index=False)
        logging.info("Built index file containing {len(index)} events.")

    timeidx = grid_index["magnitude"] > 0
    boundsidx = grid_index["magnitude"] > 0
    depthidx = grid_index["magnitude"] > 0
    magidx = grid_index["magnitude"] > 0

    if timerange is not None:
        t1 = timerange[0]
        t2 = timerange[1]
        timeidx = (grid_index["time"] >= t1) & (grid_index["time"] < t2)

    if bounds is not None:
        latidx = (grid_index["latitude"] >= bounds[2]) & (
            grid_index["latitude"] < bounds[3]
        )
        lonidx = (grid_index["longitude"] >= bounds[0]) & (
            grid_index["longitude"] < bounds[1]
        )
        boundsidx = latidx & lonidx
    if depthrange is not None:
        depthidx = (grid_index["depth"] >= depthrange[0]) & (
            grid_index["depth"] < depthrange[1]
        )
    if magrange is not None:
        magidx = (grid_index["magnitude"] >= magrange[0]) & (
            grid_index["magnitude"] < magrange[1]
        )
    events = grid_index[timeidx & boundsidx & depthidx & magidx]
    if not len(events):
        logging.info(
            "No events matching criteria in input directory. Returning empty data set."
        )
        return pd.DataFrame({})
    logging.info(f"Processing {len(events)} events...")
    dataframes = []
    for idx, row in events.iterrows():
        gridfile = row["gridfile"]
        logging.info(f"Parsing {gridfile}...")
        dataframe = calc_pager_event(
            gridfile,
            config,
            run_semi,
            fatality_file,
            economic_file,
            semi_folder,
        )
        dataframes.append(dataframe)

    dataframe = pd.concat(dataframes)
    if run_semi:
        # make TotalSemiFatalities column the last one, if it exists
        fatcol = dataframe.pop("TotalSemiFatalities")
        ncols = len(dataframe.columns)
        dataframe.insert(ncols, "TotalSemiFatalities", fatcol)
    return dataframe
