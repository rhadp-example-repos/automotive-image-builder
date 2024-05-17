import logging
import sys

class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = logging.Formatter('%(message)s')
        if record.levelno >= logging.WARNING:
            log_fmt = logging.Formatter('%(levelname)s: %(message)s')
        return log_fmt.format(record)

class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in (logging.DEBUG, logging.INFO)


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# create info and debug handler
h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.DEBUG)
h1.setFormatter(CustomFormatter())
h1.addFilter(InfoFilter())
# create handler for the rest
h2 = logging.StreamHandler()
h2.setLevel(logging.WARNING)
h2.setFormatter(CustomFormatter())
# add the handlers to the logger
log.addHandler(h1)
log.addHandler(h2)

def exit_error(s, *args):
    log.error(s, *args)
    sys.exit(1)
