"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from .lifecycle import LifeCycle
from .events import EventData, EventQueue, EVENTDATA_DEFAULT
from .log import LogSupport


class Module(LifeCycle, LogSupport):
    def __init__(self, id=None, config=None, max_events=5):
        LifeCycle.__init__(self)
        LogSupport.__init__(self)
        self._controller = None
        if id == None:
            id = self.__class__.__name__.lower()
        self.id = id
        self.max_events = max_events
        #        self.conf( config )
        self._init_internal()

    def conf(self, config):
        self._config = config

    def _init_internal(self):
        self._events = EventQueue(max_events=self.max_events)

    def __repr__(self):
        return "id: " + self.id + " events: " + str(len(self._events))

    def watching_events(self):
        return None

    def _add_event(self, event):
        self._events.add(event)
        self.info("add", event)

    def _pop_event(self):
        return self._events.pop()

    def fire_event(self, event, data=None):
        self._controller.fire_event(event, data, src=self)

    def is_event(self, event, name):
        return event.name.lower() == name.lower()

    def event_value(self, event, key=EVENTDATA_DEFAULT):
        return event.get_data(key)

    def event_data_value(self, data, key=EVENTDATA_DEFAULT):
        return EventData.get_dict_val(data, key)

    def run(self, config=None):
        ev = self._pop_event()
        if ev != None:
            res = self.loop(config, ev)
        else:
            res = self.loop(config)
        return res

    def loop(self, config=None, event=None):
        self.debug(self.id, event)
        if event != None:
            return self.__loop__(config, event.name, event.data)
        return self.__loop__(config)

    def __loop__(self, config=None, event=None, data=None):
        if self.current_level() != LifeCycle.RUNNING:
            return
        return self.__loop_run__(config, event, data)

    def __loop_run__(self, config=None, event=None, data=None):
        if event == None:
            return
        return self.__loop_event__(config, event, data)

    def __loop_event__(self, config=None, event=None, data=None):
        pass
