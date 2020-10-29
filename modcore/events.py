"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

try:
    from ucollections import deque

    print("modcore running on micropython")
except:
    from collections import deque


EVENTDATA_DEFAULT = "default"


class EventData:

    _cnt_events = 0

    @staticmethod
    def _get_id():
        EventData._cnt_events += 1
        return EventData._cnt_events

    def __init__(self, event, data={}, sender=None):
        self.id = EventData._get_id()
        self.sender = sender
        self.name = event
        self.set_data(data)

    def set_data(self, data=None):
        if data == None:
            self.data = {}
            return
        if type(data) == "dict":
            self.data = dict(data)
        else:
            self.data = {EVENTDATA_DEFAULT: data}

    def get_data(self, key=EVENTDATA_DEFAULT):
        return EventData.get_dict_val(self.data, key)

    @staticmethod
    def get_dict_val(dict, key=EVENTDATA_DEFAULT):
        return dict.get(key)

    def __repr__(self):
        return (
            self.__class__.__name__
            + " id: "
            + str(self.id)
            + " name: "
            + str(self.name)
            + " data: "
            + repr(self.data)
            + ("" if self.sender == None else " sender: " + self.sender.id)
        )


class EventQueue:
    def __init__(self, max_events=5):
        self.max_events = max_events
        self.q = deque((), self.max_events)

    def add(self, event):
        if len(self.q) >= self.max_events:
            raise Exception("event overflow")
        self.q.append(event)

    def pop(self):
        if len(self.q) > 0:
            return self.q.popleft()
        return None

    def reset(self):
        while self.pop() != None:
            pass

    def __len__(self):
        return len(self.q)
