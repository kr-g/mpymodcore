from mod3rd.admin_user.login import router

from modext.auto_config.ext_spec import Plugin


class LoginLogout(Plugin):
    def __init__(self):
        super().__init__()
        self.caption = "Login/ Logout"
        self.path_spec = "mod3rd.admin_user"
        self.generators = [router]
        self.url_caption_tuple_list = [
            (router.root + "/login", None),
            (router.root + "/logout", None),
        ]


app_ext = LoginLogout()
