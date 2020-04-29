
from mod3rd.simplicity import *
from modext.windup import Namespace

        
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


def sample2():
    t = """
    {!var.test}test == true{}
    {*it} index {_i} -> {_}
           {*child.it} sub-iter {_i}
           {}
        back in parent {_i} -> {_}
        
    {}
    """

    smpl = Simplicity( t, esc_func=simple_esc_html )

    def func(x):
        #print(x)
        return int(x)+10

    context = Namespace()
    context["var.test"] = True # autocreate parent variable on the fly !!!
    context["it"] = range(10,30,2)
    context["child"] = {
        "it" : range(1,3),
        }

    print(context)

    print( smpl.print(context) )


#call
#from samples.other3rd.simplicity_sample import sample, sample2
#sample()
    
    
