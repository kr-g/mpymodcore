
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import hashlib
import binascii

from modcore.log import LogSupport
from modext.windup.proc import Namespace


class Authentication(LogSupport):
    
    def __init__( self, basedir ):
        LogSupport.__init__(self)
        self.basedir = basedir

    def save_user_password( self, username, password_plain ):
        with open( basedir + username +".pwd.txt", "w" ) as f:
            hash = hash_password( password_plain )
            print( hash, file= f )

    def save_user_goups( self, username, groups ):
        with open( basedir + username +".grp.txt", "w" ) as f:
            joined = ":".join(groups)
            print( joined, file= f )

    def _get_prop( self, user, prop, ext ):
        try:
            fnam = self.basedir + user.name +ext+".txt"
            self.info( "loading", fnam )
            with open( fnam, "r" ) as f:
                lines = f.readlines()
                lines = list(filter( lambda x : len(x.strip())>0, lines))
                user[prop] = lines[0]                                
        except Exception as ex:
            self.excep( ex )
            self.warn("user",user.name,"not found")
        return user
        
    def _get_password( self, user ):
        self._get_prop( user, "password", ".pwd" )
        
    def _get_groups( self, user ):
        self._get_prop( user, "groups", ".grp" )
        try:
            user.groups = list(filter( lambda x : len(x.strip().lower())>0, user.groups.split(":") ))
        except:
            pass     

    def check_password( self, user, password_plain ):        
        hash = hash_password( password_plain )
        try:
            return user.password == hash
        except:
            return False
        finally:
            del user.password
       
    def find_user( self, username ):
        user = Namespace()
        user["name"] = username.lower()
        self._get_password(user)
        self._get_groups(user)
        return user
       
    def check_group( self, user, groups ):
        self.info( "checking", user, groups )
        for g in user.groups:
            if g in groups:
                return True


def create_store(basedir="/etc/shadow/"):
    return Authentication(basedir)

def hash_password(password_plain):
    h = hashlib.sha256()
    h.update(password_plain)
    hash = binascii.hexlify( h.digest() )
    return hash.decode()


security_store = create_store()

