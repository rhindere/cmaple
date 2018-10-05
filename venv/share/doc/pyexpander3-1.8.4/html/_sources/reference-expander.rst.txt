pyexpander reference
====================

A note on Python versions
-------------------------

Short version
+++++++++++++

If you don't already use pyexpander, or don't know the python language, simply
install the python 3 version of pyexpander. The program that does macro
substitutions is then "expander3.py".

Background
++++++++++

Currently there exist two major branches of the python language, python version
2 and python version 3. Both have slight differences in syntax and not all
programs are compatible with both versions.

Pyexpander comes in a python 2 and a python 3 version. You can install one of
these versions or both at the same time. In order to distinguish the versions,
the expander script is named "expander.py" for the python 2 version, and
"expander3.py" for the python 3 version. 

Note that embedded python code like in the ``py(...)`` statement must use the
same major python version as the one pyexpander uses. So if you installed
pyexpander for python 3 your embedded python code must also be in the python 3
dialect. The same applies for python 2.

Syntax of the pyexpander language
---------------------------------

The meaning of the dollar sign
++++++++++++++++++++++++++++++

Almost all elements of the language start with a dollar "$" sign. If a dollar
is preceded by a backslash "\\" it is escaped. The "\\$" is then replaced with
a simple dollar character "$" and the rules described further down do not
apply.

Here is an example::
 
  an escaped dollar: \$

This would produce this output::

  an escaped dollar: $

Comments
++++++++

A comment is started by a sequence "$#" where the dollar sign is not preceded
by a backslash (see above). All characters until and including the end of line
character(s) are ignored. Here is an example::

  This is ordinary text, $# from here it is a comment
  here the text continues.

Commands
++++++++

If the dollar sign, which is not preceded by a backslash, is followed by a
letter or an underline "_" and one or more alphanumeric characters, including
the underline "_", it is interpreted to be an expander command. 

The *name* of the command consists of all alphanumeric characters including "_"
that follow. In order to be able to embed commands into a sequence of letters,
as a variant of this, the *name* may be enclosed in curly brackets. This
variant is only allowed for commands that do not expect parameters.

If the command expects parameters, an opening round bracket "(" must
immediately (without spaces) follow the characters of the command name. The
parameters end with a closing round bracket ")".

Here are some examples::
 
  this is not a command due to escaping rules: \$mycommand
  a command: $begin
  a command within a sequence of letters abc${begin}def
  a command with parameters: $for(x in range(0,3))

Note that in the last line, since the parameter of the "for" command must be a
valid python expression, all opening brackets in that expression must match a
closing bracket. By this rule pyexpander is able to find the closing bracket
that belongs to the opening bracket of the parameter list.

Executing python statements
+++++++++++++++++++++++++++

A statement may be any valid python code. Statements usually do not return
values. All expressions are statements, but not all statements are 
expressions. In order to execute python statements, there is the "py" command.
"py" is an abbreviation of python. This command expects that valid python code
follows enclosed in brackets. Note that the closing bracket for "py" *must not*
be in the same line with a python comment, since a python comment would include
the bracket and all characters until the end of the line, leading to a
pyexpander parser error. The "py" command leads to the execution of the python
code but produces no output. It is usually used to define variables, but it can
also be used to execute python code of more complexity. Here are some
examples::

  Here we define the variable "x" to be 1: $py(x=1)
  Here we define two variables at a time: $py(x=1;y=2)
  Here we define a function, note that we have to keep
  the indentation that python requires intact:
  $py(
  def multiply(x,y):
      return x*y
      # here is a python comment
      # note that the closing bracket below
      # *MUST NOT* be in such a comment line
     )

Line continuation
+++++++++++++++++

Since the end of line character is never part of a command, commands placed on
a single line would produce an empty line in the output. Since this is
sometimes not wanted, the generation of an empty line can be suppressed by
ending the line with a single backslash "\\". Here is an example::

  $py(x=1;y=2)\
  The value of x is $(x), the value of y is $(y).
  Note that no leading empty line is generated in this example.

