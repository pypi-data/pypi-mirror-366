import logging
import logging.config
import os
import pprint
from datetime import datetime




def application(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.APPLICATION):
        self._log(logging.APPLICATION, message, args, **kwargs)

def add_applicaiton_level():
    ## Add a custom logging level for application-specific logs
    APPLICATION = 51
    logging.APPLICATION = APPLICATION
    logging.addLevelName(APPLICATION, "APPLICATION")
    logging.Logger.application = application


def initialize_logging(file_path: str, disable_log: bool = False, debug: bool = False) -> None:

    """Add the custom application logging level."""
    add_applicaiton_level()
    ## Logging Configiration
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": logging.DEBUG,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "propagate": True,
            },
        },
    }

    #log = logging.getLogger("awsome_list")

    if debug:
        """Set the logging level to DEBUG if debug is True."""
        log_config["handlers"]["console"]["level"] = logging.DEBUG
        log_config["loggers"][""]["level"] = logging.DEBUG
    else:
        """Set the logging level to INFO if debug is False."""
        log_config["handlers"]["console"]["level"] = logging.INFO
        log_config["loggers"][""]["level"] = logging.INFO
        
    if not disable_log:

        """Initialize logging configuration."""
        if not os.path.exists(file_path):
            os.makedirs(file_path)
    
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = f"{file_path}/application-{timestamp}.log"
        
        application_handler =  {
            "application": {
                "class": "logging.FileHandler",
                "level": logging.APPLICATION,
                "formatter": "default",
                "filename": log_file,
            }
        }

        log_config["handlers"].update(application_handler)
        log_config["loggers"][""]["handlers"].append("application")
    
    logging.config.dictConfig(log_config)