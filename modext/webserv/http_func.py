
HTTP_CRLF = "\r\n"

class BadRequestException(Exception):
    pass

class InternalErrorException(Exception):
    pass


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

    def get_mime(self):
        mime = self.header.get("Content-Type".upper(),None)
        return mime.lower() if mime!=None else mime


def parse_header(line):
    pos = line.index(":")
    if pos < 0:
        return line.strip(), None
    return line[0:pos].strip(), line[pos+1:].strip()

def get_http_request(client_file,client_addr, allowed=None):
    
    if allowed==None:
        allowed = ALLOWED_DEFAULT
    
    line = client_file.readline()
    try:
        method, path, proto = line.decode().strip().split(" ")
    except:
        raise BadRequestException(line)
    
    method = method.upper()
    if method not in allowed:
        raise BadRequestException(line)
    
    if path[0]!="/":
        raise BadRequestException(line)
    
    request_header = {}    
    last_header = None
    while True:
        line = client_file.readline()
        if not line  or line == b'\r\n':
            break
        # support for multiple line spawning/ folding headers
        # with leading space, or tab
        if line[0] in [" ","\t"]:
            logger.warn( "## untested header parsing" )            
            request_header[ last_header ] += line.decode()            
            logger.warn( "## untested header parsing" )
            continue
        header, value = parse_header( line.decode() )
        last_header = header.upper()
        # no support for multi headers
        request_header[last_header]=value

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



def send_http_sequence( client_file, seq ):
    for s in seq:
        if s!=None:
            client_file.send( str(s) )

def send_http_status( client_file, st=200, ststr=None ):
    send_http_sequence( client_file, [ "HTTP/1.0 ", st, ststr, HTTP_CRLF ] )

def send_http_header( client_file, header, value, sep=": " ):
    send_http_sequence( client_file, [ header, sep, value, HTTP_CRLF ] )
    
def send_http_data( client_file, data=None ):
    if data != None and len(data)>0:
        send_http_header( client_file, "Content-Length", len(data) )
    client_file.send( HTTP_CRLF )  
    if data != None:
        client_file.send( data )
  
def send_http_response( client_file, status=200, header=None, \
                        response=None, type="text/html" ):
    send_http_status( client_file, status )
    if header != None:
        for h,v in header:
            #print("header",h,v)
            send_http_header( client_file, h, v )
    if type != None:
        send_http_header( client_file, "Content-Type", type )
    send_http_data( client_file, data=response )

