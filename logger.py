import logging

logname = 'logFile.txt'

logging.basicConfig(
    filename=logname,
    filemode='w',
    format="",
    style="{",
    level=logging.INFO,
)


def log(information):
    logging.info(information)
