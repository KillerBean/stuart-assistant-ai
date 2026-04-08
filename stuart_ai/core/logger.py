import logging
import coloredlogs

def setup_logger(name: str = "stuart_ai", level: str = "INFO"):
    """Logger configuration module for Stuart AI."""
    log = logging.getLogger(name)
    coloredlogs.install(level=level, logger=log, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return log

logger = setup_logger()