If you have an application that would always require backslashes at the end of
commands you can start the expander script with option "-a". This has the same
effect as appending a backslash to each line that ends with a command. See also
:doc:`expander-options`.

So with "-a" you expander script does not have to look look like this::

  $py(
  a=True
  )\
  Here is a conditional:
  $if(a)\
  a was True
  $else\
  a was False
  $endif\

but like this::

  $py(
  a=True
  )
  Here is a conditional:
  $if(a)
  a was True
  $else
  a was False
  $endif

Substitutions
+++++++++++++

A substitution consists of a dollar "$" that is not preceded by a backslash and
followed by an opening round bracket "(" and a matching closing round bracket
")". The string enclosed by the pair of brackets must form a valid python
expression. Note that a python expression, in opposition to a python statement,
always has a value. This value is converted to a string and this string is
inserted in the text in place of the substitution command. Here is an example::

  $py(x=2) we set "x" to 2 here
  now we can replace "x" anywhere in the text
  like here $(x) since "x" alone is already a python expression.
  Note that the argument of "py" is a python statement.
  We can also insert x times 3 here like this: $(x*3). 
  We can even do calculations like: $(x*sin(x)).

There is also a mode called "simple vars" in the expander tool, where the round
brackets around variable names may be omitted. Note that this is not possible
for arbitrary python expressions, since pyexpander would not know where the
expression ends without the brackets. Here is an example::

  We define x: $py(x=1)
  In "simple vars" mode, we can use the variable as we know
  it: $(x) but also without brackets: $x. However, expressions that are
  not simple variable names must still use brackets: $(x*2).

Default values for variables
++++++++++++++++++++++++++++

When an undefined variable is encountered, pyexpander raises a python exception
and stops. Sometimes however, we want to take a default value for a variable
but only if it has not yet been set with a value. This can be achieved with the
"default" command.  This command must be followed by an opening bracket and an
arbitrary list of named python parameters. This means that each parameter
definition consists of an unquoted name, a "=" and a quoted string, several
parameter definitions must be separated by commas. The "default" command takes
these parameters and sets the variables of these names to the given values if
the variables are not yet set with different values. Here is an example::

  We define a: $py(a=1)
  Now we set a default for a and b: $default(a=10, b=20)
  Here, $(a) is 1 since is was already defined before
  and $(b) is 20, it's default value since it was not defined before.

Variable scopes
+++++++++++++++

By default, all variables defined in a "py" command are global. They exist from
the first time they are mentioned in the text and can be modified at any place
further below.  Sometimes however, it is desirable to set a variable in a
certain area of the text and restore it to it's old value below that area. In
order to do this, variable scopes are used. A variable scope starts with a
"begin" command and ends with an "end" command. All variable definitions and
changes between "begin" and "end" are reverted when the "end" command is
reached. Some commands like "for", "while" and "include" have a variant with a
"_begin" appended to their name, where they behave like "begin" and "end" and
define a variable scope additionally to their normal function. Here is an
example of "begin" and "end"::
  
  $py(a=1)
  a is now 1
  $begin
  $py(a=2)
  a is now 2
  $end
  here, a is 1 again

All variable modifications and definitions within a variable scope are isolated
from the rest of the text. However, sometimes we want to modify variables
outside the scope. This can be done by declaring a variable as non-local with
the command "nonlocal". The "nonlocal" command must be followed by a comma
separated list of variable names enclosed in brackets. When the end of the
scope is reached, all variables that were declared non-local are copied to the
outer scope. Here is an example::

  $py(a=1;b=2;c=3)
  a is now 1, b is 2 and c is 3
  $begin
  $nonlocal(a,b)
  $py(a=10;b=20;c=30)
  a is now 10, b is 20 and c is 30
  $end
  here, a is 10, b is 20 and c is 3 again

If scopes are nested, the "nonlocal" defines a variable to be non-local only in
the current scope. If the current scope is left, the variable is local again
unless it is defined non-local in that scope, too.

