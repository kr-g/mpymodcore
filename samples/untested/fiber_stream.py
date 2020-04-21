
"""

in process / working / concept


"""


"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from fiber_channel import FiberChannel, fc_readline

  
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


