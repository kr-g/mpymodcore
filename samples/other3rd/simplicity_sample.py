
from mod3rd.simplicity import *

        
##todo? when an orphan closing braket is not escaped it works too!
##since skipped whilst searching for next opening braket

def sample():
    t = """
    \{->{var}<-\}
    {!test} 
        howdy
    {}{*it}index {_i}: {_} + 10 = {func(_)}
    {*s_it}   sub iter {_}
    {}  back from sub iter, restored val {_} and index {_i}
    {}
    some text here
    }<-orphan closing bracket
    """

    smpl = Simplicity( t, esc_func=simple_esc_html )

    def func(x):
        #print(x)
        return int(x)+10

    ctx = { "test": not True, "var" : "'hello&world'", "it" : range(10,30,2), \
            "func" : func, "s_it" : range(1,3) }

    print( smpl.print(ctx) )

#call
#from samples.other3rd.simplicity_sample import sample
#sample()
    
    
