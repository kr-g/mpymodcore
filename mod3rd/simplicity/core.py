"""

work in progress

"""


"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

"""

simplicity templating processor

markup for simplicity.print(context) where context is a dict / Namespace 

{var} -> fill in the var from the context
{!var} text {} -> prints the text until closing brakets '{}' when var is True
{*iter} text {_} {} -> looping, takes the iterator / generator from the context
   and the var _ / {_} in the template contains the iterator value for this loop
   repeating the text until the closing brakets '{}'
   {_i} in the loop contains the loop number index (starts at 0)

\{ and \} in the template escapes curly brakets -> results in '{' and '}'

only simple lookup of variables in dict!!!
everything else must be done by functions in the context.

this to encourage the developer to do 'less' in ui code (even slower in execution!)
and favor to specify an interface to the ui by using the context 

"""

from .conv import simple_esc_html
from modext.windup import Namespace


class _ast(object):
    def __init__(self):
        self.content = None
        self.var = None
        self.children = []


##todo add fiber worker/ yield func so that
##templating can switch fiber worker too


class Simplicity(object):
    def __init__(self, template=None, esc_func=None):
        self.templ = template
        if esc_func == None:
            esc_func = simple_esc_html
        self.esc_func = esc_func
        self.portions = []
        self.ast = []
        if self.templ != None:
            self.parse()
            self.compile()

    def set_template(self, template):
        self.templ = template

    def parse(self):
        # here the parser is more a lexer, like in regex
        while True:
            sec = self._find_sec()
            if sec == -2:
                raise Exception("invalid template")
            if sec == -1:
                self.portions.append(self._unesc(self.templ))
                self.templ = None
                break
            ## todo slice instead of copy
            head = self.templ[: sec[0]]
            if len(head) > 0:
                self.portions.append(self._unesc(head))
            sect = self.templ[sec[0] : sec[1]]
            self.portions.append(sect)
            self.templ = self.templ[sec[1] :]

    def _unesc(self, s):
        return s.replace("\{", "{").replace("\}", "}")

    def compile(self):
        self.ast = self._compile()

    def _compile(self):
        children = []
        while True:
            if len(self.portions) == 0:
                break
            port = self.portions.pop(0)
            ast = _ast()
            if port[0] == "{":
                port = port[1:-1].replace(" ", "")
                if len(port) == 0:
                    return children
                if port[0] in ["!", "*"]:
                    port = port.strip()
                    ast.children = self._compile()
                ast.var = port
            else:
                ast.content = port
            children.append(ast)
        return children

    def print(self, context):
        rc = ""
        for a in self.ast:
            rc += self._print(a, context)
        return rc

    def _print(self, ast, context):
        if ast.content != None:
            return ast.content
        rc = ""
        if ast.var[0] == "!":
            var = ast.var[1:]
            if self._eval(var, context) == True:
                for a in ast.children:
                    rc += str(self._print(a, context))
        elif ast.var[0] == "*":
            var = ast.var[1:]
            iter = self._eval(var, context)
            cnt = 0
            for l in iter:
                for c in ast.children:
                    context["_i"] = cnt
                    context["_"] = l
                    rc += str(self._print(c, context))
                cnt += 1
        else:
            return self._eval(ast.var, context, self.esc_func)
        return rc

    # own implementation due to security and injection scenario
    ## todo follow up
    def _eval(self, var, context, esc_func=None):
        self.templ = var  ##todo replace when using slice (see above)
        sec = self._find_sec(delim="()")
        if sec == -2:
            raise Exception("syntax error")
        if sec == -1:
            val = self._get_attr(context, var)
        else:
            f = var[: sec[0]].strip()
            v = var[sec[0] + 1 : sec[1] - 1].strip()
            f = self._get_attr(context, f)
            v = self._get_attr(context, v)
            val = f(v)
        return self._eval_ret(val, esc_func)

    def _eval_ret(self, val, esc_func=None):
        if type(val) != str:
            return val
        return val if esc_func == None else esc_func(val)

    def _get_attr(self, context, var):
        if type(context) == Namespace:
            # print(">",var, context)
            val = context.get_attr(var)
        else:
            if var in context:
                val = context[var]  # this could be also a func
            else:
                raise Exception("not found", var)
        return val

    def _find_sec(self, delim="{}", pos=0):
        sta = self._find_bound(delim=delim[0], pos=pos)
        if sta < 0:
            return -1
        sto = self._find_bound(delim=delim[1], pos=sta + 1)
        if sto < 0:
            return -2
        return sta, sto + 1

    def _find_bound(self, delim, pos=0):
        while True:
            pos = self.templ.find(delim, pos)
            if pos < 0:
                return -1
            if pos > 0:
                if self.templ[pos - 1] == "\\":
                    pos += 1
                    continue
            return pos
