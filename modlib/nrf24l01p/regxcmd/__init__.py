
from const import *
from cmd import Command, RegRead, RegWrite

class RegUpdate(Command):

    def __init__(self,trans=None):
        self._trans = trans
        super().__init__()
        
    def trans(self,val):
        if self.trans != None:
            return self.trans(self,val)
        return val

    def exe( self, hal ):
        rc = hal.exe( RegRead( self.reg_adr() ) )
        val = rc[1]
        #print( "before", val )
        val = self.trans( val )
        #print( "after", val )
        rc = hal.exe( RegWrite( self.reg_adr(), val ) )
        return rc
