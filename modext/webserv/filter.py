
import json

from modcore.log import LogSupport
from .http_func import BadRequestException
from .webserv import COOKIE_HEADER


auto_cleanup = False

class Filter(LogSupport):
    
    def __init__(self,cleanup=None):
        LogSupport.__init__(self)
        if cleanup==None:
            cleanup = auto_cleanup
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
     
     
class ParameterDenseFilter(Filter):
    
    def filterRequest( self, request ):
        if request.xpar==None:
            return
        for k,v in request.xpar.items():
            if len(v)==1:
                request.xpar[k]=v[0]
            
 
class CookieFilter(Filter):
        
    def filterRequest( self, request ):
        request.xcookies = None
        cookie = request.header.get(COOKIE_HEADER,None)
        if cookie==None:
            return
        cookies = {}
        try:
            for c in cookie.split(";"):
                c = c.strip()
                if len(c)==0:
                    continue
                try:
                    k,v = c.split("=")
                    k = k.strip()
                except:
                    self.error( "client with strange cookie", c )
                    continue
                cookies[k] = v.strip()
        except Exception as ex:
            self.excep(ex,cookie)
        request.xcookies = cookies
 
        if self.cleanup:
            del request.header[COOKIE_HEADER]


class BodyTextDecodeFilter(Filter):
        
    def __init__(self,cleanup=False,mime=None):
        Filter.__init__(self,cleanup)
        self.mime = [None, 'text/plain', \
                         'application/x-www-form-urlencoded', \
                         'application/json','application/ld+json']
        if mime!=None:
            self.mime.extend( mime )
        
    def filterRequest( self, request ):
        
        if request.body == None:
            return
        
        if request.get_mime() in self.mime:
            try:
                request.body = request.body.decode()
                self.info("decoded body data")
            except Exception as ex:
                self.excep(ex)
            

class JsonParserFilter(Filter):
        
    def filterRequest( self, request ):
        
        request.xjson = None
        
        if request.body == None:
            return
        
        if request.get_mime() in ['application/json','application/ld+json']:
            try:
                request.xjson = json.loads( request.body )
                self.info("decoded body data")
            except Exception as ex:
                self.excep(ex)
            
        if self.cleanup:
            request.body = None

        
class FormDataFilter(Filter):
    
    def filterRequest( self, request ):
        
        request.xform = None
        
        if request.body == None:
            return
        
        if request.get_mime() in ['application/x-www-form-urlencoded']:
            
            request.xform = {}
            
            try:
                for kv in request.body.split("&"):
                    k, v = kv.split("=")
                    request.xform[k.strip()]=v.strip()
                        
                self.info("decoded body data")
            except Exception as ex:
                self.excep(ex)
            
        if self.cleanup:
            request.body = None
    
