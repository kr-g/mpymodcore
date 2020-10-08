
import os

from modcore.log import logger
from modcore import modc

from modext.windup import Router, StaticFiles

from mod3rd.simplicity import *
from modext.windup import Namespace


router = Router( root="/admin" )


@router.xget("/file/:filename")
def get_file( req, args ):
    rest = args.rest
    fnam = _conv(rest.filename)
    StaticFiles._send_chunked_file( req, fnam )
    
@router.xpost("/file/:filename")
def post_file( req, args ):
    
    rest = args.rest
    fnam = _conv(rest.filename)
    
    request = req.request
    data = request.body
    
    logger.info("overflow",req.overflow)
    logger.info("content_len",request.content_len())
    logger.info(fnam)
    logger.info(data)

    if req.overflow == True:
        logger.info("file to big")
        ## todo handle files > 4096 bytes
        # 403 forbidden
        req.send_response( status= 403 )
        return
    
    with open( fnam, "wb" ) as f:
        f.write( data )
        f.flush()

    req.send_response( )
    
    
@router.xget("/fstat/:filename")
def get_fstat( req, args ):
    rest = args.rest
    fnam = _conv(rest.filename)
    req.send_json(_get_file_info(fnam))


@router.xget("/mkdir/:path")
def get_mkdir( req, args ):
    rest = args.rest
    path = _conv(rest.path)
    
    path = path.split("/")
    
    fp = ""
    for p in path:
        fp += p
        try:
            os.mkdir(fp)
        except:
            pass
        fp += "/"

    req.send_response( )


@router.xget("/remove/:path/:recur_level")
def get_remove( req, args ):
    rest = args.rest
    path = _conv(rest.path)
    recur_level = int(rest.recur_level)
    
    fi = _get_file_info(path)
    folders = [fi]
    if fi["mode"]==16384:
        folders.extend( _get_folder_info(path,recur_level) )
    
    _remove(folders)
    
    req.send_response( )


@router.xget("/listdir/:path/:recur_level")
def get_listdir( req, args ):
    rest = args.rest
    path = _conv(rest.path)
    recur_level = int(rest.recur_level)
    
    logger.info(path,recur_level)
    
    folders = []
    folders.extend( _get_folder_info(path,recur_level) )
    
    req.send_json( folders )
    

@router.post("/rename")
def post_rename( req, args ):
    json = args.json
    fnam = json.filename
    new_fnam = json.filename_new
    os.rename(fnam,new_fnam)
    req.send_response( )
    

def _remove(folders):
    for fp in folders:
        if "children" in fp:
            _remove(fp["children"])
        if fp["mode"]==16384:
            os.rmdir(fp["name"])
        else:
            os.remove(fp["name"])
    

def _get_folder_info(path,recur_level):
    
    info = []
    
    fli = os.listdir(path)
    
    for f in fli:
        #logger.info(f)
        fnam = path+"/"+f
        fi = _get_file_info(fnam)
        if recur_level>0 and fi["mode"]==16384:
            fi["children"] = _get_folder_info( fnam, recur_level-1 )
        info.append( fi )
        
    return info


def _get_file_info(f):
    fs = os.stat( f )
    fi = {
            "name" : f,
            "mode" : fs[0],
            "size" : fs[6],
            "atime" : fs[7],
            "mtime" : fs[8],
            "ctime" : fs[9],
        }
    return fi


## todo refactor with FormDataDecodeFilter
def _conv(val):
    
    ## todo not fully compliant
    val = val.replace("+", " ")

    pos=0
    while True:
        pos = val.find("%",pos)
        if pos>=0:
            hex = val[pos+1:pos+3]
            b = int(hex, 16)
            s = chr(b)
            #print(hex,b,s)
            val = val[:pos] + str(s) + val[pos+3:]
            pos += 1        
        else:
            break
    return val


print()
print("*"*37)
print( "loading file api rest modules!!!" )
print("*"*37)
print()

