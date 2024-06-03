import os
import subprocess

from . import log


class OSTree:
    def __init__(self, path):
        self.path = path
        if not os.path.isdir(path):
            self.repo_init()

    def repo_init(self):
        log.debug("Initializing repo %s", self.path)
        subprocess.run(["ostree", "init", "--repo", self.path, "--mode", "archive"],
                    check=True)

    def refs(self):
        r = subprocess.run(["ostree", "refs", "--repo", self.path],
                        capture_output=True,
                        check=True)
        out = r.stdout.decode("utf-8").rstrip()
        if out:
            return out.split("\n")
        return []

    def rev_parse(self, ref):
        r = subprocess.run(["ostree", "rev-parse", "--repo", self.path, ref],
                        capture_output=True,
                        check=True)
        return r.stdout.decode("utf-8").rstrip()
