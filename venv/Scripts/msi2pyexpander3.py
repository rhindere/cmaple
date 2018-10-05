#!C:\Users\rhindere\Documents\PycharmProjects\maple_project\venv\Scripts\python.exe
# -*- coding: UTF-8 -*-
"""convert EPICS msi files to pyexpander files.
"""

from optparse import OptionParser
import sys
import re
import os.path

# version of the program:
__version__= "1.8.4" #VERSION#

# pylint: disable=invalid-name

output_mode= "w"

st_space_or_comment    = r'\s*(?:\s*(?:|\#[^\r\n]*)[\r\n]+)*\s*'

st_quoted_word         = r'\"(?:\w+)\"'
st_unquoted_word       = r'(?:\w+)'

st_quoted              = r'\"(?:.*?)(?<!\\)\"'
st_unquoted_filename   = r'(?:[^\/\s\{\}]+)'

st_unquoted_value      = r'(?:[^"\s\{\},]+)'

st_comma               = r',?'

st_top= r'([ \t]*)(file)'
rx_top= re.compile(st_top, re.M)

st_pattern= r'(%s)pattern' % st_space_or_comment
rx_pattern= re.compile(st_pattern, re.M)

st_file_head= r'(%s)(%s|%s)(%s){' % (st_space_or_comment,
                                     st_quoted,st_unquoted_filename,
                                     st_space_or_comment)
rx_file_head= re.compile(st_file_head, re.M)

st_bracket1= r'(%s)\{' % st_space_or_comment
rx_bracket1= re.compile(st_bracket1, re.M)

st_bracket2= r'(%s)\}' % st_space_or_comment
rx_bracket2= re.compile(st_bracket2, re.M)

st_def= r'(%s)(%s|%s)\s*=\s*(%s|%s)(%s)(,?)(%s)(\}?)' % \
                 (st_space_or_comment,
                  st_quoted_word,
                  st_unquoted_word,
                  st_quoted,
                  st_unquoted_value,
                  st_space_or_comment,
                  st_space_or_comment)
rx_def= re.compile(st_def, re.M)

st_val= r'(%s)(%s|%s)\s*(,|\})' % \
                 (st_space_or_comment,
                  st_quoted,
                  st_unquoted_value)
rx_val= re.compile(st_val, re.M)

def isempty(st):
    """returns True if st is empty or if st contains only spaces."""
    if st=="":
        return True
    return st.isspace()

def unquote(st):
    """removes quotes around a string.

    Here are some examples:
    >>> unquote("")
    ''
    >>> unquote('"')
    ''
    >>> unquote('""')
    ''
    >>> unquote('"x"')
    'x'
    >>> unquote('"x')
    'x'
    >>> unquote('x"')
    'x'
    """
    try:
        if st[0]=='"':
            st= st[1:]
    except IndexError as _:
        pass
    try:
        if st[-1]=='"':
            st= st[0:-1]
    except IndexError as _:
        pass
    return st

def quote(st):
    """always return a quoted string.

    Here are some examples:
    >>> quote('')
    '""'
    >>> quote('a')
    '"a"'
    >>> quote('"a"')
    '"a"'
    >>> quote('"a')
    '"a"'
    >>> quote('a"')
    '"a"'
    """
    if st=="":
        return '""'
    if st[0]!='"':
        st= '"'+st
    if st[-1]!='"':
        st= st+'"'
    return st

