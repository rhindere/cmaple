"""implement the parser for pyexpander.
"""
import bisect
import re

__version__= "1.8.4" #VERSION#

# pylint: disable= invalid-name

# we use '\n' as line separator and rely on python's built in line end
# conversion to '\n' on all platforms.
# You may howver, use change_linesep() to change the line separator.

LINESEP= "\n"
LINESEP_LEN= len(LINESEP)

def change_linesep(sep):
    """change line separator, this is here just for tests.
    """
    # pylint: disable= global-statement
    global LINESEP, LINESEP_LEN
    LINESEP= sep
    LINESEP_LEN= len(sep)

class IndexedString(object):
    """a string together with row column information.

    Here is an example:

    >>> txt='''01234
    ... 67
    ... 9abcd'''
    >>> l=IndexedString(txt)
    >>> l.rowcol(0)
    (1, 1)
    >>> l.rowcol(1)
    (1, 2)
    >>> l.rowcol(4)
    (1, 5)
    >>> l.rowcol(5)
    (1, 6)
    >>> l.rowcol(6)
    (2, 1)
    >>> l.rowcol(7)
    (2, 2)
    >>> l.rowcol(8)
    (2, 3)
    >>> l.rowcol(9)
    (3, 1)
    >>> l.rowcol(13)
    (3, 5)
    >>> l.rowcol(14)
    (3, 6)
    >>> l.rowcol(16)
    (3, 8)
    """
    # pylint: disable= too-few-public-methods
    def __init__(self, st):
        self._st=st
        self._lines=None
        self._positions=None
    def _list(self):
        """calculate and remember positions where lines begin."""
        l= len(self._st)
        pos=0
        self._lines=[1]
        self._positions=[0]
        lineno=1
        while True:
            # look for the standard lineseparator in the string:
            p= self._st.find(LINESEP, pos)
            if p<0:
                # not found
                break
            pos= p+LINESEP_LEN
            if pos>=l:
                break
            lineno+=1
            self._lines.append(lineno)
            self._positions.append(pos)
    def rowcol(self,pos):
        """calculate (row,column) from a string position."""
        if self._lines is None:
            self._list()
        idx= bisect.bisect_right(self._positions, pos)-1
        off= self._positions[idx]
        return(self._lines[idx], pos-off+1)
    def st(self):
        """return the raw string."""
        return self._st
    def __str__(self):
        return "IndexedString(...)"
    def __repr__(self):
        # Note: if repr(some object) gets too long since
        # repr(IndexedString(..)) basically prints the whole input file
        # you may in-comment the following line in order to make
        # the output shorter:
        #return "IndexedString(...)"
        return "IndexedString(%s)" % repr(self._st)

class ParseException(Exception):
    """used for Exceptions in this module."""
    def __init__(self, value, pos=None, rowcol=None):
        super(ParseException, self).__init__(value, pos, rowcol)
        self.value = value
        self.pos= pos
        self.rowcol= rowcol
    def __str__(self):
        if self.rowcol is not None:
            return "%s line %d, col %d" % \
                   (self.value,self.rowcol[0],self.rowcol[1])
        elif self.pos is not None:
            return "%s position: %d" % (self.value,self.pos)
        return "%s" % self.value

rx_pyIdent= re.compile(r'([A-Za-z_][\w\.]*)$')

rx_csv=re.compile(r'\s*,\s*')

def scanPyIdentList(st):
    """scan a list of python identifiers.

    Here are some examples:

    >>> scanPyIdentList("a,b")
    ['a', 'b']
    >>> scanPyIdentList("a,b.d, c")
    ['a', 'b.d', 'c']
    >>> scanPyIdentList("a,b.d, c&")
    Traceback (most recent call last):
        ...
    ParseException: list of python identifiers expected
    """
    lst= re.split(rx_csv, st)
    for elm in lst:
        m= rx_pyIdent.match(elm)
        if m is None:
            raise ParseException("list of python identifiers expected")
    return lst

rx_py_in= re.compile(r'^\s*(.*?)\s*\b(in)\b\s*(.*?)\s*$')
def scanPyIn(st):
    """scan a python "in" statement.

    Here are some examples:

    >>> scanPyIn(" (a,b) in k.items() ")
    ('(a,b)', 'in', 'k.items()')
    """
    m= rx_py_in.match(st)
    if m is None:
        raise ParseException("python \"in\" expression expected")
    return m.groups()

rx_bracketed= re.compile(r'\{[A-Za-z_]\w*\}')

