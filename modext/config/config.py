import os
import json

from .namespace import Namespace


def ensure_path(fnam):

    dirs = fnam.split("/")
    dirs.pop(-1)

    complete = ""
    for dir in dirs:
        if len(dir) == 0:
            continue
        complete += "/" + dir
        try:
            os.mkdir(complete)
        except Exception as ex:
            pass

    # this raises exception if path was not created
    dir = "/".join(dirs)
    os.stat(dir)


## todo, refactor Namespace
class Config(Namespace):
    def __init__(self, fnam):

        # Namespace.__init__(self)
        self._fnam = fnam

    def load(self, fnam=None):

        if fnam == None:
            fnam = self._fnam

        with open(fnam, "r") as f:
            cont = f.read()

        cfg = json.loads(cont)
        self.update(cfg)

    def save(self):
        ensure_path(self._fnam)
        with open(self._fnam, "w") as f:
            f.write(json.dumps(dict(self)))
