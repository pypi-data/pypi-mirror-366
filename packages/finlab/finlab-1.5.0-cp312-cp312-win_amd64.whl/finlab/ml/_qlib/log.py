import logging
from typing import Dict, Any, Text, Optional
from logging import config as logging_config

logger = logging.getLogger(__name__)

def get_module_logger(*args, **kwargs):
    """
    Get a logger for a specific module.

    Args:
        module_name (str): The name of the module for which to get the logger.

    Returns:
        logging.Logger: A logger instance for the specified module.
    """
    return logger



class _QLibLoggerManager:
    def __init__(self):
        self._loggers = {}

    def setLevel(self, level):
        for logger in self._loggers.values():
            logger.setLevel(level)

    def __call__(self, module_name, level: Optional[int] = None):
        """
        Get a logger for a specific module.

        :param module_name: str
            Logic module name.
        :param level: int
        :return: Logger
            Logger object.
        """
        return logger


get_module_logger = _QLibLoggerManager()

def set_log_with_config(log_config: Dict[Text, Any]):
    """set log with config

    :param log_config:
    :return:
    """
    logging_config.dictConfig(log_config)