def parseBracketed(idxst,pos):
    """parse an identifier in curly brackets.

    Here are some examples:

    >>> def test(st,pos):
    ...     idxst= IndexedString(st)
    ...     (a,b)= parseBracketed(idxst,pos)
    ...     print(st[a:b])
    ...
    >>> test(r'{abc}',0)
    {abc}
    >>> test(r'{ab8c}',0)
    {ab8c}
    >>> test(r'{c}',0)
    {c}
    >>> test(r'{}',0)
    Traceback (most recent call last):
        ...
    ParseException: command enclosed in curly brackets at line 1, col 1
    >>> test(r'{abc',0)
    Traceback (most recent call last):
        ...
    ParseException: command enclosed in curly brackets at line 1, col 1
    >>> test(r'x{ab8c}',1)
    {ab8c}
    """
    if not isinstance(idxst, IndexedString):
        raise TypeError("idxst par wrong: %s" % repr(idxst))
    st= idxst.st()
    m= rx_bracketed.match(st,pos)
    if m is None:
        raise ParseException("command enclosed in curly brackets at",
                             rowcol= idxst.rowcol(pos))
    return(pos,m.end())

rx_StringLiteralStart= re.compile(r'''(UR|Ur|uR|ur|r|u|R|U|)("""|''' + \
                                  """'''""" + \
                                  r'''|'|")''')
def parseStringLiteral(idxst,pos):
    r"""parse a python string literal.

    returns 2 numbers, the index where the string starts and
    the index of the first character *after* the string

    Here are some examples:

    >>> def test(st,pos):
    ...     idxst= IndexedString(st)
    ...     (a,b)= parseStringLiteral(idxst,pos)
    ...     print(st[a:b])
    ...

    >>> test(r'''"abc"''',0)
    "abc"

    >>> test("'''ab'c'd'''",0)
    '''ab'c'd'''
    >>> test("'''ab'cd''''",0)
    '''ab'cd'''

    >>> test(r'''U"abc"''',0)
    U"abc"
    >>> test(r'''xU"abc"''',1)
    U"abc"
    >>> test(r'''xUr"abc"''',1)
    Ur"abc"

    >>> test(r'''xUr"ab\\"c"''',1)
    Ur"ab\\"

    >>> test(r'''xUr"ab\"c"''',1)
    Ur"ab\"c"
    >>> test(r'''xUr"ab\"c"''',0)
    Traceback (most recent call last):
        ...
    ParseException: start of string expected at line 1, col 1
    >>> test(r'''"ab''',0)
    Traceback (most recent call last):
        ...
    ParseException: end of string not found at line 1, col 1
    >>> test(r"'''ab'",0)
    Traceback (most recent call last):
        ...
    ParseException: end of string not found at line 1, col 1
    >>> test(r'''"ab\"''',0)
    Traceback (most recent call last):
        ...
    ParseException: end of string not found at line 1, col 1
    """
    if not isinstance(idxst, IndexedString):
        raise TypeError("idxst par wrong: %s" % repr(idxst))
    st= idxst.st()
    m= rx_StringLiteralStart.match(st,pos)
    if m is None:
        raise ParseException("start of string expected at",
                             rowcol= idxst.rowcol(pos))
    prefix= m.group(1)
    starter= m.group(2) # """ or ''' or " or '
    #is_unicode= False
    #is_raw= False
    #if -1!=prefix.find("r"):
    #    is_raw= True
    #elif -1!=prefix.find("R"):
    #    is_raw= True
    #if -1!=prefix.find("u"):
    #    is_unicode= True
    #elif -1!=prefix.find("U"):
    #    is_unicode= True
    startpos= pos+len(prefix)+len(starter)
    while True:
        idx= st.find(starter, startpos)
        # if startpos>len(st), idx is also -1
        if idx==-1:
            raise ParseException("end of string not found at",
                                 rowcol= idxst.rowcol(pos))
        if st[idx-1]=="\\":
            # maybe escaped quote char
            e= None
            try:
                if st[idx-2]!="\\":
                    # only then it is an escaped quote char
                    startpos= idx+1
                    continue
            except IndexError as _e:
                e= _e
            if e is not None:
                raise ParseException("end of string not found at",
                                     rowcol= idxst.rowcol(pos))
        break
    if len(starter)==1:
        # simple single quoted string
        return(pos,idx+1)
    return(pos,idx+3)

