from modcore.log import logger
from modcore import modc

from modext.windup import Router, StaticFiles

from mod3rd.simplicity import *
from modext.windup import Namespace


router = Router(root="/admin")


@router.get("/generators")
def list_generators(req, args):

    gen = []

    for g in req.windup.generators:
        meta = {
            "type": type(g).__name__,
            # "id" : id(g),
            "xroot": g.xroot,
        }

        if type(g).__name__ in [
            "Router",
            "AuthRouter",
        ]:
            rinfo = []
            for r in g.route:
                route_meta = {
                    "method": r[1],
                    "path": g.root + r[0],
                }
                rinfo.append(route_meta)
            meta["route"] = rinfo

        gen.append(meta)

    req.send_json(gen)
