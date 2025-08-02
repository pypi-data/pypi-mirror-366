## main

## 1.1.18 / 2024-05-08
 - Removing numpy pin to v1.x.

## 1.1.17 / 2024-05-08
 - Now installing application data files under a 'data' directory.

## 1.1.16 / 2024-05-08
 - Added a user configuration tool.

## 1.1.14 / 2024-05-08
 - Added documentation to README
 - cleaned up bug relating to single event runs.

## 1.1.13 / 2024-05-07
 - Refactored command line program pagerlite to have two subcommands, `event` and `batch`.
 - Skipping grids discovered in shakemap "backup" directories.

## 1.1.12 / 2024-04-30
 - Now allowing users to specify semi-empirical model from external folder;
 - allowing users to specify events to process using time, space, and magnitude ranges.

## 1.1.11 / 2024-04-19
 - Modifying expected losses of 0 to 0.1 to ensure desired probability when basically no exposure

## 1.0.10 / 2024-04-17
 - Changed default model file format to Excel
 - Added command line options to pagerlite to allow users to pass in custom Excel model files
 - Fixed notebooks
## 1.0.9 / 2023-02-09
 - Added two command line options for processing single events, updated readme.

## 1.0.8 / 2023-10-10
 - Fixed bug in code packaging.

## 1.0.7 / 2023-10-10
 - Fixed bug in handling of semi-empirical model results.


## 1.0.6 / 2023-10-10
 - Initial checkin with this changelog.
 - Adding in CI workflow for testing, deployment, etc.
 - Fixing strec configuration issues
 - Fixing existing dependency issues
 - Using dynamic versioning with setuptools_scm