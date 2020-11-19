"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import sys
import time

CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

#

LOGLEVEL = "LOGLEVEL"
LOGCFG = "etc/log.cfg.txt"

#

_logstr = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
    NOTSET: "NOTSET",
}


def _timefunc():
    return time.localtime(time.time())


class LogSupport(object):

    timefunc = _timefunc

    stdout = sys.stdout
    stderr = sys.stderr  ##todo write level >= WARN also on stderr??

    level = INFO
    showdate = True
    showtime = True

    def __init__(self, level=None):
        self.log_level(level)
        self.logname = self.__class__.__name__
        self.showtime = LogSupport.showtime

    def log_level(self, level=None):
        self._log_level = level  # if level != None else LogSupport.level

    def get_level(self):
        if self._log_level == None:
            return LogSupport.level
        return self._log_level

    @staticmethod
    def global_level(level):
        LogSupport.level = level

    def _timestr(self):
        tm = LogSupport.timefunc()[0:6]
        ds = "%04d%02d%02d" % tm[0:3] if LogSupport.showdate else ""
        ls = "-" if LogSupport.showdate else ""
        ts = "%02d%02d%02d" % tm[3:6]
        return ds + ls + ts

    def _loglevel(self, level):
        cur = self.get_level()
        return level >= cur and cur > 0

    def _log(self, level, *args):
        if len(args) == 0:
            return self._loglevel(level)
        if self._loglevel(level):
            self._log2(level, _logstr[level], *args)

    def _log2(self, level, infostr, *args):
        if self.showtime:
            self._print_fd(self._timestr(), end=":")
        if infostr:
            self._print_fd(infostr, end=":")
        self._print_fd(self.logname, end=":")
        if "id" in self.__dict__:
            self._print_fd(self.id, end=":")
        self._print_fd(*args)

    def _print_fd(self, *args, end="\n", file=None):
        if file == None:
            file = LogSupport.stdout
        print(*args, end=end, file=file)

    def debug(self, *args):
        return self._log(DEBUG, *args)

    def info(self, *args):
        return self._log(INFO, *args)

    def warn(self, *args):
        return self._log(WARNING, *args)

    def error(self, *args):
        return self._log(ERROR, *args)

    def critical(self, *args):
        return self._log(CRITICAL, *args)

    def excep(self, ex, *args):
        self.critical(*args)
        sys.print_exception(ex)  ##todo print with  _print_fd


def set_log_level(level):
    logger.info("setting log level", _logstr[level], "=", level)
    LogSupport.global_level(level)


def set_log_level_from_config(cfg):
    info_str = _logstr[INFO]
    levelstr = cfg.get(LOGLEVEL, info_str)
    r = list(filter(lambda x: x[1] == levelstr, _logstr.items()))
    if len(r) != 1:
        raise Exception("unknown log level", levelstr)
    level = r[0][0]
    set_log_level(level)


def read_level():

    try:
        with open(LOGCFG) as f:
            lines = f.readlines()
    except:
        return

    lines = list(map(lambda x: x.strip(), lines))
    lines = list(filter(lambda x: len(x) > 0, lines))
    lines = list(filter(lambda x: x[0] != "#", lines))

    if len(lines) == 0:
        return

    level = lines[0]
    set_log_level_from_config({LOGLEVEL: level})


def write_level():
    with open(LOGCFG, "w") as f:
        f.write(_logstr[LogSupport.level])
        f.write("\n")


read_level()

logger = LogSupport()
logger.logname = "main"
