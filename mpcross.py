
"""

    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE

"""
"""

compile the project with mpcross
- compile target folder {proj_folder}/mpy/...
- checks for date/time which py file has changed
- writes delta information to compile.txt

remark: 
- mpcross is not included, refer to micropython github,
  and homepage on how to setup the environment
- to find the proper byte code version use check_mpy.py
  (also in this folder)


call to execute:

compile_all()

"""

import os
import sys
import glob
import time


MPYCROSS = os.environ.setdefault( "MPY_CROSS" , "../micropython/mpy-cross/mpy-cross" )

forceCompile = os.environ.setdefault( "MPY_FORCE_COMPILE", "False" ).lower() == "true"


def get_src_dest( fnam, dest_dir ):
    p = os.path.dirname( fnam )
    f = os.path.basename( fnam )
    nam, ext = os.path.splitext( f )
    f1 = os.path.join( p, f )
    f2 = os.path.join( dest_dir, p, f"{nam}.mpy" )
    return f1, f2    

def check_compile( fnam, dest_dir ):

    if forceCompile:
        return True
    
    f1,f2 = get_src_dest( fnam, dest_dir )
    #print(f1,f2)
    
    try:
        m1 = os.stat( f1 ).st_mtime
        m2 = os.stat( f2 ).st_mtime
        needcompile = m1 > m2
    except:
        needcompile = True

    return needcompile

def ensure_dest_dir( fnam ):
    dir = os.path.dirname( fnam )
    os.makedirs( dir, exist_ok=True )

def compile_file( fnam, dest_dir ):
    print( "compile", fnam )
    f1,f2 = get_src_dest( fnam, dest_dir )
    ensure_dest_dir( f2 )
    cmd = f"{MPYCROSS} {f1} -o {f2}"
    print( cmd )
    rc = os.system( cmd )
    if rc > 0:
        print( "err", rc )
        exit(rc)

def get_all():
    files = glob.glob( "**/**.py", recursive=True )
    files = filter( lambda x : not x.startswith("build/"), files )
    return files


dest_dir = "./mpy/"

def compile_delta():
    files = get_all()
    compiled = []
    for f in files:
        if f in ["mpcross.py","check_mpy.py","boot.py","setup.py","webrepl_cfg.py",]:
            continue
        if check_compile( f, dest_dir ):
            compile_file( f, dest_dir )
            compiled.append(f)
        else:
            print("up to date", f )
    return compiled


# call this

def compile_all():
    files = compile_delta()
    with open( "compile.txt" ,"a" ) as f:
        print("-"*37, file=f)
        print(time.asctime(time.localtime(time.time())), file=f)
        print("-"*37, file=f)
        for fnam in files:
            print(fnam, file=f)
        

if __name__=='__main__':
    compile_all()
    
    
        
