from logging import DEBUG, basicConfig, getLogger

logger = getLogger(" ")
basicConfig(
    filename="log.log",
    encoding="utf-8",
    level=DEBUG,
    filemode="w",
    format="%(levelname)s: %(message)s",
)
logger.setLevel(9)


def debug(*args):
    logger.debug(" ".join([str(s) for s in args]))
