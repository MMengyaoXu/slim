import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def add_url_log(url, method):
    logger.info("* Mounted url: {url} [{method}]".format(url=url, method=method))
