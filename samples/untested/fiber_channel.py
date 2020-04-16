
#from modcore.log import LogSupport
#from modcore.fiber import *


class DataChunk(object):
    
    def __init__(self,data):
        self.data = data
        self.pre = None
        
    def link(self,chunk):
        if chunk!=None:
            chunk.pre = self
        return self
    
    def __len__(self):
        return len(self.data)
    
    # find a obj in the data 
    def find( self, obj, start=0 ):
        return self.data.find( obj, start )
    
    # get a sub portion until pos
    def slice( self, pos ):
        data = self.data[:pos]
        self.data = self.data[pos+1:]
        return data
    
    def merge(self):
        if self.pre!=None:
            self.data += self.pre.data
            # keep order
            self.pre.data = None
            self.pre = self.pre.pre
            # done
        return self

    def close(self):
        self.data = None
        if self.pre!=None:
            self.pre.close()
            
    def __repr__(self):
        return self.__class__.__name__ + "(" \
              + repr( self.data ) + ")"
  

class FiberChannelBrokenException(Exception):
    pass
class FiberChannelEmptyException(Exception):
    pass

# optimized single link list
# with option too peek (top)
# and split at defined point
class FiberChannel(object):
    
    def __init__(self):
        #LogSupport.__init__(self)
        self.first = None
        self.last = None
        self._broken = False
        
    # no put allowed on closed channel
    def put( self, data ):
        if self._broken==True:
            raise FiberChannelBrokenException()
        chunk = DataChunk(data)
        self.first = chunk.link( self.first )
        if self.last == None:
            self.last = self.first
        
    # its possible to get all pending data
    # even the channel is closed/ broken
    def pop(self):
        if self.last==None:
            raise FiberChannelEmptyException()
        chunk = self.last
        self.last = chunk.pre
        chunk.pre=None
        if self.last==None:
            self.first=None
        return chunk.data
    
    def __len__(self):
        if self.last==None:
            raise FiberChannelEmptyException()
        _len = 0
        next = self.last
        while next != None:
            _len += len(next)
            next = next.pre
        return _len
    
    def top(self):
        if self.last==None:
            raise FiberChannelEmptyException()
        return self.last
    
    ## todo
    
    def hangup(self):
        self._broken = True
        
    def dense(self):
        if self.last == None:
            return
        if self.last.pre == self.first:
            self.first = self.last
        self.last.merge()
    
    def data_available(self):
        return self.last != None
    
    def poll(self):
        if self._broken==True:
            raise FiberChannelBrokenException()
        if self.last==None:
            raise FiberChannelEmptyException()
        return True
    
    def close(self):
        if self.last!=None:
            self.last.close()
            self.last = None
        self.first = None
        self._broken = True

    def __repr__(self):
        return self.__class__.__name__ + "(" \
                  + str(self.last != None) + ")" 


def fc_readline(fc,max_size_dense=128):

    chunk = fc.top()
           
    pos = chunk.find("\n".encode())

    if pos>=0:
        line= chunk.slice(pos)
        return line    
    
    if chunk.pre==None:
        if fc._broken:
            # return pending bytes
            if len(chunk)>0:
                chunk = fc.pop()
                return chunk
            raise FiberChannelBrokenException()
        return None
    
    if len(chunk)>max_size_dense:
        raise Exception("buffer overflow")
    
    fc.dense()
     
     
     
     
def sample():     
               
    fc = FiberChannel()

    chk_size = 64
    with open( "../../boot.py","rb" ) as f:
        while True:
            rc = f.read( chk_size )
            if len(rc)==0:
                break
            fc.put( rc )


    print( len(fc) )

    # fake end of transmisson
    fc.hangup()
     
    if False:
        while fc.data_available():
            chunk = fc.pop()
            print(chunk)
     
    if True: 
        while fc.data_available():
            l = fc_readline(fc)
            if l!=None:
                print(l.decode())
            else:
                print(">dense")
        


sample()