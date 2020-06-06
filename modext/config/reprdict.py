

class _ReprDictIter(object):
    
    def __init__(self,dic):
        self.dic = dict(dic)
    
    def __iter__(self):
        for attr in self.dic:
            yield attr, self.dic[attr]
           
   
class ReprDict(object):
    
    def __iter__(self):
        return iter(_ReprDictIter( self.__repr__() ))

    def reprlist(self,it):
        return list(map( lambda x : dict(x), it ))

    def __repr__(self):
        raise Exception("implementation missing")
    
    