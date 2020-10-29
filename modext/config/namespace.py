"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""


# todo
# refactor with ReprDict


class _ReprListIter(object):
    def __init__(self, el):
        self.el = el

    def __iter__(self):
        for el in self.el:
            if type(el) == Namespace:
                yield dict(el)
            else:
                yield el


class _ReprDictIter(object):
    def __init__(self, dic):
        self.dic = dict(dic)

    def __iter__(self):
        for attr in self.dic:
            val = self.dic[attr]
            if type(val) == list:
                yield attr, list(_ReprListIter(val))
            else:
                yield attr, val


class Namespace(object):
    def update(self, val_dict):
        for key, data in val_dict.items():
            # data = val_dict[key]
            self.set_attr(key, data)  # recursion
        return self

    def get_attr(self, nam):
        elem = self
        dot = nam.split(".")
        if len(dot) > 1:
            for d_name in dot[:-1]:
                nam = d_name.strip()
                if len(nam) == 0:
                    raise Exception("malformed dotted name specifier")
                if nam in elem:
                    elem = elem[nam]
                else:
                    raise Exception("not found", nam)
            nam = dot[-1]
        val = getattr(elem, nam)
        return val

    def set_attr(self, nam, val):
        dot = nam.split(".")
        if len(dot) == 1:
            if type(val) == dict:
                child = Namespace()
                child.update(val)
                val = child
            elif type(val) == list:
                child = []
                for ch in val:
                    ##todo list, tuple, ...
                    if type(ch) == dict:
                        el = Namespace()
                        el.update(ch)
                        ch = el
                    child.append(ch)
                val = child
            setattr(self, nam, val)
        else:
            elem = self
            for d_name in dot[:-1]:
                d_name = d_name.strip()
                if len(d_name) == 0:
                    raise Exception("malformed dotted name specifier")
                if d_name in elem:
                    elem = elem[d_name]
                    continue
                new_elem = Namespace()
                setattr(elem, d_name, new_elem)
                elem = new_elem
            setattr(elem, dot[-1], val)

    def __setitem__(self, key, val):
        return self.set_attr(key, val)

    def __delitem__(self, key):
        return delattr(self, key)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def items(self):
        return self.__dict__.items()

    """
    def __iter2__(self):
        for attr in self.__dict__:
            yield attr, self.__dict__[attr]
    """

    def __iter__(self):
        return iter(_ReprDictIter(self.__dict__))

    def __contains__(self, key):
        return key in self.__dict__
