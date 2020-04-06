
import machine
import sys
import binascii

import socket
import uselect

from modcore import VERSION
from modcore.log import LogSupport, logger

from .http_func import *


ALLOWED_DEFAULT = ["GET","POST"]

COOKIE_HEADER = "COOKIE"
SET_COOKIE_HEADER = "SET-COOKIE"
EXPIRE_COOKIE = ";expires=Thu, Jan 01 1970 00:00:00 UTC;"

##
## todo timeout handling here
##
   
class RequestHandler(LogSupport):
    
    def __init__(self,webserver,addr,client,client_file):
        LogSupport.__init__(self)
        self.webserver = webserver
        self.addr = addr
        self.client = client
        self.client_file = client_file
        self.request = None
        
    def __len__(self):
        # this can return None
        return self.request.content_len()
    
    def load_request(self,allowed=None):
        self.request = get_http_request( self.client_file, self.addr, allowed )
    
    def load_content( self, max_size=4096 ):
        self.request = get_http_content( self.client_file, self.request, max_size=max_size )

    def get_body(self, max_size=4096 ):
        if self.request.body==None:
            _len = len(self)
            if _len==None or _len==0:
                return
            self.info("load body data")
            self.load_content( max_size )
        return self.request.body
    
    def overflow(self):
        return self.request.overflow
    
    def send_response(self, status=200, header=None, response=None, \
                      type="text/html", suppress_id = False ):
        header = self._add_server_header(header,suppress_id)
        send_http_response( self.client_file, status, header, response, type )
      
    def close(self):
        self.client_file.close()
        self.client.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type != None:
            self.excep( exc_value, "closing socket on error" )
            try:
                if exc_type == type(BadRequestException):
                    send_http_status( self.client_file, 400 )
                else:
                    send_http_status( self.client_file, 500 )
                # send ending info
                send_http_data( self.client_file )
            except Exception as ex:
                self.excep( ex, "send status failed" )
        self.close()
    
    def _add_server_header(self,header,suppress_id):
        if header==None:
            header=[]
        _id = ""
        if not suppress_id:
            _id = ":"+binascii.hexlify( machine.unique_id() ).decode()
        header.append( ("Server", "modcore/" + str(VERSION) \
                           + " (" + sys.platform + _id  + ")" ) )
        return header
    
    def set_cookie(self,header,cookie,value=None):
        if header==None:
            header = []
        if value == None:
            value = "\'\'" + EXPIRE_COOKIE
        header.append( (SET_COOKIE_HEADER, \
                        cookie + "=" + str(value) ) )
        return header
        
  
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
        return RequestHandler( self, addr, client, client_file )
              
    def stop(self):
        self.poll.unregister( self.socket )
        self.socket.close()
        

