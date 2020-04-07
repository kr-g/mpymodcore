
from .content import ContentGenerator, LogSupport


class Router(ContentGenerator):

    def __init__( self, root=None, suppress_id=False ):
        ContentGenerator.__init__(self,root,suppress_id)
        self.route = []

    def handle(self,req):
        self.debug("searching route")
        request = req.request
        path = request.xpath
        for to, method, func in self.route:
            
            rc = self._root_match(request.xpath)
            if rc != None:
                if rc==False:
                    return
                
            url = self.root + to
            if url==path and ( method==None or method==request.method ):
                self.info( "found route", self.root, to, method, func )
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
            raise Exception( "malformed route", to )
        def dector(f):
            #@functools.wraps(f)
            def inner(*argv,**kwargs):
                self.info( "call route ", self.root, to )
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