def parseComment(idxst,pos):
    r"""parse a python comment.

    Here are some examples:

    >>> import os
    >>> def test(st,pos,sep=None):
    ...     if sep:
    ...         change_linesep(sep)
    ...     idxst= IndexedString(st)
    ...     (a,b)= parseComment(idxst,pos)
    ...     print(repr(st[a:b]))
    ...     change_linesep(os.linesep)
    ...
    >>> test("#abc",0)
    '#abc'
    >>> test("#abc\nef",0,"\n")
    '#abc\n'
    >>> test("#abc\r\nef",0,"\r\n")
    '#abc\r\n'
    >>> test("xy#abc",2)
    '#abc'
    >>> test("xy#abc\nef",2,"\n")
    '#abc\n'
    >>> test("xy#abc\nef",3)
    Traceback (most recent call last):
        ...
    ParseException: start of comment not found at line 1, col 4
    """
    if not isinstance(idxst, IndexedString):
        raise TypeError("idxst par wrong: %s" % repr(idxst))
    st= idxst.st()
    if st[pos]!="#":
        raise ParseException("start of comment not found at",
                             rowcol= idxst.rowcol(pos))
    idx_lf= st.find(LINESEP,pos+1)
    if idx_lf==-1:
        return(pos, len(st))
    return(pos,idx_lf+LINESEP_LEN)

rx_CodePart= re.compile(r'''((?:UR|Ur|uR|ur|r|u|R|U|)(?:"""|''' + """'''""" + \
                        r'''|'|")|#|\(|\))''')
def parseCode(idxst,pos):
    r"""parse python code, it MUST start with a '('.

    Here are some examples:

    >>> def test(st,pos):
    ...     idxst= IndexedString(st)
    ...     (a,b)= parseCode(idxst,pos)
    ...     print(st[a:b])
    ...
    >>> test(r'(a+b)',0)
    (a+b)
    >>> test(r'(a+(b*c))',0)
    (a+(b*c))
    >>> test(r'(a+(b*c)+")")',0)
    (a+(b*c)+")")
    >>> test(r"(a+(b*c)+''')''')",0)
    (a+(b*c)+''')''')
    >>> test(r"(a+(b*c)+''')'''+# comment )\n)",0)
    Traceback (most recent call last):
        ...
    ParseException: end of bracket expression not found at line 1, col 1
    >>>
    >>> test("(a+(b*c)+''')'''+# comment )\n)",0)
    (a+(b*c)+''')'''+# comment )
    )
    """
    if not isinstance(idxst, IndexedString):
        raise TypeError("idxst par wrong: %s" % repr(idxst))
    st= idxst.st()
    if st[pos]!="(":
        raise ParseException("start of bracket expression not found at",
                             rowcol= idxst.rowcol(pos))
    startpos= pos+1
    while True:
        m= rx_CodePart.search(st, startpos)
        if m is None:
            raise ParseException("end of bracket expression not found at",
                                 rowcol= idxst.rowcol(pos))
        matched= m.group(1)
        if matched=="#":
            # a comment
            (_,b)= parseComment(idxst, m.start())
            startpos= b
            continue
        if matched=="(":
            # an inner bracket
            (_,b)= parseCode(idxst, m.start())
            startpos= b
            continue
        if matched==")":
            return(pos,m.start()+1)
        # from here it must be a string literal
        (_,b)= parseStringLiteral(idxst, m.start())
        startpos= b
        continue

class ParsedItem(object):
    """base class of parsed items."""
    def __init__(self, idxst, start, end):
        if not isinstance(idxst, IndexedString):
            raise TypeError("idxst par wrong: %s" % repr(idxst))
        self._idxst= idxst
        self._start= start
        self._end= end
    def string(self):
        """return the string that represents the ParsedItem."""
        return self._idxst.st()[self._start:self._end+1]
    def start(self):
        """return the start of the ParsedItem in the source string."""
        return self._start
    def end(self):
        """return the end of the ParsedItem in the source string."""
        return self._end
    def rowcol(self, pos= None):
        """calculate (row,column) from a string position."""
        if pos is None:
            pos= self.start()
        return self._idxst.rowcol(pos)
    def positions(self):
        """return start and end of ParsedItem in the source string."""
        return "(%d, %d)" % (self._start, self._end)
    def __str__(self):
        return "('%s', %s, %s)" % (self.__class__.__name__, \
               self.positions(), repr(self.string()))
    def __repr__(self):
        return "%s(%s, %s, %s)" % (self.__class__.__name__, \
                repr(self._idxst), repr(self._start), repr(self._end))

