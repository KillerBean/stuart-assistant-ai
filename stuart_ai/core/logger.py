import logging
import coloredlogs

def setup_logger(name: str = "stuart_ai", level: str = "INFO"):
    logger = logging.getLogger(name)
    coloredlogs.install(level=level, logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logger

logger = setup_logger()
