"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import time

from modcore.log import LogSupport
from .proc import Namespace
from .filter import Filter


SID = "xsession_id"
EXPIRES = "xsession_expires"
CREATED = "xsession_created"
TIMEOUT = 60 * 30


class SessionLoad(Filter):
    def __init__(self, session_store, cleanup=None):
        Filter.__init__(self, cleanup=cleanup)
        self.session_store = session_store

    def filterRequest(self, request):

        coky = self.session_store.cookie_name

        created = False

        if request.xcookies == None:
            request.xcookies = {}

        sid = request.xcookies.get(coky)

        if sid == None:
            created = True
            sid = self.session_store.create()

        sess = self.session_store.load(sid)

        if sess == None:
            created = True
            sid = self.session_store.create()
            sess = self.session_store.load(sid)

        if created:
            request.xcookies[coky] = sess

        request.xsession_cookie = self.session_store.cookie_name
        request.xsession_is_new = created
        request.xsession_id = sid
        request.xsession = sess

        xargs = request.xargs
        xargs.set_attr("session", request.xsession)

        self.info("sid", request.xsession_id, "created", request.xsession_is_new)

        # untested
        if self.cleanup:
            del sess[SID]
            del sess[EXPIRES]


class SessionSave(Filter):
    def __init__(self, session_store, cleanup=None):
        Filter.__init__(self, cleanup=cleanup)
        self.session_store = session_store

    def filterRequest(self, request):

        xargs = request.xargs
        self.info("xargs", xargs)

        if (
            request.xsession == None
            or ("session" not in xargs)
            or xargs.session == None
        ):
            if request.xsession_id != None:
                self.session_store.destroy(request.xsession_id)
        else:
            self.session_store.store(request.xsession_id, request.xsession)

        self.info("sid", request.xsession_id)


class SessionStore(LogSupport):
    def __init__(self, cookie_name="sessionid", expires_after=TIMEOUT, cleanup=None):
        LogSupport.__init__(self)
        self.cookie_name = cookie_name
        self.expires_after = expires_after
        self.sessions = {}
        self.cleanup = cleanup

    def _create_id(self):
        sessionid = (
            str(time.ticks_us())
            + "_"
            + str(time.ticks_cpu())
            + "_"
            + str(time.ticks_ms())
        )
        return sessionid

    def renew(self, session):
        self.info("renew")
        exp = time.ticks_add(time.ticks_ms(), self.expires_after * 1000)
        session.update({EXPIRES: exp})

    def create(self):
        while True:
            sid = self._create_id()
            if sid not in self.sessions:
                break
            self.warn("ups...")

        self.info("create", sid)

        session = Namespace()
        session.update({SID: sid, CREATED: time.time()})
        self.renew(session)
        self.sessions[sid] = session

        return sid

    def is_expired(self, session):
        sid = session.get(SID, None)
        exp = session.get(EXPIRES, 0)
        now = time.ticks_ms()
        self.info(now, exp)
        diff = time.ticks_diff(exp, now)
        expired = diff < 0
        if expired:
            self.info("expired", sid, exp, now, diff)
        return expired

    def purge_expired(self):
        for sid in self.sessions.keys():
            session = self.sessions.get(sid)
            if self.is_expired(session):
                self.destroy(sid)

    def load(self, sid):
        self.info("load", sid)
        session = self.sessions.get(sid, None)
        self.info("session", session)
        if session == None:
            return
        if self.is_expired(session):
            self.destroy(sid)
            return
        self.renew(session)
        return session

    def store(self, sid, session):
        self.info("store", sid)
        session = self.sessions.get(sid, None)
        if session == None:
            return
        self.sessions[sid] = session

    def destroy(self, sid):
        self.info("destroy", sid)
        session = self.sessions.get(sid, None)
        if session == None:
            return
        del self.sessions[sid]

    def pre_filter(self):
        return SessionLoad(self, cleanup=self.cleanup)

    def post_filter(self):
        return SessionSave(self, cleanup=self.cleanup)


store = SessionStore()


def purge_expired():
    store.purge_expired()
