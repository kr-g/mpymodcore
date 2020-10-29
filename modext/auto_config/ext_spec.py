class Plugin(object):
    def __init__(self):
        self.caption = None
        self.path_spec = None
        self.global_var = "_"
        self.modules = []
        self.generators = []
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
            + "spec :"
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
