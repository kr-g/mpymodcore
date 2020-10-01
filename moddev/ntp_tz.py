
import time


class tz_mez(object):
    
    def __init__(self):
        n = time.time()
        tn = time.localtime( n )       
        year_tm = (tn[0], 0, 0, 0, 0, 0, 0, 0)
        
        summer = self._patch( year_tm, self._summer_start() )
        winter = self._patch( year_tm, self._winter_start() )
        
        self.summer_tm = self._find_last_sunday( summer )
        self.winter_tm = self._find_last_sunday( winter )
        
        self.summer = time.mktime( self.summer_tm )
        self.winter = time.mktime( self.winter_tm )
    
    def _patch(self,tm,tp):
        tm = list(tm)
        for i in range(0,3):
            tm[i+1] = tp[i]
        return tm
        
    def _summer_start(self):
        # 31 march, 1am utc
        return 3,31,1
    
    def _winter_start(self):
        # 31 oct, 1am utc
        return 10,31,1

    def _find_last_sunday( self, t ):
        tm = list(time.localtime( time.mktime(t) ))
        dow = tm[6]
        if dow != 6:
            tm[2] -= dow+1
            tm[6] = 6
        return tm

    def __repr__(self):
        return {
            "now_utc" : time.time(),
            "summer" : self.summer,
            "summer_tm" : self.summer_tm,
            "winter" : self.winter,
            "winter_tm" : self.winter_tm,
            }
    
    