class ParsedLiteral(ParsedItem):
    """class of a parsed literal.

    A literal is a substring in the input that shouldn't be modified by
    pyexpander.
    """
    def __init__(self, idxst, start, end):
        ParsedItem.__init__(self, idxst, start, end)

class ParsedComment(ParsedItem):
    """class of a parsed comment.

    A comment in pyexpander starts with '$#'.
    """
    def __init__(self, idxst, start, end):
        ParsedItem.__init__(self, idxst, start, end)

class ParsedVar(ParsedItem):
    """class of a parsed variable.

    A variable in pyexpander has the form "$(identifier)".
    """
    def __init__(self, idxst, start, end):
        ParsedItem.__init__(self, idxst, start, end)

class ParsedEval(ParsedItem):
    """class of an pyexpander expression.

    A pyexpander expression has the form "$(expression)" e.g. "$(a+1)". This is
    different from ParsedVar where the string within the brackets is a simple
    identifier.
    """
    def __init__(self, idxst, start, end):
        ParsedItem.__init__(self, idxst, start, end)

class ParsedPureCommand(ParsedItem):
    """class of a pyexpander command without arguments.

    A pure command has the form "$name". Such a command has no arguments which
    would be enclosed in round brackets immediately following the name.
    """
    def __init__(self, idxst, start, end):
        ParsedItem.__init__(self, idxst, start, end)

class ParsedCommand(ParsedItem):
    """class of a pyexpander command with arguments.

    A command has the form "$name(argument1, argument2, ...)".
    """
    def __init__(self, idxst, start, end, ident):
        ParsedItem.__init__(self, idxst, start, end)
        self.ident= ident
    def args(self):
        """return the arguments of the command."""
        return self.string()
    def __str__(self):
        return "('%s', %s, %s, %s)" % (self.__class__.__name__, \
               self.positions(), repr(self.string()), \
               repr(self.ident))
    def __repr__(self):
        return "%s(%s, %s, %s, %s)" % (self.__class__.__name__, \
                repr(self._idxst), repr(self._start), repr(self._end), \
                repr(self.ident))


rx_DollarFollows= re.compile(r'([A-Za-z_]\w*|\(|\{|#)')

def parseDollar(idxst, pos):
    r"""parse things that follow a dollar.

    Here are some examples:

    >>> def test(st,pos):
    ...   idxst= IndexedString(st)
    ...   (p,elm)= parseDollar(idxst,pos)
    ...   print("Parsed: %s" % elm)
    ...   print("rest of string:%s" % st[p:])
    ...
    >>> test("$abc",0)
    Parsed: ('ParsedPureCommand', (1, 3), 'abc')
    rest of string:
    >>> test("$abc%&/",0)
    Parsed: ('ParsedPureCommand', (1, 3), 'abc')
    rest of string:%&/
    >>> test("$abc(2*3)",0)
    Parsed: ('ParsedCommand', (5, 7), '2*3', 'abc')
    rest of string:
    >>> test(" $abc(2*sin(x))",1)
    Parsed: ('ParsedCommand', (6, 13), '2*sin(x)', 'abc')
    rest of string:
    >>> test(" $abc(2*sin(x))bn",1)
    Parsed: ('ParsedCommand', (6, 13), '2*sin(x)', 'abc')
    rest of string:bn
    >>> test(" $# a comment\nnew line",1)
    Parsed: ('ParsedComment', (3, 13), ' a comment\n')
    rest of string:new line
    >>> test("$(abc)",0)
    Parsed: ('ParsedVar', (2, 4), 'abc')
    rest of string:
    >>> test("$(abc*2)",0)
    Parsed: ('ParsedEval', (2, 6), 'abc*2')
    rest of string:
    >>> test(" $(2*x(y))abc",1)
    Parsed: ('ParsedEval', (3, 8), '2*x(y)')
    rest of string:abc
    """
    if not isinstance(idxst, IndexedString):
        raise TypeError("idxst par wrong: %s" % repr(idxst))
    st= idxst.st()
    if st[pos]!="$":
        raise ParseException("'$' expected at",
                             rowcol= idxst.rowcol(pos))
    m= rx_DollarFollows.match(st, pos+1)
    if m is None:
        raise ParseException("unexpected characters after '$' at",
                             rowcol= idxst.rowcol(pos))
    matched= m.group(1)
    if matched=="#":
        # an expander comment
        (a, b)= parseComment(idxst, pos+1)
        elm= ParsedComment(idxst, a+1, b-1)
        return (b, elm)
    if matched=="(":
        # pylint: disable= redefined-variable-type
        (a, b)= parseCode(idxst, pos+1)
        m_ident= rx_pyIdent.match(st, a+1, b-1)
        if m_ident is not None:
            elm= ParsedVar(idxst, a+1, b-2)
        else:
            elm= ParsedEval(idxst, a+1, b-2)
        return (b, elm)
    if matched=="{":
        # a purecommand enclosed in "{}" brackets
        (a, b)= parseBracketed(idxst, pos+1)
        elm= ParsedPureCommand(idxst, a+1, b-2)
        return (b, elm)
    # from here: a purecommand or a command
    try:
        nextchar= st[m.end()]
    except IndexError as _:
        nextchar= None
    if nextchar=="(":
        (a, b)= parseCode(idxst, m.end())
        elm= ParsedCommand(idxst, a+1, b-2, matched)
        return (b, elm)
    elm= ParsedPureCommand(idxst, pos+1, m.end()-1)
    return (m.end(), elm)

