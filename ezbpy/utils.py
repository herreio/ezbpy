import logging


def get_logger(name, loglevel=logging.WARNING):
    logger = logging.getLogger(name)
    if not logger.handlers:
        stream = logging.StreamHandler()
        stream.setLevel(loglevel)
        stream.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(stream)
    if logger.level != loglevel:
        logger.setLevel(loglevel)
    return logger
