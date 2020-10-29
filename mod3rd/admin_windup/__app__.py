from mod3rd.admin_windup.editor import static_files
from mod3rd.admin_windup.file_api import router
from mod3rd.admin_windup.content import router as content_router

from modext.auto_config.ext_spec import Plugin


class FileUtils(Plugin):
    def __init__(self):
        super().__init__()
        self.caption = "File Utils"
        self.path_spec = "mod3rd.admin_windup"
        self.generators = [static_files, router, content_router]
        self.url_caption_tuple_list = [
            (static_files.root, None),
            (router.root + "/browse", None),
            (content_router.root + "/generators", None),
        ]


app_ext = FileUtils()
