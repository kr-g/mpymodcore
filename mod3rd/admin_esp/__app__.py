
from mod3rd.admin_esp.wlan import router

from modext.auto_config.ext_spec import Plugin


class WLAN_chooser(Plugin):

    def __init__(self):
        super().__init__()
        self.caption = "WLAN"
        self.path_spec = "mod3rd.admin_esp"
        self.generators = [router]
        self.url_caption_tuple_list = [( router.root + "/wlan",None)]


app_ext = WLAN_chooser()

