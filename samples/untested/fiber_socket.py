
"""

in process / working / concept


"""

"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

"""

websocket 

https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers

https://tools.ietf.org/html/rfc6455#section-5.1

"""

import time
import binascii
import hashlib
import socket
import struct


HTTP_CRLF = "\r\n"

def open_connection(host,port=80):
    
    ## todo reconnection handling
    
    sock = socket.socket()
    sockaddr = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    sockaddr = sockaddr[0][-1]
    #print(sockaddr)
    
    #
    # non blocking socket !!!
    #
    sock.settimeout(0)
    
    try:
        sock.connect(sockaddr)
    except OSError:
        pass
    except Exception as ex:
        print("err",ex,type(ex))
        sock.close()
    
    return sock


def send_data(sock,data):
    
    ## todo use stream object
    
    while len(data)>0:
        try:
            rc = sock.send( data )
            #print( ">",data , end="" )
            #print( ">>",rc, len(data))
            data = data[rc:]
        except OSError as ex:
            pass
            #print( "send err", ex )
    
    
def recv_data(sock,max=200000):
    
    ## todo use stream object
    
    buf = bytes()
    while max>=0:
        max-=1
        try:
            c = sock.recv(512)
            if len(c)==0:
                break
            buf += c
            #print("ok", c)
            #if buf.endswith(b"\r\n\r\n"):
            #    break
            break
        except OSError as ex:
            pass
            #time.sleep(0.5)
            #if max%10==0:
            #    print( "recv err", ex, buf )

    return buf if len(buf)>0 else None


def send_frame(sock,data,opcode=0x02,mask=None):
    
    ## todo use stream object
    
    payload_len = len(data)
    
    buf = bytes()
    buf += bytes([ 0b10000000 | ( opcode & 0b00001111 ) ]) # FIN bit always set, mask opcode
    
    byte1 = [ payload_len ]
    paylen = []
    if payload_len>=126 and payload_len<=0xffff:
        byte1 = [126]
        paylen = struct.pack(">H",payload_len)
    if payload_len>0xffff:
        byte1 = [127]
        paylen = struct.pack(">Q",payload_len) 
    if mask!=None:
       byte1[0] |= 0b10000000 # set MASK bit   
    buf += bytes(byte1)
    buf += bytes(paylen)
            
    if mask!=None:
        print("send mask")
        buf += struct.pack( ">I", mask )
        maskbuf = buf[-4:] 
        #print( [bin(mb) for mb in maskbuf], end = " " )
        
        nbuf = bytes()
        for p in range(0,len(data)):
            decoded = data[p] ^ maskbuf[p % 4]
            nbuf += bytes([decoded])
        data = nbuf
        
    buf += data
 
    """ 
    print( ">>>", end="" )
    for i in range( 0, len(buf )):
        print( bin( buf[i] ), end=" ")
    print()
    """
    print( "send>", buf )
    
    
    send_data( sock, buf )
    

def recv_frame(sock):
    
    ## todo use stream object
    
    buf = recv_data(sock)
    if buf==None:
        return buf

    """
    print( "<<<", end="" )
    for i in range( 0, len(buf )):
        print( bin( buf[i] ), end=" ")
    print()
    """

    fin = buf[0] & 0b10000000
    rsv = buf[0]>>4 & 0b00000111
    opcode = buf[0] & 0b00001111
    
    if not fin:
        raise Exception("recv continue frame. not supported.")
    if rsv!=0:
        print( "recv RSV=", rsv )
    
    if opcode==0x9:
        print( "recv ping" )
        # ping, pong back
        opcode = 0xa # pong opcode
        buf[0] = ( buf[0] & 0x11110000 ) | opcode

        send_data( sock, buf )
        return None
    
    mask = buf[1] & 0b10000000
    
    payload_len = buf[1] & 0b01111111

    pos = 2

    if payload_len == 126:
        payload_len = struct.unpack( ">H", buf[pos:pos+2] )
        pos += 2
    if payload_len == 127:
        payload_len = struct.unpack( ">Q", buf[pos:pos+8] )
        pos += 8

    data = bytes()
    
    if mask:
        mask_key = struct.unpack( ">I", buf[pos:pos+4] )
        pos += 4
        print("recv mask")
        for p in range( 0, payload_len ):
            data += bytes( buf[pos] ^ mask_key[ p % 4 ] )
    else:
        data += bytes(buf[pos:])

    return data



def sample():
    
    sock = open_connection("echo.websocket.org")
    
    #print("connected")
    
    salt = str(time.time())
    sec_key = binascii.b2a_base64(salt.encode()).decode().strip()
    
    data = "GET / HTTP/1.1" +HTTP_CRLF
    data += "Host: echo.websocket.org" +HTTP_CRLF
    data += "Upgrade: websocket" +HTTP_CRLF
    data += "Connection: upgrade" +HTTP_CRLF
    data += "Sec-WebSocket-Key: " + sec_key +HTTP_CRLF
    data += "Sec-WebSocket-Version: 13" +HTTP_CRLF
    data += "User-Agent: modcore" +HTTP_CRLF
    #data += "Accept: */*" +HTTP_CRLF
    data += HTTP_CRLF
    
    send_data(sock,data.encode())
    
    #print( "websocket handshake send" )
    
    buf = recv_data(sock)
    
    all_lines = buf.decode().splitlines() 
    websocket = list(filter( \
        lambda x : x.lower().startswith('Sec-WebSocket-Accept'.lower()), \
        all_lines ))
    #print( all_lines )
    #print( salt, list(websocket) )
    
    if len(websocket)==1:
        hash = hashlib.sha1()
        hash.update(sec_key.encode())
        hash.update("258EAFA5-E914-47DA-95CA-C5AB0DC85B11".encode())
        control_key = binascii.b2a_base64( hash.digest() ).strip().decode()
        recv_key = websocket[0].split(":")[1].strip()
        
        if control_key!=recv_key:
            raise Exception("websocket wrong secret key" )
        print("websocket handshake ok")      
    else:
        raise Exception("websocket handshake missing" )
    
    send_frame(sock,"this is a masked demo text".encode(),opcode=0x2 , \
               mask = 0b10101010101010101010101010101010)

    max = 1
    while max>0:
        max -= 1
        print( "recv" )
        buf = recv_frame(sock)
        if buf==None:
            break
        if len(buf)==0:
            break
        print(buf)

    sock.close()
    
if __name__=='__main__':
    sample()
    
    
    