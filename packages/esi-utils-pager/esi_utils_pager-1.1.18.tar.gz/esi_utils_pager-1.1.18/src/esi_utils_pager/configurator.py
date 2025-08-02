# stdlib imports
import logging
import pathlib
import re
import zipfile

# third party imports
from ruamel.yaml import YAML

from esi_utils_pager.config import get_config_file

# dictionary with model_data key and filename regex to search for
model_data_sections = {
    "city_file": "cities",
    "timezones_file": "combined",
    "country_grid": "isogrid",
    "ocean_vectors": "ne_10m_ocean",
    "border_vectors": "10m_admin_0_countries",
    "ocean_grid": "oceangrid",
    "counties": "tl_2010_us_county10",
    "states": "tl_2010_us_state10",
    "tracts": "us_tracts",
    "urban_rural_grid": "glurextents",
    "population_data": "lspop",
}

meta_extensions = [".hdr", ".prj", ".dbf", ".shx"]
main_extensions = [".shp", ".bil", ".csv", ".flt"]


class Configurator:
    def __init__(self, pager_dir, model_zipfile, pop_zipfile=None):
        self.pager_dir = pathlib.Path(pager_dir)
        self.model_zipfile = model_zipfile
        self.pop_zipfile = pop_zipfile
        if not self.pager_dir.exists():
            self.pager_dir.mkdir(parents=True)
        self.data_dir = self.pager_dir / "data"

    def configure(self):
        """Get configuration dictionary and list of files to extract from zipfile(s)."""
        extract_files = {self.model_zipfile: [], self.pop_zipfile: []}

        config_dict = {"model_data": {}}
        logging.info(f"Inspecting files in {self.model_zipfile}")
        with zipfile.ZipFile(self.model_zipfile, "r") as myzip:
            datafiles = myzip.namelist()
            for key, vregex in model_data_sections.items():
                for datafile in datafiles:
                    dfilename = self.data_dir / datafile
                    parent = dfilename.parent
                    if not parent.exists():
                        parent.mkdir(parents=True)
                    if re.search(vregex, datafile) is not None:
                        if key != "population_data":
                            if dfilename.suffix in main_extensions:
                                config_dict["model_data"][key] = str(dfilename)
                            extract_path = dfilename.parent
                        else:
                            if dfilename.suffix in main_extensions:
                                year = int(re.search("[0-9]+", dfilename.name).group())
                                config_dict["model_data"]["population_data"] = [
                                    {
                                        "population_grid": str(dfilename),
                                        "population_year": year,
                                    }
                                ]
                            extract_path = dfilename.parent.parent
                        extract_files[self.model_zipfile].append(
                            (datafile, extract_path)
                        )
        if self.pop_zipfile is not None:
            with zipfile.ZipFile(self.pop_zipfile, "r") as myzip:
                datafiles = myzip.namelist()
                for datafile in datafiles:
                    dfilename = self.data_dir / "population" / datafile
                    if dfilename.suffix in main_extensions:
                        year = int(re.search("[0-9]+", dfilename.name).group())
                        config_dict["model_data"]["population_data"].append(
                            {
                                "population_grid": str(dfilename),
                                "population_year": year,
                            }
                        )
                    extract_path = dfilename.parent

                    extract_files[self.pop_zipfile].append((datafile, extract_path))

        return (config_dict, extract_files)

    def write(self, config_dict, extract_files):
        config_file = get_config_file(ignore_missing=True)
        yaml = YAML()
        with open(config_file, "wt") as fobj:
            yaml.dump(config_dict, fobj)
        with zipfile.ZipFile(self.model_zipfile, "r") as myzip:
            for zip_path, extract_path in extract_files[self.model_zipfile]:
                logging.info(f"Extracting file {zip_path}...")
                myzip.extract(zip_path, extract_path)
        if self.pop_zipfile is None:
            return
        with zipfile.ZipFile(self.pop_zipfile, "r") as myzip:
            for zip_path, extract_path in extract_files[self.pop_zipfile]:
                logging.info(f"Extracting file {zip_path}...")
                myzip.extract(zip_path, extract_path)
