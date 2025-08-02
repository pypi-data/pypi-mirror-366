# stdlib imports
import os.path
import pathlib
import shutil

# third party imports
from ruamel.yaml import YAML


def read_config():
    """Read in configuration parameters from config .py file.

    returns:
      Dictionary containing configuration parameters.
    raises:
      Exception if config file does not exist.
    """
    # get config file name, make sure it exists
    configfilename = get_config_file()
    if configfilename is None:
        raise Exception("Config file could not be found at %s." % configfilename)
    yaml = YAML()
    config = yaml.load(open(configfilename, "rt"))
    return config


def read_mail_config():
    """Read in configuration parameters from config .py file.

    returns:
      Dictionary containing configuration parameters.
    raises:
      Exception if config file does not exist.
    """
    # get config file name, make sure it exists
    configfilename = get_mail_config_file()
    if configfilename is None:
        raise Exception("Config file could not be found at %s." % configfilename)

    config = yaml.safe_load(open(configfilename, "rt"))
    return config


def write_config(config, make_backup=True):
    """Write out config parameters.

    :param config:
      Dictionary with configuration parameters.
    :param make_backup:
      Boolean indicating whether a backup of the current config file
      should be made before writing new one.
    """
    # get config file name, make sure it exists
    configfilename = get_config_file(ignore_missing=True)
    if not configfilename.exists():
        raise Exception("Config file could not be found at %s." % configfilename)
    backup_name = pathlib.Path.home() / ".losspager" / "config.yml.bak"
    shutil.copyfile(configfilename, backup_name)
    with open(configfilename, "wt") as f:
        f.write(yaml.dump(config))


def get_mail_config_file():
    """Find and return config file name, if exists.  None returned if file does not exist.

    :returns:
      config file name, or None if config file does not exist.
    """
    configfilename = os.path.join(
        os.path.expanduser("~"), ".losspager", "mailconfig.yml"
    )
    if not os.path.isfile(configfilename):
        return None
    return configfilename


def get_config_file(ignore_missing=False):
    """Find and return config file name, if exists.  None returned if file does not exist.

    :returns:
      config file name, or None if config file does not exist.
    """
    configfilename = pathlib.Path.home() / ".losspager" / "config.yml"
    if not configfilename.exists() and not ignore_missing:
        return None
    return configfilename