# read all of <stdin> into a single variable:
def process_file(filename, outputfile):
    """convert a single file."""
    # pylint: disable= too-many-branches
    # pylint: disable= too-many-statements
    global output_mode
    if filename != "-":
        f= open(filename, "r")
    else:
        sys.stderr.write("(expect input from stdin)\n")
        f= sys.stdin
    all_= f.read()
    if filename != "-":
        f.close()

    new=[]
    pos= 0
    mode=["top"]
    value_dict={}
    while True:
        #print "pos:",pos
        #print "mode:",repr(mode)
        if mode[-1] == "top":
            m= rx_top.search(all_,pos)
            if m is not None:
                # append everything *before* the match:
                new.append( all_[pos:m.start()] )
                pos= m.end()
                mode.append("file")
                continue
            else:
                new.append( all_[pos:] )
                break
        elif mode[-1] == "in pattern":
            m= rx_bracket1.match(all_, pos)
            if m is not None:
                #print "MATCH:",all_[m.start():m.end()]
                if not isempty(m.group(1)):
                    new.append(m.group(1))
                new.append("          ( ")
                pos= m.end()
                mode.append("in pattern list")
                continue
            else:
                new.append("        )\\")
                mode.pop()
                continue
        elif mode[-1] == "in pattern list":
            m= rx_val.match(all_,pos)
            if m is not None:
                #print "MATCH:",all_[m.start():m.end()]
                if not isempty(m.group(1)):
                    new.append(m.group(1))
                s= quote(m.group(2))
                b= m.group(3)
                if b != "}":
                    new.append("%s, " % s)
                else:
                    new.append("%s),\n" % s)
                    mode.pop()
                pos= m.end()
                continue
            raise AssertionError("parse error at:"+all_[pos:pos+40])

        elif mode[-1] == "file":
            m= rx_file_head.match(all_,pos)
            if m is not None:
                #print "MATCH:",all_[m.start():m.end()]
                if not isempty(m.group(1)):
                    new.append(m.group(1))
                new.append("$substfile(\"%s\")\\\n" % m.group(2))
                if not isempty(m.group(3)):
                    new.append(m.group(3))
                pos= m.end()
                mode.append("in file")
                continue
        elif mode[-1] == "in file":
            m= rx_pattern.match(all_, pos)
            if m is not None:
                if not isempty(m.group(1)):
                    new.append(m.group(1))
                new.append("$pattern(\n")
                pos= m.end()
                mode.append("in pattern")
                continue
            m= rx_bracket1.match(all_, pos)
            if m is not None:
                #print "MATCH:",all_[m.start():m.end()]
                if not isempty(m.group(1)):
                    new.append(m.group(1))
                new.append("$subst(\n")
                pos= m.end()
                mode.append("subst")
                value_dict= {}
                continue
            m= rx_bracket2.match(all_,pos)
            if m is not None:
                #print "MATCH:",all_[m.start():m.end()]
                #new.extend((m.group(1),"),"))
                pos= m.end()
                mode.pop() # pop "in file"
                mode.pop() # pop "file"
                continue
            raise AssertionError("parse error at:"+all_[pos:pos+40])
        elif mode[-1] == "subst":
            m= rx_def.match(all_,pos)
            if m is not None:
                #print "MATCH:",all_[m.start():m.end()]
                #print "MATCH GROUPS:",m.groups()
                if not isempty(m.group(1)):
                    new.append(m.group(1))
                name= unquote(m.group(2)) # name
                value= quote(m.group(3)) # value
                new.append("        %s= %s" % (name,value))
                if name in value_dict:
                    sys.stderr.write("WARNING: duplicate symbol: %s=%s\n" % \
                                     (name,value))
                else:
                    value_dict[name]= value
                b= m.group(7) # optional closing bracket
                if b != "}":
                    new.append(",\n")
                if not isempty(m.group(4)):
                    new.append(m.group(4))
                if not isempty(m.group(6)):
                    new.append(m.group(6))
                if b == "}":
                    new.append(",\n      )\\\n")
                    mode.pop()
                pos= m.end()
                continue
            else:
                m= rx_bracket2.match(all_,pos)
                if m is None:
                    raise AssertionError("parse error near: \"%s\"" % all_[pos:pos+10])
                if not isempty(m.group(1)):
                    new.append(m.group(1))
                new.append(")\\\n")
                mode.pop()
                pos= m.end()
                continue

    if outputfile is not None:
        out= open(outputfile, output_mode)
        output_mode= "a"
    else:
        out= sys.stdout
    #out.write("do(\n")
    out.write("".join(new))
    #out.write(")\n")
    if outputfile is not None:
        out.close()


def process_files(options,args):
    """do all the work."""
    filelist= []
    if options.substitutionfile is not None:
        filelist= options.substitutionfile
    if len(args)>0: # extra arguments
        filelist.extend(args)
    if len(filelist)<=0:
        filelist= ["-"]
    for f in filelist:
        process_file(f, options.outputfile)

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

def print_summary():
    """print a short summary of the scripts function."""
    print("%-20s: convert substitution files to pyexpander format.\n" % \
          script_shortname())

def main():
    """The main function.

    parse the command-line options and perform the command
    """
    # command-line options and command-line help:
    usage = "usage: %prog [options] {files}"

    parser = OptionParser(usage=usage,
                          version="%%prog %s" % __version__,
                          description="this program converts EPICS "+\
                                      "substitution files to "+\
                                      "pyexpander format.\n")

    parser.add_option("--summary",
                      action="store_true",
                      help="Show a summary of the program's function.",
                     )
    parser.add_option("-S", "--substitutionfile",
                      action="append",
                      type="string",
                      help="Specify the SUBSTITUTIONFILE.",
                      metavar="SUBSTITUTIONFILE"
                     )
    parser.add_option("-o", "--outputfile",
                      action="store",
                      type="string",
                      help="Specify the OUTPUTFILE.",
                      metavar="OUTPUTFILE"
                     )

    # x= sys.argv
    (options, args) = parser.parse_args()
    # options: the options-object
    # args: list of left-over args

    if options.summary:
        print_summary()
        sys.exit(0)

    process_files(options,args)
    sys.exit(0)

if __name__ == "__main__":
    main()

