import logging.config
import yaml
import os
from importlib import resources
from typing import Optional, Dict, Any

def get_default_logging_config() -> Dict[str, Any]:
    """
    Load the default logging configuration from the bundled YAML file.
    
    Returns:
        Dict[str, Any]: The logging configuration dictionary loaded from the 
                        bundled logging_config.yaml file.
                        
    Raises:
        FileNotFoundError: If the bundled logging_config.yaml file is not found.
        yaml.YAMLError: If the YAML content is invalid or cannot be parsed.
    """
    with resources.files("default_logging").joinpath("logging_config.yaml").open("r") as f:
        config = yaml.safe_load(f)
    return config

def configure_logging(config_path: Optional[str] = None) -> None:
    """
    Configure logging from a YAML file with automatic directory creation.

    This function configures the Python logging system using either a custom YAML 
    configuration file or the default bundled configuration. It automatically creates
    directories for file handlers (RotatingFileHandler and FileHandler) to ensure log
    files can be written successfully.

    Args:
        config_path (Optional[str]): Path to a custom YAML configuration file. 
                                   If None, uses the default bundled configuration.

    Raises:
        FileNotFoundError: If the specified config_path file does not exist.
        yaml.YAMLError: If the YAML configuration content is invalid or cannot be parsed.
        OSError: If directory creation fails for file handler log paths.
        Exception: For other errors during logging configuration setup.
    """
    if config_path:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = get_default_logging_config()

    if 'handlers' in config:
        for handler_name, handler_config in config['handlers'].items():
            if handler_config.get('class') == 'logging.handlers.RotatingFileHandler' or \
            handler_config.get('class') == 'logging.FileHandler':
                filename = handler_config.get('filename')
                if filename:
                    os.makedirs(os.path.dirname(filename), exist_ok=True)

    logging.config.dictConfig(config)
