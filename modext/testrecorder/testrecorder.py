
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import os
import sys


__test_ids = {}
__test_id_cnt = 0

def _reset():
    global __test_ids
    global __test_id_cnt 
    __test_ids = {}
    __test_id_cnt = 0
 
#
# use this to create trackable id() based identifiers,
# see example at the end of this file
#

def tid(obj):
    global __test_ids
    global __test_id_cnt 
    oid = id(obj)
    rid = None
    if oid in __test_ids:
        rid = __test_ids[oid]
    else:
        __test_id_cnt += 1
        rid = __test_id_cnt
        __test_ids[oid]=__test_id_cnt
    return "{testid:"+str(rid)+"}"


class TestRecorder(object):
    
    # the folder MUST exist, no automatic creation!
    dest_dir = "~/testrecorder/"
    fallback_dir = "./"
    
    # testname: defaults to "default" if not specified
    # record
    # - True: recording the test output in of testname.trec.txt 
    # - False: capturing test output in testname.trun.txt and check against testname.trec.txt
    #
    # nil: True for ignore everything
    # reset: reset internal counter and obj cache
    
    def __init__(self,testname=None,record=False,nil=False,dest_dir=None,reset=True):
        
        if reset:
            _reset()
        
        if dest_dir==None:
            dest_dir = TestRecorder.dest_dir
        
        if dest_dir.find("~")==0:
            try:
                dest_dir = os.path.expanduser(dest_dir)
            except:
                print("no user path expanded")
                dest_dir = dest_dir.replace("~",TestRecorder.fallback_dir)
            
        if testname==None or len(testname.strip())==0:
            testname="default"
        
        self.testname = testname
        self.dest_dir = dest_dir
        
        self.fnam_record = dest_dir+testname+".trec.txt"
        self.fnam_run = dest_dir+testname+".trun.txt"
        
        self.record = record
        self.nil = nil
                
        if self.record:
            try:
                os.remove( self.fnam_record )
            except:
                pass
        try:
            os.remove( self.fnam_run )
        except:
            pass
        
        self.open_platform_specific()
        
    # platform specific handling
        
    def open_platform_specific(self):
        ## todo -> dupterm, problem. will not work because eg thonny
        ## todo -> unix port plus mocking
        # fails on micropython
        self.stdout = sys.stdout
        
        # this will redirect all output to self.write 
        sys.stdout = self
      
    def close_platform_specific(self):
        ## todo
        # this will fail on micropython
        sys.stdout = sys.__stdout__

    # end of platform specific handling

    def write(self,by):
        if not self.nil:
            if self.record:
                with open( self.fnam_record, "a+" ) as f:
                    f.write(by)
            else:
                with open( self.fnam_run, "a+" ) as f:
                    f.write(by)
            
        return print( by, file=self.stdout, end="" )
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        
        self.close_platform_specific()
            
        if exc_type==None:
            self._assert()
 
    def _assert(self):
        if not self.record and not self.nil:
            with open( self.fnam_record  ) as f:
                tr = f.readlines()
            with open( self.fnam_run  ) as f:
                trun = f.readlines()
            cnt = 1
            while True:
                if len(tr)==0:
                    break
                t1 = tr.pop(0)
                if len(trun)==0:
                    raise Exception( self.__class__.__name__,  "failed, missing line", cnt )
                t2 = trun.pop(0)
                if t1!=t2:
                    raise Exception( self.__class__.__name__,  "failed, line", cnt )
                cnt+=1
            if len(trun)>0:
                raise Exception( self.__class__.__name__,  "failed, overflow line", cnt )

            print("-"*37)
            print( self.__class__.__name__, "test ok [" + self.testname +"]")
            print("-"*37)


def sample():

    print()
    print("*** testing TestRecorder itself ***" )
    print()    
    
    nil = False

    testnam = "testrecorder"

    # ignore this since already in git
    if False:
        # no name, or blank name default to 'default'
        # create the recording
        with TestRecorder(testnam,record=True,nil=nil, dest_dir = "./") as tr:
            print("test recorder beispiel", tid(tr))
            print("one line")
        
    # check against recording, this will result in ok
    with TestRecorder(testnam,record=False,nil=nil, dest_dir = "./") as tr:
        print("test recorder beispiel", tid(tr))
        print("one line")
    
    print()
    print("--- from here onwards only fails ---" )
    print()
    
    try:
        # check against recording, this will fail
        with TestRecorder(testnam,record=False,nil=nil, dest_dir = "./") as tr:
            print("test recorder beispiel", tid(tr))
            # missing line here
    except Exception as ex:
        print(ex)
    
    try:
        # check against recording, this will fail
        with TestRecorder(testnam,record=False,nil=nil, dest_dir = "./") as tr:
            # additional text
            print("test recorder beispiel", tid(tr)+"stupid")
            print("one line")
    except Exception as ex:
        print(ex)
    
    try:
        # print one additional line, this will result in exception
        with TestRecorder(testnam,record=False,nil=nil, dest_dir = "./") as tr:
            print("test recorder beispiel", tid(tr))
            print("one line")
            # one more line
            print("bullshit")
    except Exception as ex:
        print(ex)
   
    
if __name__=='__main__':

    sample()
    
    
    