Extending the pyexpander language
+++++++++++++++++++++++++++++++++

All functions or variables defined in a "$py" command have to be applied in the
text by enclosing them in brackets and prepending a dollar sign like here::

  $(myvar)
  $(myfunction(parameters))

However, sometimes it would be nice if we could use these python objects a bit
easier. This can be achieved with the "extend" or the "extend_expr" command.
"extend" expects to be followed by a comma separated list of identifiers
enclosed in brackets. "extend_expr" must be followed by a python expression
that is an iterable of strings. The identifiers can then be used in the text
without the need to enclose them in brackets. Here is an example::

  $extend(myvar,myfunction)
  $myvar
  $myfunction(parameters)

Note that identifiers extend the pyexpander language local to their scope. Here
is an example for this::

  $py(a=1)
  $begin
  $extend(a)
  we can use "a" here directly like $a
  $end
  here the "extend" is unknown, a has always
  to be enclosed in brackets like $(a)

You should note that with respect to the "extend" command, there is a
difference between including a file with the "include" command or the
"include_begin" command (described further below). The latter one defines a
new scope, and the rule shown above applies here, too.

Conditionals
++++++++++++

A conditional part consists at least of an "if" and an "endif" command. Between
these two there may be an arbitrary number of "elif" commands. Before "endif"
and after the last "elif" (if present) there may be an "else" command. "if" and
"elif" are followed by a condition expression, enclosed in round brackets.
"else" and "endif" do not have parameters. If the condition after "if" is true,
this part is evaluated. If it is false, the next "elif" part is tested. If it
is true, this part is evaluated, if not, the next "elif" part is tested and so
on. If no matching condition was found, the "else" part is evaluated. All of
this is oriented on the python language which also has "if","elif" and "else".
"endif" has no counterpart in python since there the indentation shows where
the block ends. Here is an example::

  We set x to 1; $py(x=1)
  $if(x>2)
  x is bigger than 2
  $elif(x>1)
  x is bigger than 1
  $elif(x==1)
  x is equal to 1
  $else
  x is smaller than 1
  $endif
  here is a classical if-else-endif:
  $if(x>0)
  x is bigger than 0
  $else
  x is not bigger than 0
  $endif
  here is a simple if-endif:
  $if(x==0)
  x is zero
  $endif

While loops
+++++++++++

While loops are used to generate text that contains almost identical
repetitions of text fragments. The loop continues while the given loop
condition is true. A While loop starts with a "while" command followed by a
boolean expression enclosed in brackets. The end of the loop is marked by a
"endwhile" statement. Here is an example::

  $py(a=3)
  $while(a>0)
  a is now: $(a)
  $py(a-=1)
  $endwhile

In this example the loop runs 3 times with values of a ranging from 3 to 1. 

The command "while_begin" combines a while loop with a scope::

  $while_begin(condition)
  ...
  $endwhile
  
and::

  $while(condition)
  $begin
  ...
  $end
  $endwhile

are equivalent. 
  
For loops
+++++++++

For loops are a powerful tool to generate text that contains almost identical
repetitions of text fragments. A "for" command expects a parameter that is a
python expression in the form "variable(s) in iterable". For each run the
variable is set to another value from the iterable and the following text is
evaluated until "endfor" is found. At "endfor", pyexpander jumps back to the
"for" statement and assigns the next value to the variable. Here is an
example::

  $for(x in range(0,5))
  x is now: $(x)
  $endfor

The range function in python generates a list of integers starting with 0 and
ending with 4 in this example. 

You can also have more than one loop variable::

  $for( (x,y) in [(x,x*x) for x in range(0,3)])
  x:$(x) y:$(y)
  $endfor

or you can iterate over keys and values of a python dictionary::

  $py(d={"A":1, "B":2, "C":3})
  $for( (k,v) in d.items())
  key: $(k) value: $(v)
  $endfor

The command "for_begin" combines a for loop with a scope::

  $for_begin(loop expression)
  ...
  $endfor
  
and::

  $for(loop expression)
  $begin
  ...
  $end
  $endfor

