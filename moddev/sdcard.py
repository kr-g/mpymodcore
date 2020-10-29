"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import uos
import machine

import time
import ntptime

from modcore import Module
from modcore.log import LogSupport

SD_SLOT = 3
SD_PATH = "/sd"


class SDCard(Module):
    def on_add(self):
        self.slot = SD_SLOT
        self.path = SD_PATH
        self.card = None
        self.info("add", "slot", self.slot, "path", self.path)

    def conf(self, config=None):
        if config != None:
            self.slot = config.get("SD_SLOT", SD_SLOT)
            self.path = config.get("SD_PATH", SD_PATH)
        self.info("config", "slot", self.slot, "path", self.path)

    def mount(self):
        if self.card != None:
            raise Exception("already in use")
        self.card = machine.SDCard(slot=self.slot)
        uos.mount(self.card, self.path)
        self.info("mount")

    def umount(self):
        uos.umount(self.path)
        self.card.deinit()
        self.card = None
        self.info("umount")
