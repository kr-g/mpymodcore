
from .content import ContentGenerator, LogSupport


class Router(ContentGenerator):

    def __init__( self, suppress_id=False ):
        LogSupport.__init__(self)
        self.suppress_id = suppress_id
        self.route = []

    def handle(self,req):
        self.debug("searching route")
        request = req.request
        for to, method, func in self.route:
            if to==request.xpath and ( method==None or method==request.method ):
                self.info( "found route", to, method, func )
                para = request.xpar
                if para==None:
                    para = {}
                f = func( req, para )
                return True
        
    def _append(self,to,method,func):
        if method!=None:
            method = method.upper()
        self.route.append( (to,method,func) )
        
    def _decor(self,to,method):
        self.info("route", to, method )
        if to[0]!="/":
            raise Exception( "malformed route" )
        def dector(f):
            #@functools.wraps(f)
            def inner(*argv,**kwargs):
                self.info( "call route ", to )
                res = f(*argv,**kwargs)
                return res
            self._append( to, method, inner ) 
            return inner
        return dector

    def get(self,to):
        return self._decor(to,"GET")
    
    def post(self,to):
        return self._decor(to,"POST")
    
    def __call__(self,to="/index",method=None):
        return self._decor(to,method)


