
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from modcore.log import LogSupport


class Namespace(object):
    
    def update(self, val_dict ):
        for key in val_dict:
            data = val_dict[key]
            self.set_attr(key,data) # recursion
        return self

    def get_attr(self,nam):
        elem = self
        dot = nam.split(".")
        if len(dot)>1:
            for d_name in dot[:-1]:
                nam = d_name.strip()
                if len(nam)==0:
                    raise Exception("malformed dotted name specifier")
                if nam in elem:
                    elem = elem[nam]
                else:
                    raise Exception("not found", nam )
            nam = dot[-1]
        val = getattr(elem,nam)
        return val
        
    def set_attr(self,nam,val):
        dot = nam.split(".")
        if len(dot)==1:
            if type(val)==dict:
                child = Namespace()
                child.update( val )
                val = child
            elif type(val)==list:
                child = []
                for ch in val:
                    ##todo list, tuple, ...
                    if type(ch)==dict:
                        el = Namespace()
                        el.update( ch )
                        ch = el
                    child.append( ch )
                val = child
            setattr(self,nam,val)
        else:
            elem = self
            for d_name in dot[:-1]:
                d_name = d_name.strip()
                if len(d_name)==0:
                    raise Exception("malformed dotted name specifier")
                if d_name in elem:
                    elem = elem[d_name]
                    continue
                new_elem = Namespace()
                setattr( elem, d_name, new_elem )
                elem = new_elem
            setattr(elem,dot[-1],val)

    def __setitem__(self,key,val):
        return self.set_attr(key,val)

    def __delitem__(self,key):
        return delattr(self,key)

    def __getitem__(self,key):
        return getattr(self,key)

    def get(self,key,default=None):
        return self.__dict__.get(key,default)

    def __iter__(self):
        for attr in self.__dict__:
            yield attr
         
    ##todo refactor with ReprDict
    def __repr__(self):
        s = "{ "
        deli = ""
        for attr in self:
            s += deli
            s += '"' + attr + '" : '
            val = getattr( self, attr )
            if type(val)==str:
                s += '"' + str(val) + '"'
            elif type(val)==list:
                s += '['
                dell = ""
                for el in val:
                    s += dell
                    s += str(el)
                    dell =", "
                s += ']'
            else:                
                s += str(val) 
            deli = ", "
        s += "}"
        return s


class Processor(LogSupport):
    
    def __init__(self,windup):
        LogSupport.__init__(self)
        self.windup = windup
        self.req = None
        self.req_done = False
            
    def run(self,req):
        
        self.req = req
        
        req.load_request(self.windup.allowed)
        
        # when logging use argument list rather then
        # concatenate strings together -> performace        
        self.info( "request" , req.request )
        self.info( "request content len", len( req ) )
                
        request = req.request
        
        request.xargs = Namespace()
        
        for f in self.windup.headerfilter:
            rc = f.filterRequest( request )
        
        req.load_content( max_size=4096 )
        if req.overflow == True:
            # if bodydata is too big then no data is loaded automatically
            # dont run body filters automatically if max size exceeds
            # if a request contains more data the generator
            # needs to decide what to do in detail
            #
            # some req.x-fields are then not available !!!
            # because each filter sets them on its own !!!
            #
            self.warn("no auto content loading. size=", len(req))
            self.warn("not all req.x-fields area available")
        else:
            for f in self.windup.bodyfilter:
                f.filterRequest( request )
                
        self.info( "xargs", request.xargs )

        # after auto cleanup with filter this can be None
        body = req.request.body 
        if body!=None:
            self.info( "request content", body )
          
        self.req_done = False
        for gen in self.windup.generators:
            self.req_done = gen.handle( req )
            if self.req_done:
                break
        
        return self.req_done
        
    def _after_run_done(self,req):
        pass
    
    def _after_run_undone(self,req):
        self.req_done = True
        self.windup.call404(req)
        
    def loop(self):
        pass
    
    def done(self):
        return self.req_done
        
    def stop(self):
        pass
    
    def kill(self,reason=None):
        pass
    
    def close(self):
        self.req.close()
        self.req=None
    
    