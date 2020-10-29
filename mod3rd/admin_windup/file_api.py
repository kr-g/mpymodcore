import os
import hashlib
import binascii

from modcore.log import logger
from modcore import modc

from modext.windup import Router, StaticFiles

from mod3rd.simplicity import *
from modext.windup import Namespace


router = Router(root="/admin")


def _is_file(mode):
    return mode & 32768 > 0


def _is_dir(mode):
    return mode & 16384 > 0


@router.xget("/file/:filename")
def get_file(req, args):
    rest = args.rest
    fnam = _conv(rest.filename)

    try:
        fi = _get_file_info(fnam)
        if _is_dir(fi["mode"]):
            raise Exception("file is directory")
    except Exception as ex:
        logger.excep(ex, "bad file", fnam)
        req.send_response(status=404)
        return

    StaticFiles._send_chunked_file(req, fnam)


@router.xpost("/file/:filename")
def post_file(req, args):

    rest = args.rest
    fnam = _conv(rest.filename)

    request = req.request
    data = request.body

    logger.info("overflow", req.overflow())
    content_len = request.content_len()
    logger.info("content_len", content_len)
    logger.info(fnam)
    logger.info(data)

    if req.overflow() == True:
        logger.info("file to big, processing chunks")
        # handle files > 4096 bytes

        with open(fnam, "wb") as f:

            while content_len > 0:
                ## todo timeout error handling
                data = req.load_chunk(chunk_size=min(content_len, 512))
                if len(data) == 0:
                    ## todo, never reached currently => fiber socket stream
                    logger.info("end of transmission")
                    break
                logger.info(content_len, data)
                content_len -= len(data)

                f.write(data)
                f.flush()

        ## todo error handling
        req.send_response()
        return

    with open(fnam, "wb") as f:
        f.write(data)
        f.flush()

    req.send_response()


@router.xget("/fstat/:filename")
def get_fstat(req, args):
    rest = args.rest
    fnam = _conv(rest.filename)
    req.send_json(_get_file_info(fnam))


@router.xget("/hash/:filename")
def get_hash(req, args):
    rest = args.rest
    fnam = _conv(rest.filename)
    digest = _get_file_hash(fnam)
    hash = binascii.hexlify(digest).decode()
    req.send_json(
        {
            "file": fnam,
            "hash": hash,
        }
    )


@router.xget("/mkdir/:path")
def get_mkdir(req, args):
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

    req.send_response()


@router.xget("/remove/:path/:recur_level")
def get_remove(req, args):
    rest = args.rest
    path = _conv(rest.path)
    recur_level = int(rest.recur_level)

    _remove_path(path, recur_level)

    req.send_response()


@router.xget("/listdir/:path/:recur_level")
def get_listdir(req, args):
    rest = args.rest
    path = _conv(rest.path)
    recur_level = int(rest.recur_level)

    logger.info(path, recur_level)

    folders = []
    folders.extend(_get_folder_info(path, recur_level))

    req.send_json(folders)


@router.post("/rename")
def post_rename(req, args):
    json = args.json
    fnam = json.filename
    new_fnam = json.filename_new
    os.rename(fnam, new_fnam)
    req.send_response()


@router.get("/browse")
def get_browse(req, args):
    # rest = args.rest
    path = "/"
    try:
        path = _conv(args.param.path)
        if len(path) == 0:
            path = "/"
    except:
        pass
    logger.info(path)

    folder = _get_folder_info(path, 0)
    logger.info(path, folder)

    data = _browse_html(path, folder)

    req.send_response(response=data, fibered=True)


def _browse_html(path, folder):
    t = """
        <!DOCTYPE html>
        <html>
        <title>browse {path}</title>
        <body>

        <h2>Content: {path}</h2>

        {!notroot}<div><a href='./browse?path={parent}'>.. up ..</a></div><div>&nbsp;</div>{}

        <table>
        {*folder}        
        <tr>
            <td>
            {!isfile(_)}
                {name(_)} </td><td> {_.size} </td><td>
                    <a target="_blank" href='./editor/#?file={_.name}'>open in editor</a></td>
            {}
            {!isdir(_)}
                <a href='./browse?path={_.name}'>{name(_)}</a>
            {}
            </td>
        </tr>
        {}
        </table>

        </body>
        </html>            
    """

    smpl = Simplicity(t, esc_func=simple_esc_html)
    ctx = Namespace()

    def _is_no_dir(fi):
        return _is_file(fi.mode)

    def _is_dir(fi):
        return not _is_file(fi.mode)

    def _chop_path(fi):
        return fi.name[len(path) :]

    ctx.update(
        {
            "notroot": path != "/",
            "isfile": _is_no_dir,
            "isdir": _is_dir,
            "parent": path[: path.rindex("/")],
            "path": path,
            "name": _chop_path,
            "folder": folder,
        }
    )

    data = smpl.print(ctx)
    return data


def _remove(folders):
    for fp in folders:
        if "children" in fp:
            _remove(fp["children"])
        if _is_file(fp["mode"]):
            os.remove(fp["name"])
        else:
            os.rmdir(fp["name"])


def _remove_path(path, recur_level):
    fi = _get_file_info(path)
    folders = [fi]
    if _is_dir(fi["mode"]):
        fi["children"] = _get_folder_info(path, recur_level)
    print(folders)
    _remove(folders)


def _get_folder_info(path, recur_level):

    info = []

    fli = os.listdir(path)

    for f in fli:
        # logger.info(f)
        fnam = path + "/" + f
        if fnam[0:2] == "//":
            fnam = fnam[1:]
        fi = _get_file_info(fnam)
        if recur_level > 0 and _is_dir(fi["mode"]):
            fi["children"] = _get_folder_info(fnam, recur_level - 1)
        info.append(fi)

    return info


def _get_file_info(f, include_hash=False):
    fs = os.stat(f)
    fi = {
        "name": f,
        "mode": fs[0],
        "size": fs[6],
        "atime": fs[7],
        "mtime": fs[8],
        "ctime": fs[9],
        "hash": None,
    }
    if include_hash:
        fi["hash"] = _get_file_hash(f)
    return fi


def _get_file_hash(fnam, blk_size=512):
    sha = hashlib.sha256()
    with open(fnam) as f:
        while True:
            cb = f.read(blk_size)
            if len(cb) == 0:
                break
            sha.update(cb)
    return sha.digest()


## todo refactor with FormDataDecodeFilter
def _conv(val):

    ## todo not fully compliant
    val = val.replace("+", " ")

    pos = 0
    while True:
        pos = val.find("%", pos)
        if pos >= 0:
            hex = val[pos + 1 : pos + 3]
            b = int(hex, 16)
            s = chr(b)
            # print(hex,b,s)
            val = val[:pos] + str(s) + val[pos + 3 :]
            pos += 1
        else:
            break
    return val


print()
print("*" * 37)
print("loading file api rest modules!!!")
print("*" * 37)
print()