def parseBackslash(idxst, pos):
    r"""parses a backslash.

    >>> import os
    >>> def test(st,pos,sep=None):
    ...     if sep:
    ...         change_linesep(sep)
    ...     idxst= IndexedString(st)
    ...     (p,elm)= parseBackslash(idxst,pos)
    ...     print("Parsed: %s" % elm)
    ...     print("rest of string:%s" % repr(st[p:]))
    ...     change_linesep(os.linesep)
    ...
    >>> test(r"\abc",0)
    Parsed: ('ParsedLiteral', (0, 0), '\\')
    rest of string:'abc'
    >>> test("\\",0)
    Parsed: ('ParsedLiteral', (0, 0), '\\')
    rest of string:''
    >>> test("\\\rab",0,"\r")
    Parsed: None
    rest of string:'ab'
    >>> test("\\\rab",0,"\n")
    Parsed: ('ParsedLiteral', (0, 0), '\\')
    rest of string:'\rab'
    >>> test("\\\rab",0,"\r\n")
    Parsed: ('ParsedLiteral', (0, 0), '\\')
    rest of string:'\rab'
    >>> test("\\\nab",0,"\r")
    Parsed: ('ParsedLiteral', (0, 0), '\\')
    rest of string:'\nab'
    >>> test("\\\nab",0,"\n")
    Parsed: None
    rest of string:'ab'
    >>> test("\\\nab",0,"\r\n")
    Parsed: ('ParsedLiteral', (0, 0), '\\')
    rest of string:'\nab'
    >>> test("\\\r\nab",0,"\r")
    Parsed: None
    rest of string:'\nab'
    >>> test("\\\r\nab",0,"\n")
    Parsed: ('ParsedLiteral', (0, 0), '\\')
    rest of string:'\r\nab'
    >>> test("\\\r\nab",0,"\r\n")
    Parsed: None
    rest of string:'ab'
    """
    # backslash found
    if not isinstance(idxst, IndexedString):
        raise TypeError("idxst par wrong: %s" % repr(idxst))
    st= idxst.st()
    if st[pos]!="\\":
        raise ParseException("backslash expected at",
                             rowcol= idxst.rowcol(pos))
    l_= len(st)
    if pos+1>=l_:
        # no more characters
        elm= ParsedLiteral(idxst, pos, pos)
        return (pos+1, elm)
    else:
        # at least one more character
        nextchar= st[pos+1]
        if nextchar=="\\":
            elm= ParsedLiteral(idxst, pos, pos)
            return (pos+2, elm)
        if nextchar=="$":
            elm= ParsedLiteral(idxst, pos+1, pos+1)
            return (pos+2, elm)
        if pos+LINESEP_LEN>=l_:
            # not enough characters for LINESEP
            elm= ParsedLiteral(idxst, pos, pos)
            return (pos+1, elm)
        else:
            for i in range(LINESEP_LEN):
                if st[pos+1+i]!=LINESEP[i]:
                    # no line separator follows
                    elm= ParsedLiteral(idxst, pos, pos)
                    return (pos+1, elm)
            return(pos+LINESEP_LEN+1, None)

