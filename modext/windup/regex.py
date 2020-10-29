"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import re

## todo
##
def xurl_params(url, xpath):
    def find(s, pos=0):
        poss = s.find(":", pos)
        if poss < 0:
            return None
        pose = s.find("/", poss + 1)
        if pose < 0:
            pose = len(s)
        return poss, pose

    sections = []
    names = []

    pos = 0
    pp = 0
    while True:
        p = find(url, pos)
        if p == None:
            break
        p1, p2 = p
        names.append(url[p1:p2])
        sections.append(url[pp:p1])
        pos = p2 + 1
        pp = p2
    if len(url[pp:]) > 0:
        sections.append(url[pp:])

    # print(sections,names)

    regex = "[^/]+"
    xurl = url
    for n in names:
        xurl = xurl.replace(n + "/", regex + "/")

    xurl = xurl.replace(names[-1], regex)

    # print(xurl)

    regex = re.compile(xurl)
    m = regex.match(xpath)

    if m:
        values = []
        for i in range(0, len(sections) - 1):
            sec = sections[i]
            xpath = xpath[len(sec) :]
            pos = xpath.find(sections[i + 1])
            val = xpath[:pos]
            values.append(val)
            xpath = xpath[len(val) :]
            # print(i,sec,sections[i+1], pos, val, xpath)

        if len(sections) > 0:
            val = xpath[len(sections[-1]) :]
            values.append(val)

        # print( names, values )

        params = dict(zip(map(lambda x: x[1:], names), values))

        return params


"""    
print( xurl_params( "/user/:user/id/:userid/end", "/user/john/id/24325/end" ))
print( xurl_params( "/user/:user/id/ii/:userid", "/user/john/id/ii/24325" ))
print( xurl_params( "/:user/id/:userid", "/john/id/24325" ))
"""
