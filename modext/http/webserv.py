
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import machine
import sys
import binascii

import socket
import uselect

import json

from modcore import VERSION
from modcore.log import LogSupport, logger

try:
    from modext.fiber import Fiber
    print("fiber module loaded")
except:
    print("fiber module not loaded")

from .http_func import *


ALLOWED_DEFAULT = ["GET","POST"]

COOKIE_HEADER = "COOKIE"
SET_COOKIE_HEADER = "SET-COOKIE"
EXPIRE_COOKIE = ";expires=Thu, Jan 01 1970 00:00:00 UTC;"

##
## todo timeout handling here
##
   
class RequestHandler(LogSupport):
    
    def __init__(self,webserver,addr,client,client_file,suppress_id = False):
        LogSupport.__init__(self)
        self.suppress_id = suppress_id
        self.webserver = webserver
        self.addr = addr
        self.client = client
        self.client_file = client_file
        self.request = None
        ## todo, move floop out ? see winup
        self.fiberloop = None
        
    def __len__(self):
        # this can return None
        return self.request.content_len()
    
    def load_request(self,allowed=None):
        self.request = get_http_request( self.client_file, self.addr, allowed )
    
    def load_content( self, max_size=4096 ):
        self.request = get_http_content( self.client_file, self.request, max_size=max_size )

    def load_chunk( self, chunk_size=256 ):
        return get_http_chunk( self.client_file, self.request, chunk_size=chunk_size )
    """
    def get_body(self, max_size=4096 ):
        if self.request.body==None:
            _len = len(self)
            if _len==None or _len==0:
                return
            self.info("load body data")
            self.load_content( max_size )
        return self.request.body
    """   
    def overflow(self):
        return self.request.overflow
    
    # send redirect
    def send_redirect(self, url, status=302, header=None ):
        if header==None:
            header=[]
        header.append( ("Location", url ) )
        self.send_response( status=status, header=header )
    
    # send a complete response
    def send_response(self, status=200, header=None, response=None, \
                      type="text/html", response_i=None ):
        header = self._add_server_header(header)        
        self._add_session_cookie(header)
        
        send_http_response( self.client_file, status, header, response, type, response_i )

    # send portions: header part
    def send_head(self, status=200, header=None, type="text/html" ):
        header = self._add_server_header(header)        
        self._add_session_cookie(header)
        # send empty response -> just send header
        send_http_response_header( self.client_file, status, header, type )
        
    # send portions: data part
    def send_data(self, response ):
        send_http_data( self.client_file, response )

    # json
    def send_json( self, obj, header=None, status=200, \
                   type='application/json' ):
        
        response = json.dumps( obj )
        
        self.send_response( status=status, header=header, response=response, type=type )
        

    # fiber
    def send_fiber( self, fbr ):
        try:
            self.fiberloop.add( Fiber( fbr ) )
        except:
            self.warn("fiber modul not loaded. discard.")

    def close(self):
        self.info("close socket")
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
    
    def _add_server_header(self,header):
        if header==None:
            header=[]
        _id = ""
        if not self.suppress_id:
            _id = ":"+binascii.hexlify( machine.unique_id() ).decode()
        header.append( ("Server", "modcore/" + str(VERSION) \
                           + " (" + sys.platform + _id  + ")" ) )
        return header
    
    def _add_session_cookie(self,header):
        try:
            if self.request.xsession_is_new:
                self.info("send session cookie")
                self.set_cookie( header, self.request.xsession_cookie, \
                                 self.request.xsession_id )
        except:
            pass
    
    def set_cookie(self,header,cookie,value=None,path="/"):
        if header==None:
            header = []
        if value == None:
            value = "\'\'" + EXPIRE_COOKIE
        header.append( (SET_COOKIE_HEADER, \
                        cookie + "=" + str(value) + "; Path=" + path ) )
        return header
        
  
class WebServer(LogSupport):
    
    def __init__(self,host='0.0.0.0',port=80,wrap_socket=None,suppress_id=False):
        LogSupport.__init__(self)
        self.host = host
        self.port = port
        self.wrap_socket = wrap_socket
        self.socket = None
        self.poll = None
        self.suppress_id = suppress_id
        
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
        
        try:
            if self.wrap_socket!=None:
                client = self.wrap_socket( client )
        except Exception as ex:
            self.excep(ex, "SSL failed" )
        
        client_file = client.makefile( 'rwb', 0 )
        return RequestHandler( self, addr, client, client_file, suppress_id=self.suppress_id )
              
    def stop(self):
        if self.poll!=None:
            self.poll.unregister( self.socket )
            self.poll = None
        if self.socket!=None:
            self.socket.close()
            self.socket = None
        

