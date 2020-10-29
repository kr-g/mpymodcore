class _ReprListIter(object):
    def __init__(self, el):
        self.el = el

    def __iter__(self):
        for el in self.el:
            if type(el) == ReprDict:
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


class ReprDict(object):
    def __iter__(self):
        return iter(_ReprDictIter(self.__repr__()))

    def reprlist(self, it):
        return list(map(lambda x: dict(x), it))

    ## todo rename and refactor
    ##  e.g. __conv_dict__, or __to_dict__
    def __repr__(self):
        raise Exception("implementation missing")
