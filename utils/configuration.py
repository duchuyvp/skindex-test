import os
import pathlib
import logging
from typing import Any
from utils import creational, io
import yaml

logger = logging.getLogger(__file__)


DEFAULT_PATH = "/etc/config"


def get_config_path():
    path = os.environ.get("CONFIG_PATH", DEFAULT_PATH)

    return path


@creational.singleton
class Configuration(dict[str, Any]):
    """
    A custom dictionary class for storing configuration settings.

    This class extends the built-in dict class to provide additional functionality for managing
    configuration settings.

    Example usage:
    config = Configuration()
    config['debug'] = True
    config['log_level'] = 'INFO'
    """


config: Configuration = Configuration()


def load_config(config_path: str = ".configs") -> dict[str, Any]:
    """Load configuration files from the specified path and return a dictionary with the
    configuration settings.

    Args:
        config_path (str): The path where the configuration files are located. Defaults to
        ".configs".

    Returns:
        dict[str, Any]: A dictionary containing the configuration settings loaded from the files.
    """
    config_path = config_path or get_config_path()
    global config
    config = Configuration()

    for root, _, files in os.walk(config_path):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                filepath = os.path.join(root, file)
                logger.debug(f"Loading configuration file: {filepath}")

                data = io.yaml_to_dict(filepath)
                config |= data
    logger.debug(f"Load config from: {config}")
    return config


def get_config() -> dict[str, Any]:
    """Get configuration settings from a file."""
    global config
    config = config or load_config()
    return config
