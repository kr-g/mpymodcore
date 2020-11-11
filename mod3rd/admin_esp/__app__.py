from mod3rd.admin_esp.wlan import router as wlan_router
from mod3rd.admin_esp.softap import router as softap_router

from modext.auto_config.ext_spec import Plugin


class WLAN_chooser(Plugin):
    def __init__(self):
        super().__init__()
        self.caption = "WLAN"
        ## todo remove
        self.path_spec = "mod3rd.admin_esp"
        self.generators = [wlan_router]
        self.url_caption_tuple_list = [(wlan_router.root + "/wlan", None)]


class SoftAp_config(Plugin):
    def __init__(self):
        super().__init__()
        self.caption = "SoftAP"
        ## todo remove
        self.path_spec = "mod3rd.admin_esp"
        self.generators = [softap_router]
        self.url_caption_tuple_list = [(softap_router.root + "/softap", None)]


app_ext = [WLAN_chooser(), SoftAp_config()]
