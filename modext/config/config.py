
import json
from modext.windup.proc import Namespace

## todo, refactor Namespace
class Config(Namespace):
    
    def __init__(self,fnam):
        
        #Namespace.__init__(self)
        self._fnam = fnam
    
    def load(self):
        
        with open(self._fnam,"r") as f:
            cont = f.read()
            
        cfg = json.loads( cont )
        self.update( cfg )
        
    def save(self):
        
        with open(self._fnam,"w") as f:
            f.write( json.dumps( self ))
    
