
import network

from modcore import modc, Module, LifeCycle


WLAN_CFG = "wlan.cfg"

class WLAN(Module):
        
    def init(self):
        self.last_status = False
    
    def conf(self,config=None):
        super( Module, self ).conf(config)
        self.update()
        
    def update(self):
        try:
            self.last_status = self.wlan.isconnected()
        except:
            self.last_status = False

    def start(self):
        self.wlan_start()
        #self.update()

    def loop(self,config=None,event=None):
        if self.current_level() != LifeCycle.RUNNING:
            return
        status = self.wlan.isconnected()
        if status != self.last_status:
            self.update()
            self.fire_event("wlan", status)

    def stop(self):
        self.wlan_stop()
        #self.update()

    ## deprecated

    def wlan_config(self,ssid,passwd):
        """set wlan ssid and password for automatic connection during startup"""
        wlan_cfg = "\n".join( [ssid, passwd] )
        if passwd == None or len(passwd)<8:
            raise Exception("password too short")
        try:
            with open( WLAN_CFG, "wb" ) as f:
                f.write( wlan_cfg )
        except Exception as ex:
            self.excep( ex, "config" )
            
    def wlan_remove(self):
        """remove wlan info and disable automatic connection during startup"""
        import uos
        self.wlan_stop()
        uos.remove( WLAN_CFG )

    def wlan_start(self,active=True,setntp=True):
        """start wlan if configured before, otherwise do nothing"""
        try:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(False)
        except Exception as ex:
            self.excep( ex, "internal" )
    
        try:        
            with open( WLAN_CFG ) as f:
                content = f.read()
        except:
            return
        
        try:
            credits = list(filter( lambda x : len(x.strip()) > 0, content.split("\n") ))
            
            if active:
                self.wlan.active(active)
                self.wlan.connect(credits[0].strip(), credits[1].strip())
                self.info( "wlan", self.wlan.ifconfig() )
                           
        except Exception as ex:
            self.excep( ex, "start" )

    def wlan_stop(self):
        """disabled wlan, no reconfiguration of prior configuration"""
        if self.wlan:
            self.wlan_start(active=False)

    def ifconfig(self):
        return self.wlan.ifconfig()
    
    
wlan_ap = WLAN("wlan")
modc.add( wlan_ap )
    
