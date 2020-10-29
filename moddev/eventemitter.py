"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import time

from modcore import modc, Module, LifeCycle


class EventEmitter(Module):
    def on_add(self):
        self.check_lifecycle = True

    def init(self):
        self.event = None

    def conf(self, config=None):
        if config != None:

            self.event = config.get(self.id + ":event", None)
            self.info("event:", self.event)

    def split_event_data(self, eventdata):

        if type(eventdata) == type(list()):
            for data in eventdata:
                yield from self.split_event_data(data)
            return

        pos = eventdata.find(":")
        if pos < 0:
            yield eventdata, None
        else:
            yield eventdata[:pos], eventdata[pos + 1 :]

    def __loop__(self, config=None, event=None, data=None):

        if self.check_lifecycle and self.current_level() != LifeCycle.RUNNING:
            return

        if self.__loop2__(config, event, data) == False:
            return

        if self.__emit__(config) == True:
            if self.event != None:
                for event, data in self.split_event_data(self.event):
                    self.fire_event(event, data)

    # overload this if required, return False to return without call emit
    def __loop2__(self, config=None, event=None, data=None):
        pass

    # overload this and return True for emitting the event
    def __emit__(self, config=None):
        pass
