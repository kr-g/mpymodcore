from modext.config import ReprDict


class Plugin(ReprDict):
    def __init__(self):
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

    def __repr__(self):
        return {
            "caption": self.caption,
            "path_spec": self.path_spec,
            "var": self.global_var,
            "modules": self.modules,
            "generators": self.generators,
            "url": self.url_caption_tuple_list,
            "type": self.type,
            "licenses": self.licenses_url,
        }
