
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from modext.windup import Router

from . import security_store


class AuthRouter(Router):
    
    def __init__( self, root=None, allow_roles=None, status=401, location=None ):
        Router.__init__(self,root=root)
        self.allow_roles = allow_roles
        self.status = status
        self.location = location
    
    def _decor(self,to,method,groups,xtract=False):
        self.info("route", self.root + to, "for", "all" if method==None else method )
        if to[0]!="/":
            raise Exception( "malformed route", to )
        def dector(f):
            #@functools.wraps(f)
            def inner(*argv,**kwargs):
                self.info( "call route ", self.root, to )                
                self.__check_or_fail(groups,*argv)
                res = f(*argv,**kwargs)
                return res
            self._append( to, method, inner, xtract ) 
            return inner
        return dector
    
    def __check_or_fail(self,groups,*argv):
        req = argv[0]
        args = argv[1]        
        session = args.session
        try:
            if "auth_user" not in session:
                raise Exception("not logged in")
            allowed = security_store.check_group( session.auth_user, groups )
            if not allowed:
                raise Exception("no matching groups")
        except Exception as ex:
            self.excep( ex, "permission failed" )
            header = []
            if self.location!=None:
                header.append( ("Location", self.location ) )
            req.send_response( status=self.status, header=header )
            raise Exception("security failure, permission denied")
        
    def get(self,to,groups):
        return self._decor(to,"GET",groups)
    
    def post(self,to,groups):
        return self._decor(to,"POST",groups)
    
    def xget(self,to,groups):
        return self._decor(to,"GET",groups,True)
    
    def xpost(self,to,groups):
        return self._decor(to,"POST",groups,True)
    
    def __call__(self,to,groups,method=None,xtract=False):
        return self._decor(to,method,groups,xtract)
        
    