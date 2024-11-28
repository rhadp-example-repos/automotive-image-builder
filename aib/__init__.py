import logging
import os
import sys

from dataclasses import dataclass
from functools import cached_property
from typing import Any


@dataclass
class AIBParameters:
    args: Any
    base_dir: str

    @cached_property
    def include_dirs(self):
        return [self.base_dir] + self.args.include

    @cached_property
    def build_dir(self):
        return (
            os.path.expanduser(self.args.build_dir)
            if self.args.build_dir
            else None
        )

    def func(self, tmpdir, runner):
        return self.args.func(self, tmpdir, runner)

    def __getattr__(self, name: str) -> Any:
        return vars(self.args).get(name)


class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = logging.Formatter("%(message)s")
        if record.levelno >= logging.WARNING:
            log_fmt = logging.Formatter("%(levelname)s: %(message)s")
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
