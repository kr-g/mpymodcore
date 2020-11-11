class Plugin(object):
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
        return (
            self.__class__.__name__
            + "( "
            + "caption :"
            + self.caption
            + ", "
            + "path spec :"
            + self.path_spec
            + ", "
            + "var :"
            + self.global_var
            + ", "
            + "modules :"
            + str(self.modules)
            + ", "
            + "generators :"
            + str(self.generators)
            + ", "
            + "url :"
            + str(self.url_caption_tuple_list)
            + ", "
            + "type :"
            + self.type
            + ", "
            + "licenses :"
            + str(self.licenses_url)
            + ", "
            + " )"
        )
