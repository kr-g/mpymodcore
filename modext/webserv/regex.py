
import re


def xurl_params( url, xpath ):

    def find( s, pos=0 ):
        poss = s.find(":",pos)
        if poss<0:
            return None
        pose = s.find("/",poss+1)
        if pose<0:
            pose = len(s )
        return poss, pose

    sections = []
    names = []

    pos = 0
    pp = 0
    while True:
        p = find(url,pos)
        if p==None:
            break
        p1,p2=p
        names.append( url[p1:p2] )
        sections.append( url[pp:p1] )
        pos=p2+1
        pp=p2
    sections.append( url[pp:] )
        
    regex = "[^/]+"
    xurl = url
    for n in names:
        xurl = xurl.replace( n+"/", regex+"/" )
       
    regex = re.compile( xurl )
    m = regex.match( xpath )
    
    if m:
        values = []
        for i in range( 0, len(sections)-1):
            sec = sections[i]
            xpath = xpath[len(sec):]
            pos = xpath.find( sections[i+1] )
            val = xpath[:pos]
            values.append( val )
            xpath = xpath[len(val):]
            
        if len(sections)>0:
            val = xpath[len(sections[-1]):]
            values.append( val )
        
        params = dict(zip( map( lambda x : x[1:], names), values ))
        
        return params


    