rx_top= re.compile(r'(\$|\\)')
def parseAll(idxst, pos):
    r"""parse everything.

    >>> def test(st,pos):
    ...     idxst= IndexedString(st)
    ...     pprint(parseAll(idxst,pos))
    ...

    >>> test("abc",0)
    ('ParsedLiteral', (0, 2), 'abc')
    >>> test("abc$xyz",0)
    ('ParsedLiteral', (0, 2), 'abc')
    ('ParsedPureCommand', (4, 6), 'xyz')
    >>> test("abc${xyz}efg",0)
    ('ParsedLiteral', (0, 2), 'abc')
    ('ParsedPureCommand', (5, 7), 'xyz')
    ('ParsedLiteral', (9, 11), 'efg')
    >>> test("abc$xyz(2*4)",0)
    ('ParsedLiteral', (0, 2), 'abc')
    ('ParsedCommand', (8, 10), '2*4', 'xyz')
    >>> test("abc$(2*4)ab",0)
    ('ParsedLiteral', (0, 2), 'abc')
    ('ParsedEval', (5, 7), '2*4')
    ('ParsedLiteral', (9, 10), 'ab')
    >>> test("abc\\$(2*4)ab",0)
    ('ParsedLiteral', (0, 2), 'abc')
    ('ParsedLiteral', (4, 4), '$')
    ('ParsedLiteral', (5, 11), '(2*4)ab')
    >>> test("ab$func(1+2)\\\nnew line",0)
    ('ParsedLiteral', (0, 1), 'ab')
    ('ParsedCommand', (8, 10), '1+2', 'func')
    ('ParsedLiteral', (14, 21), 'new line')
    >>> test("ab$func(1+2)\nnew line",0)
    ('ParsedLiteral', (0, 1), 'ab')
    ('ParsedCommand', (8, 10), '1+2', 'func')
    ('ParsedLiteral', (12, 20), '\nnew line')
    >>> test("ab$(xyz)(56)",0)
    ('ParsedLiteral', (0, 1), 'ab')
    ('ParsedVar', (4, 6), 'xyz')
    ('ParsedLiteral', (8, 11), '(56)')

    >>> test(r'''
    ... Some text with a macro: $(xy)
    ... an escaped dollar: \$(xy)
    ... a macro within letters: abc${xy}def
    ... a pyexpander command structure:
    ... $if(a=1)
    ... here
    ... $else
    ... there
    ... $endif
    ... now a continued\
    ... line
    ... from here:$# the rest is a comment
    ... now an escaped continued\\
    ... line
    ... ''',0)
    ('ParsedLiteral', (0, 24), '\nSome text with a macro: ')
    ('ParsedVar', (27, 28), 'xy')
    ('ParsedLiteral', (30, 49), '\nan escaped dollar: ')
    ('ParsedLiteral', (51, 51), '$')
    ('ParsedLiteral', (52, 83), '(xy)\na macro within letters: abc')
    ('ParsedPureCommand', (86, 87), 'xy')
    ('ParsedLiteral', (89, 124), 'def\na pyexpander command structure:\n')
    ('ParsedCommand', (129, 131), 'a=1', 'if')
    ('ParsedLiteral', (133, 138), '\nhere\n')
    ('ParsedPureCommand', (140, 143), 'else')
    ('ParsedLiteral', (144, 150), '\nthere\n')
    ('ParsedPureCommand', (152, 156), 'endif')
    ('ParsedLiteral', (157, 172), '\nnow a continued')
    ('ParsedLiteral', (175, 189), 'line\nfrom here:')
    ('ParsedComment', (192, 214), ' the rest is a comment\n')
    ('ParsedLiteral', (215, 238), 'now an escaped continued')
    ('ParsedLiteral', (239, 239), '\\')
    ('ParsedLiteral', (241, 246), '\nline\n')
    """
    if not isinstance(idxst, IndexedString):
        raise TypeError("idxst par wrong: %s" % repr(idxst))
    st= idxst.st()
    parselist=[]
    l= len(st)
    while True:
        if pos>=l:
            return parselist
        m= rx_top.search(st, pos)
        if m is None:
            parselist.append(ParsedLiteral(idxst, pos, len(st)-1))
            return parselist
        if m.start()>pos:
            parselist.append(ParsedLiteral(idxst, pos, m.start()-1))
        if m.group(1)=="\\":
            (p, elm)= parseBackslash(idxst, m.start())
            if elm is not None:
                parselist.append(elm)
            pos= p
            continue
        # from here it must be a dollar sign
        (pos, elm)= parseDollar(idxst, m.start())
        parselist.append(elm)
        continue

def pprint(parselist):
    """pretty print a parselist."""
    for elm in parselist:
        print(str(elm))

def _test():
    """perform the doctest tests."""
    import doctest
    print("testing...")
    doctest.testmod()
    print("done")

if __name__ == "__main__":
    _test()
