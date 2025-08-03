import yaml
from dotenv import load_dotenv
import os
from os import getenv as secret  # noqa: F401

from common_utils.logger import create_logger

logged_root_dirs = []


def get_root_dir(dunder_file: str) -> str | None:
    """ Returns the root directory of the project, called using __file__.

    Uses either 'src', 'venv' or DOCKER_WORKDIR env-var to determine the root directory.
    """
    root_dir = None
    try:
        if "venv" in os.path.abspath(dunder_file):
            root_dir = os.path.abspath(dunder_file).split("venv")[0][:-1]
        elif "src" in os.path.abspath(dunder_file):
            root_dir = os.path.abspath(dunder_file).split("src")[0][:-1]
        elif os.getenv('DOCKER_WORKDIR'):
            root_dir = os.getenv('DOCKER_WORKDIR')
        else:
            if dunder_file != __file__:
                logger.debug(f"Cannot get root dir, as {dunder_file} not in src or venv dir")
            else:
                logger.debug(f"Cannot get ROOT_DIR, as {dunder_file} not in src or venv dir")
    except Exception:
        logger.debug(f"Could not get root dir from {dunder_file}")
    finally:
        # remove /. end of root_dir
        if root_dir and root_dir[-2:] == '\\.':
            root_dir = root_dir[:-2]
        elif root_dir and root_dir[-1] == '\\':
            root_dir = root_dir[:-1]
        if os.getenv('DONT_PRINT_ROOT_DIR'):
            return root_dir
        logger.debug(f"{'ROOT_DIR' if dunder_file == __file__ else 'get_root_dir'}: {root_dir}"
                     f"  -  {os.listdir(root_dir) if root_dir not in logged_root_dirs else ''}")
        logged_root_dirs.append(root_dir)
        return root_dir


def load_config_yaml(file_path: str) -> dict | None:
    """ Loads a yaml file from the given path and returns the data as a dict. """
    try:
        _stream = open(file_path, "r", encoding="utf-8")
        return yaml.safe_load(_stream)
    except Exception as e:
        logger.debug(f"Could not load config from {file_path}")
        return None


def config_entry(key):
    return CONFIG[key]


# Load default config from config.yml using ROOT_DIR
logger = create_logger("Config Helper")
load_dotenv()
ROOT_DIR = get_root_dir(__file__)
if ROOT_DIR:
    CONFIG = load_config_yaml(f"{ROOT_DIR}/config.yml")
else:
    logger.debug("ROOT_DIR is None, trying to load CONFIG from config.yml in current dir")
    CONFIG = load_config_yaml("config.yml")
