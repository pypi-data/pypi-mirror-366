import logging

def setup_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:  # Prevent duplicate handlers
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '[%(levelname)s] %(message)s'
        ))
        logger.addHandler(console_handler)

    return logger
