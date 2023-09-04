import logging
import colorlog

log = logging.getLogger("MondayAPI - AI")
log.setLevel(logging.DEBUG)

# StreamHandler for console with color
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
ch.setFormatter(color_formatter)

# FileHandler for writing logs to a file
fh = logging.FileHandler("app.log")
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

log.addHandler(ch)
log.addHandler(fh)