are equivalent. 

macros
++++++

Macros provide a way to group parts of your scripts and reuse them at other
places. Macros can have arguments that provide values when the macro is
instantiated. You can think of a macro as a way to copy and paste a part of
your script to a different location. Note that a macro invocation must always
be followed by a pair of brackets, even if the macro doesn't get any arguments.

Here is an example::

  $macro(snippet)
  This is a macro that just 
  adds some text.
  $endmacro
  \
  $macro(underline, line)
  $(line)
  $("-" * len(line))
  $endmacro
  \
  $underline("My heading")
  $snippet()

If you run this with expander.py or expander3.py with option -a (see 
`Line continuation`_), this is the output::

  My heading
  ----------
  This is a macro that just 
  adds some text.

Arguments to macros are given the same way as in python, except you cannot use
default values for arguments.

With option -i (see :doc:`expander-options`) pyexpander indents lines according to the row where the macro invocation was placed. Here is an example::

  $macro(subsnippet)
  This is another
  snippet.
  $endmacro
  \
  $macro(snippet)
  This is a macro that just 
  adds some text and contains
  a subsnippet from here
      $subsnippet()
  to here.
  Snippet end.
  $endmacro
  \
  $macro(underline, line)
  $(line)
  $("-" * len(line))
  $endmacro
  \
  $underline("My heading")
      $snippet()

If you run this with expander.py or expander3.py with option -a and -i,
you get the following output::

  My heading
  ----------
      This is a macro that just 
      adds some text and contains
      a subsnippet from here
          This is another
          snippet.
      to here.
      Snippet end.

As you see, the text of the macro has the same indentation level as the macro
itself. This is also true for macros that contain other macros.

Include files
+++++++++++++

The "include" command is used to include a file at the current position. It
must be followed by a string expression enclosed in brackets. The given file is
then interpreted until the end of the file is reached, then the interpretation
of the text continues after the "include" command in the original text.

Here is an example::

  $include("additional_defines.inc")

The command "include_begin" combines an include with a scope. It is equivalent
to the case when the include file starts with a "begin" command and ends with
an "end" command.

Here is an example::

  $include_begin("additional_defines.inc")

Commands for EPICS macro substitution
+++++++++++++++++++++++++++++++++++++

`EPICS <http://www.aps.anl.gov/epics>`_ is a framework for building control
systems. pyexpander has three more commands for this application, that
are described here:

:doc:`EPICS support in pyexpander <epics-support>`.

Internals
---------

This section describes how pyexpander works. 

pyexpander consists of the following parts:

pyexpander.parser
+++++++++++++++++

A python module that implements a parser for expander files. This is the
library that defines all functions and classes the are used for 
pyexpander.

Here is a link to the :py:mod:`pyexpander.parser`.

pyexpander.lib
++++++++++++++

A python module that implements all the functions needed to 
implement the pyexpander language.

Here is a link to the :py:mod:`pyexpander.lib`.

Scripts provided by the package
-------------------------------

expander3.py
++++++++++++

This script is used for macro substitution in text files. They have
command line options for search paths and file names and use pyexpander 
to interpret the given text file.

You will probably just use one of these for your application. However, you
could write a python program yourself that imports and uses the pyexpander
library.

Here is a link to the `expander3.py command line options <expander-options.html>`_.

Note that if you installed the python 2 version of pyexpander, this script is
called "expander.py" instead.

msi2pyexpander3.py
++++++++++++++++++

This script is used to convert `EPICS <http://www.aps.anl.gov/epics>`_ `msi
<http://www.aps.anl.gov/epics/extensions/msi/index.php>`_ template files to the
format of pyexpander. You only need this script when you have an `EPICS
<http://www.aps.anl.gov/epics>`_ application and want to start using pyexpander
for it.

Here is a link to the `command line options of msi2pyexpander3.py
<msi2pyexpander-options.html>`_.

Note that if you installed the python 2 version of pyexpander, this script is
called "msi2pyexpander.py" instead.

