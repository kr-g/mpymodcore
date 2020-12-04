from modcore.log import LogSupport
from modext.config import ReprDict


class PluginUrl(ReprDict):
    def __init__(self, url, caption, ext_url=True):
        self.url = url
        if caption == None:
            caption = url
        self.caption = caption
        self.ext_url = ext_url

    def __repr__(self):
        return {"url": self.url, "caption": self.caption, "ext_url": self.ext_url}


class Plugin(ReprDict, LogSupport):
    def __init__(self):
        LogSupport.__init__(self)
        # the name of the plugin
        self.caption = None
        # path_spec is set by the loader
        self.path_spec = None
        # not used as of now
        self.global_var = "_"
        # not used as of now
        self.modules = []
        # the generators for windup
        self.generators = []
        # a list of url entry-points provided by the plugin
        self.url_caption_tuple_list = []
        self.type = "user"
        self.licenses_url = []

    def check(self):
        self.info("check", self.__class__)
        self.url_caption_tuple_list = list(
            map(lambda x: self._url_type(x), self.url_caption_tuple_list)
        )

    def _url_type(self, obj):
        if type(obj) == tuple:
            return PluginUrl(*obj)
        return obj

    def __repr__(self):

        return {
            "caption": self.caption,
            "path_spec": self.path_spec,
            "var": self.global_var,
            "modules": self.modules,
            # "generators": self.generators,
            "url_list": self.reprlist(self.url_caption_tuple_list),
            "type": self.type,
            "licenses": self.licenses_url,
        }
