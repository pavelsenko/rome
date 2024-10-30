import logging

def get_logger():
    """Creates and configures a logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s')

    # Add formatter to console handler
    ch.setFormatter(formatter)

    # Add console handler to logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger
