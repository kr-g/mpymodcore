
import socket
import uselect

from modcore.log import LogSupport, logger


##
## todo timeout handling here
##

class HTTPRequest():
    
    def __init__(self, client_addr, method, path, proto, header, body=None ):
        self.client_addr = client_addr
        self.method = method.upper()
        self.path = path
        self.proto = proto
        self.header = header
        self.body = body
        self.overflow = False
        
    def __repr__(self):
        return self.__class__.__name__  + " " + str(self.client_addr[0]) \
                + " " + self.method + " " \
                + self.path + " " \
                + self.proto + " " \
                + repr(self.header) + " " \
                + ("<overflow>" if self.overflow else \
                    ( str( len( self.body ) ) if self.body != None else "<empty>" ))
       
    def ok(self):
        return not self.overflow
    
    def content_len(self):
        contlen = self.header.get("Content-Length".upper(),None)
        if contlen!=None:
            return int(contlen)
 
 
# primitives 

def parse_header(line):
    pos = line.index(":")
    if pos < 0:
        return line.strip(), None
    return line[0:pos].strip(), line[pos+1:].strip()

def get_http_request(client_file,client_addr):
    
    request_header = {}    
    line = client_file.readline()    
    method, path, proto = line.decode().strip().split(" ")
    
    while True:
        line = client_file.readline()
        if not line  or line == b'\r\n':
            break
        header, value = parse_header( line.decode() )
        request_header[header.upper()]=value

    return HTTPRequest( client_addr, method, path, proto, request_header )

def get_http_content(client_file,req,max_size=4096):
    toread = req.content_len()
    if toread != None:
        if toread < max_size:            
            content = client_file.read( toread )
            req.body = content
        else:
            req.overflow = True
    return req
   
HTTP_CRLF = "\r\n"

def send_http_status( client_file, st=200 ):
    client_file.send( "HTTP/1.0 " )
    client_file.send( str( st ) )
    client_file.send( HTTP_CRLF )  

def send_http_header( client_file, header, value ):
    client_file.send( header )
    client_file.send( ": " )
    client_file.send( str( value ) )
    client_file.send( HTTP_CRLF )  
    
def send_http_data( client_file, data=None ):
    if data != None and len(data)>0:
        send_http_header( client_file, "Content-Length", len(data) )
    client_file.send( HTTP_CRLF )  
    if data != None:
        client_file.send( data )
  
def send_http_response( client_file, status=200, header=None, response=None, type="text/html" ):
    send_http_status( client_file, status )
    if header != None:
        for h,v in header:
            send_http_header( client_file, h, v )
    if type != None:
        send_http_header( client_file, "Content-Type", type )
    send_http_data( client_file, data=response )
 
# end of primitives
  
  
class RequestHandler(LogSupport):
    
    def __init__(self,webserver,request,client,client_file):
        LogSupport.__init__(self)
        self.webserver = webserver
        self.request = request
        self.client = client
        self.client_file = client_file
        
    def __len__(self):
        # this can return None
        return self.request.content_len()
    
    def load_content( self, max_size=4096 ):
        self.request = get_http_content( self.client_file, self.request, max_size=max_size )
    
    def get_body(self):
        return self.request.body
    
    def overflow(self):
        return self.request.overflow
    
    def send_response(self, status=200, header=None, response=None, type="text/html" ):
        send_http_response( self.client_file, status, header, response, type )
      
    def close(self):
        self.client_file.close()
        self.client.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
  
class WebServer(LogSupport):
    
    def __init__(self,port=80):
        LogSupport.__init__(self)
        self.host = '0.0.0.0'
        self.port = port
        
    def start(self):
        self.addr = socket.getaddrinfo( self.host, self.port)[0][-1]
        
        self.socket = socket.socket()
        self.socket.bind(self.addr)
        self.socket.listen(1)
        
        self.poll = uselect.poll()
        self.poll.register( self.socket, uselect.POLLIN )
  
    def can_accept(self,timeout=153):        
        res = self.poll.poll(timeout)
        return res != None and len(res)>0           
            
    def accept(self):
        
        client, addr = self.socket.accept()
        self.debug( 'client connected from', addr )
        
        client_file = client.makefile( 'rwb', 0 )

        try:
            req = get_http_request( client_file, addr )  
            
            return RequestHandler( self, req, client, client_file )
            
        ## todo timeouts           
        except Exception as ex:
            self.excep(ex,"accept")
            client_file.close()
            client.close()
    
    def stop(self):
        self.poll.unregister( self.socket )
        self.socket.close()
        

