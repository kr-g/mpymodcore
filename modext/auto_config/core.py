import os

from modcore.log import LogSupport


def _os_stat(path):
    try:
        return os.stat(path)
    except:
        return None


class Loader(LogSupport):
    def __init__(self):
        super().__init__()
        self.imports = []
        self.plugins = []

    def _get_dir_filter(self, path):
        paths = map(lambda x: path + "/" + x, os.listdir(path))
        fstat = map(lambda x: (x, _os_stat(x)), paths)
        dirs = filter(lambda x: x[1][0] & 16384 > 0, fstat)
        return dirs

    def find(self, path):
        self.info("search apps in", path)
        dirs = self._get_dir_filter(path)
        apps = filter(lambda x: _os_stat(x[0] + "/__app__.py"), dirs)
        app_paths = list(map(lambda x: x[0], apps))
        self.info("found apps", app_paths, "in", path)
        return app_paths

    def find_3rd(self, path="mod3rd"):
        return self.find(path)

    def find_apps(self, path="modapp"):
        return self.find(path)

    def do_import(self, name_spec, _globals=None, name_or_alias=None):
        if name_or_alias == None:
            try:
                name_or_alias = name_spec[name_spec.rfind("/") + 1 :]
            except:
                name_or_alias = name_spec
        path = name_spec.replace("/", ".") + ".__app__"
        self.info("importing", (path, name_spec, name_or_alias))
        imp = __import__(path)
        _mod = imp
        nav = path.split(".")
        nav.pop(0)
        for s in nav:
            _mod = getattr(_mod, s)
        if _globals != None:
            _globals[name_or_alias] = _mod

        self.imports.append(imp)
        self.plugins.append(_mod)
        return _mod


_core_loader = None


def get_core_loader():
    global _core_loader
    if _core_loader == None:
        _core_loader = Loader()
    return _core_loader
