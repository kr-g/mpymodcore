
#from modcore.log import LogSupport
#from modcore.fiber import *


class FiberChannelDataChunk(object):
    
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
        self.data = self.data[pos:]
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
        chunk = FiberChannelDataChunk(data)
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
    
    def top(self):
        if self.last==None:
            raise FiberChannelEmptyException()
        return self.last
    
    def __len__(self):
        if self.last==None:
            raise FiberChannelEmptyException()
        _len = 0
        next = self.last
        while next != None:
            _len += len(next)
            next = next.pre
        return _len
    
    ## todo
    
    def hangup(self):
        self._broken = True
        
    def broken(self):
        return self._broken
        
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

    if max_size_dense==None:
        max_size_dense = 128

    try:
        chunk = fc.top()
    except FiberChannelEmptyException:
        return bytes()
           
    pos = chunk.find("\n".encode())

    if pos>=0:
        line= chunk.slice(pos+1)
        return line    
    
    if chunk.pre==None:
        if fc.broken()==True:
            # return pending bytes
            if len(chunk)>0:
                chunk = fc.pop()
                return chunk
        return None
    
    if len(chunk)>max_size_dense:
        raise Exception("buffer overflow")
    
    fc.dense()
    
    return None
          
  
class FiberStreamIO(object):
    
    def open(self):
        pass
    
    # reading from fiber stream
    # return None if no data available
    # return zero length bytes() for EOF
    def read(self, fchan ):
        pass
    
    # writing into fiber stream
    # return True is more data is available
    def write(self, fchan ):
        pass
  
    def close(self):
        pass
  
 
class FiberStream(object):
    
    def __init__(self, channel=None):
        self._closable = channel == None
        if channel==None:
            channel=FiberChannel()
        self.channel = channel
        self._reader = None
        self._writer = None
    
    def close(self):
        if self._closable==True:
            self.channel.close()
            self.channel = None
        # close ???
        if self._reader!=None:
            self._reader.close()
        if self._writer!=None:
            self._writer.close()
    
    def reader(self,fstreamio=None):
        self._reader = fstreamio

    def writer(self,fstreamio=None):
        self._writer = fstreamio

    # if no reader is defined return chunk
    def read(self):
        try:
            if self._reader==None:
                return self.channel.pop()
            return self._reader.read(self.channel)
        except FiberChannelEmptyException:
            return bytes()
    
    # if given write data to channel 
    def write(self,data=None):
        if data!=None:
            self.channel.push(data)
        return self._writer.write(self.channel)
     
     
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
                print(l)
            else:
                print(">dense")


def sample2():     
               
    fc = FiberChannel()

    cnt = 0
    chk_size = 64
    with open( "../../boot.py","rb" ) as f:
        while True:
            rc = f.read( chk_size )
            if len(rc)==0:
                break
            
            # add with line numbers
            fc.put( (str(cnt) +":").encode() + rc )
            
            cnt += 1
            # steal alreay some data...
            if cnt % 3 == 0:
                chunk = fc.pop()
                print("pop at cnt=",cnt,"->",chunk) 

    print( len(fc) )

    # fake end of transmisson
    #fc.hangup()
    print("-"*37)
     
    while fc.data_available():
        chunk = fc.pop()
        print(chunk)


def sample3():

    class FiberStreamIO_file_input_writer(FiberStreamIO):
        
        def __init__(self,fnam,blksize=128,lineno=False):
            self.fnam = fnam
            self.blksize = blksize
            self.done = False
            self.lineno = lineno
            
        def open(self):
            self.file = open(self.fnam,"rb")
            self.cnt = 0
            
        def write( self, fchan ):
            self.cnt += 1

            if self.done==False:
                
                rc = self.file.read(self.blksize)
                if len(rc)>0:
                    fchan.put(rc)
                    
                self.done = len(rc)==0                
                if self.done:
                    fchan.hangup()
                    
            return self.done!=True
               
        def close(self):
            self.file.close()


    class FiberStreamIO_readline_reader(FiberStreamIO):                        
        def read( self, fchan ):        
            return fc_readline(fchan)
                       

    fc = FiberChannel()
    fs = FiberStream(channel=fc)
    fiw = FiberStreamIO_file_input_writer( "../../boot.py", blksize=32 )
    fiw.open()
    fs.writer( fiw )

    cnt = 0

    # write to channel, steal away every 3rd line
    while fs.write():
        cnt+=1
        if cnt%3==0:
            # read raw data chunk, default for stream
            print(fs.read())

    print("-"*37)
    print("read until end with readline")
    print("-"*37)

    rlr = FiberStreamIO_readline_reader()
    fs.reader(rlr)

    while True:
        # read uses readline io reader to read from channel
        data = fs.read()
        if data==None:
            #print(">dense")
            continue
        if len(data)==0:
            break
        print(data)

        
