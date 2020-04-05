
from modcore.log import LogSupport


class Filter(LogSupport):
    
    def __init__(self,cleanup=False):
        LogSupport.__init__(self)
        self.cleanup = cleanup
    
    def filterRequest( self, request ):
        pass


class PathSplitFilter(Filter):
    
    def filterRequest( self, request ):
        path, query, fragment = self.split(request.path)        
        request.xpath = path
        request.xquery = query
        request.xfragment = fragment

        if self.cleanup:
            request.path = None
    
    def split(self,path):
        query = None
        fragment = None
        try:
            path, fragment = path.split("#")
        except:
            pass
        try:
            path, query = path.split("?")
        except:
            pass
        return path, query, fragment

        
class ParameterSplitFilter(Filter):
    
    def filterRequest( self, request ):
        request.xparam = None
        if request.xquery==None:
            return
        param = self.split(request.xquery)
        request.xparam = param
        
        if self.cleanup:
            request.xquery = None
    
    def split(self,param):
        parl = param.split("&")
        parl = list(filter( lambda x : x!=None and len(x)>0, parl ))
        return parl if len(parl)>0 else None


class ParameterValueFilter(Filter):
    
    def filterRequest( self, request ):
        request.xkeyval = None
        if request.xparam==None:
            return
        keyval = list(map( lambda x : x.split("="), request.xparam ))
        request.xkeyval = keyval
    
        if self.cleanup:
            request.xparam = None


class ParameterPackFilter(Filter):
    
    def filterRequest( self, request ):
        request.xpar = None
        if request.xkeyval==None:
            return
        keyval = {}
        for k,v in request.xkeyval:
            if k not in keyval:
                keyval[k]=[v]
                continue
            keyval[k].append(v)
            
        request.xpar = keyval
        
        if self.cleanup:
            request.xkeyval = None
     
     