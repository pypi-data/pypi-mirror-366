# Table of Contents
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Installation](#installation)
- [Upgrading](#upgrading)
- [Required data](#required-data)
- [Configuration (for calc\_pager\_event API usage and command line usage)](#configuration-for-calc_pager_event-api-usage-and-command-line-usage)
- [Command Line Usage](#command-line-usage)
- [Library Usage](#library-usage)

# Introduction

This library of tools forms the modeling core of the Prompt Assessment for Global Earthquake Response (PAGER) system,
which provides fatality and economic loss impact estimates following significant earthquakes worldwide. The models implemented here are based on work described in the following papers:

```
Jaiswal, K. S., and Wald, D. J. (2010). An Empirical Model for Global Earthquake Fatality Estimation. Earthquake Spectra, 26, No. 4, 1017-1037
```

```
Jaiswal, K. S., and Wald, D. J. (2011). Rapid estimation of the economic consequences of global earthquakes. U.S. Geological Survey Open-File Report 2011-1116, 47p.
```

```
Jaiswal, K. S., Wald, D. J., and D’Ayala, D. (2011). Developing Empirical Collapse Fragility Functions for Global Building Types. Earthquake Spectra, 27, No. 3, 775-795
```

The software here can be used for other applications, although it is important to note that the empirical loss models
have not been calibrated with events newer than 2010, and the semi-empirical fatality model results are less accurate than the empirical equivalent.

# Installation

`pip install esi-utils-pager`

# Upgrading

`pip install --upgrade esi-utils-pager`

# Required data

A number of data files external to the repository are required for usage:

 - Population grid, which can be obtained from Oakridge National Labs [Landscan project](https://landscan.ornl.gov/about)
 - Country code grid, which can be obtained upon request from the PAGER team.
 - Urban/rural code grid, obtained from the Socioeconomic Data and Applications Center [(SEDAC)](https://sedac.ciesin.columbia.edu/data/collection/grump-v1)

# Configuration (for calc_pager_event API usage and command line usage)
To run the `pagerlite` program (see below), you must first create a `.losspager/config.yml` file in your home directory. 
You can make the .losspager directory using this command (on Linux and Mac platforms):

`mkdir ~/.losspager`

You may then create the config.yml file in that directory using your text editor of choice. 
This file should look like the following: 

```
#############Minimum PAGER configuration################
#This is where output data goes
output_folder: /data/pagerdata/output/

#Anything not already captured by PAGER event logs will be written here
log_folder: /data/pagerdata/logs

#This section describes all the data needed to run models and make maps
model_data:
  timezones_file: /data/pagerdata/model_data/combined_shapefile.shp
  country_grid: /data/pagerdata/model_data/countriesISO_Aug2022_withbuffer.tif
  population_data:
  - {population_grid: /data/pagerdata/model_data/population/lspop2018.flt, population_year: 2018}
  urban_rural_grid: /data/pagerdata/model_data/glurextents.bil
```


# Command Line Usage
The command line program made available by this repository is `pagerlite`. This program outputs detailed empirical
(fatality/economic) PAGER model results to a tabular format. The help for this program (`pagerlite -h`):

```
positional arguments:
  {event,batch}         Sub-commands are available below.
    event               Run a single event through pagerlite
    batch               Run many events through pagerlite

optional arguments:
  -h, --help            show this help message and exit
  -s, --run-semi        Calculate semi-empirical model results as well.
  -o OUTFILE, --outfile OUTFILE
                        Specify output file (.xlsx for Excel, .csv for CSV)
  -v, --verbose         Print progress output to the screen
  -f FATALITY_FILE, --fatality-file FATALITY_FILE
                        Path to custom fatality Excel file
  -e ECONOMIC_FILE, --economic-file ECONOMIC_FILE
                        Path to custom economic Excel file
  --semi-folder SEMI_FOLDER
                        Path to folder containing custom semi-empirical Excel files. These files MUST be named
                        semi_inventory.xlsx, semi_collapse_mmi.xlsx, semi_casualty.xlsx and semi_workforce.xlsx.
```

There are two subcommands for pagerlite:

 - `pagerlite event` Run on a single event specified by ComCat event ID OR path to grid.xml.
 - `pagerlite batch` Run pagerlite on a directory containing many grid.xml files 
    (these files can be in sub-directories).

The event subcommand is straightforward (`pagerlite event -h`):

```
usage: pagerlite event [-h] file_or_url

positional arguments:
  file_or_url  Path to local ShakeMap grid XML OR ComCat event ID.

optional arguments:
  -h, --help   show this help message and exit
```

The `batch` subcommand has a number of optional arguments (`pagerlite batch -h`):

```
usage: pagerlite batch [-h] [-f FOLDER] [-t TIME_RANGE TIME_RANGE] [-b lonmin lonmax latmin latmax]
                       [-d depthmin depthmax] [-m minmag maxmag]

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        A folder containing many ShakeMap *grid.xml files.
  -t TIME_RANGE TIME_RANGE, --time-range TIME_RANGE TIME_RANGE
                        Only process events within given time range.
  -b lonmin lonmax latmin latmax, --bounds lonmin lonmax latmin latmax
                        Only process events within spatial boundary [lonmin lonmax latmin latmax].
  -d depthmin depthmax, --depth-range depthmin depthmax
                        Only process events within depth range [depthmin depthmax].
  -m minmag maxmag, --mag-range minmag maxmag
                        Minimum and maximum (authoritative) magnitude to restrict search.
```

## Examples

To run the PAGER empirical models *only* on a ShakeMap grid.xml file in the current directory and write the results to an Excel file:

`pagerlite -o output.xlsx event grid.xml`

To run the PAGER empirical models *only* on a directory containing (potentially) many sub-directories with 
files ending in "grid.xml":

`pagerlite -o output.xlsx batch -f /data/shakemap_output/`

To run the PAGER empirical models *only* on a ComCat event ID (this will download the authoritative 
ShakeMap grid.xml file from ComCat):

`pagerlite -o output.xlsx batch us7000lz23 `

To run the PAGER empirical AND semi-empirical models, simply add the `-s` flag to any of the above commands:

`pagerlite -s -o output.xlsx batch us7000lz23`

To run the PAGER empirical models on a folder but only for events between 2010 and 2017:

`pagerlite -o output.xlsx batch -f /data/shakemap_output/ -t 2010-01-01 2017-12-31T23:59:59`

To run PAGER empirical models on a folder but only for events in Japan:
`pagerlite -o output.xlsx batch -f /data/shakemap_output/ -b 30.844021 44.762578 128.336525  149.031827`

It is possible to provide your own PAGER input files for the empirical fatality and economic models, 
and for the semi-empirical fatality model. These files can be found in the repository:

 - [Empirical fatality model](https://code.usgs.gov/ghsc/esi/esi-utils-pager/-/raw/main/src/esi_utils_pager/data/fatality.xlsx?ref_type=heads):
 - [Empirical economic model](https://code.usgs.gov/ghsc/esi/esi-utils-pager/-/raw/main/src/esi_utils_pager/data/economic.xlsx?ref_type=heads)
 - Semi-Empirical Model Data:
   - [Inventory](https://code.usgs.gov/ghsc/esi/esi-utils-pager/-/raw/main/src/esi_utils_pager/data/semi_inventory.xlsx?ref_type=heads)
   - [Workforce](https://code.usgs.gov/ghsc/esi/esi-utils-pager/-/raw/main/src/esi_utils_pager/data/semi_workforce.xlsx?ref_type=heads)
   - [Collapse](https://code.usgs.gov/ghsc/esi/esi-utils-pager/-/raw/main/src/esi_utils_pager/data/semi_collapse_mmi.xlsx?ref_type=heads)
   - [Casualty](https://code.usgs.gov/ghsc/esi/esi-utils-pager/-/raw/main/src/esi_utils_pager/data/semi_casualty.xlsx?ref_type=heads)


To run pagerlite on the event `us10003re5` with custom empirical data files:

`pagerlite -f ~/custom_fatality.xlsx -e ~/custom_economic.xlsx event us10003re5`

To run the semi-empirical model with custom data files, assuming those files are all in the same folder, 
and all named as they are in the repository (semi_inventory.xlsx, semi_workforce.xlsx, 
semi_collapse_mmi.xlsx, semi_casualty.xlsx):

`pagerlite -s --semi-folder ~/test_semi/test1 event us10003re5`

Any custom input files can be used in either `event` or `batch` modes.

See the help for more options (depth and magnitude ranges) on restricting processing of ShakeMap
grids.

### Running background processes

Running pagerlite over a large number of events can take many minutes or hours
depending on the number of events being run.  If you have access to a Linux system, you can
run a batch process in the background and also ensure that the process will continue when you
disconnect from the remote Linux system. The way to do this is to combine the `nohup` command
(short for "no hang up") and the ampersand "&" character at the end of the command. 
Below is an example running on all events inside an Afghanistan bounding box:

`nohup pagerlite  -o ~/afghanistan_text.csv -v batch -f /data/shakedata/ -b 60.271 73.367 29.581 38.795 > ~/afghanistan_log.txt&`

Executing this command with the "&" at the end will start it running in the background. When it is done, you
can run `tail afghanistan_log.txt` until you see a line that looks like this:

`Saving 1258 rows to afghanistan_text.csv`

If you want to watch the progress of pagerlite, you can run:

`tail -f afghanistan_log.txt`

and see output streaming by as each event is processed.


# Library Usage

Usage of the relevant code modules is detailed in the Jupyter notebooks, most notably in the 
[Earthquake Losses notebook](https://code.usgs.gov/ghsc/esi/esi-utils-pager/-/blob/main/notebooks/EarthquakeLosses.ipynb)


