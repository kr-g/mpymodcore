from modcore.log import logger
from modext.windup import Router, StaticFiles

from modext.auto_config.core import get_core_loader
from modext.auto_config.ext_spec import Plugin, PluginUrl

from modext.config import ReprDict

static_files = StaticFiles(["/mod3rd/main_dashboard/www_main"], root="/main")

rooter = Router(root="/rest/main")


@rooter.get("/plugins")
def get_plugins(req, args):

    plugins = _get_all_plugins()

    req.send_json(ReprDict().reprlist(plugins))


def _get_all_plugins():
    cfg_loader = get_core_loader()

    plugins = []

    for plugin in cfg_loader.plugins:
        try:
            ext = plugin.app_ext
            if ext == None:
                continue
            if type(ext) != list:
                ext = [ext]
            plugins.extend(ext)
        except Exception as ex:
            logger.excep(ex, "plugins")

    print(plugins)

    return plugins


class MainDashBoard(Plugin):
    def __init__(self):
        super().__init__()
        self.caption = "Main"
        self.path_spec = ""
        self.generators = [static_files, rooter]
        self.url_caption_tuple_list = [
            PluginUrl(static_files.root + "/#", "mpy-modecore dashboard"),
        ]


app_ext = MainDashBoard()
