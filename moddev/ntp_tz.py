
import time

# https://en.wikipedia.org/wiki/Central_European_Time
# https://en.wikipedia.org/wiki/Daylight_saving_time

class tz_cet(object):
    
    def __init__(self):
        n = self._utc_time()
        tn = time.localtime( n )       
        year_tm = (tn[0], 0, 0, 0, 0, 0, 0, 0)
        
        summer = self._patch( year_tm, self._summer_start() )
        winter = self._patch( year_tm, self._winter_start() )
        
        self.summer_tm = self._find_last_sunday( summer )
        self.winter_tm = self._find_last_sunday( winter )
        
        self.summer = time.mktime( self.summer_tm )
        self.winter = time.mktime( self.winter_tm )
    
    def _utc_time(self):
        return time.time()
    
    def _patch(self,tm,tp):
        tm = list(tm)
        for i in range(0,3):
            tm[i+1] = tp[i]
        return tm
        
    def _find_last_sunday( self, t ):
        # this is official across europe
        # refer wiki article above
        tm = list(time.localtime( time.mktime(t) ))
        dow = tm[6]
        if dow != 6:
            tm[2] -= dow+1
            tm[6] = 6
        return tm

    def get_current_tz(self):
        n = self._utc_time()
        offset = self._utc_tz_offset()
        if n >= self.summer and n < self.winter:
            offset += self._summer_tz_offset()
        return offset

    def _summer_start(self):
        # 31 march, 1am utc
        return 3,31,1
    
    def _winter_start(self):
        # 31 oct, 1am utc
        return 10,31,1

    def _utc_tz_offset(self):
        # berlin, rome, warsaw
        return 3600
    
    def _summer_tz_offset(self):
        return 3600

    def __repr__(self):
        
        now = time.time()
        offset = self.get_current_tz()
        
        return {
            "now_utc" : now,
            "now_utc_tm" : time.localtime(now),
            "tz_offset" : offset,
            "now_tz_tm" : time.localtime( now + offset ),
            "summer" : self.summer,
            "summer_tm" : self.summer_tm,
            "winter" : self.winter,
            "winter_tm" : self.winter_tm,
            }
    
    