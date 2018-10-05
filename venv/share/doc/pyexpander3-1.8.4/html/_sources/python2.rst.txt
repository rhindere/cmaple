=======================================================
pyexpander for users not familiar with python version 2
=======================================================

.. This text is RST (ReStructured Text), 
   see also http://docutils.sourceforge.net/rst.html

Introduction
------------

Pyexpander is based on the python programming language not just with respect to
it's implementation. Expressions and statements are, in fact, python code. This
page shows some simple use cases for pyexpander for users that do not yet know
python. If you are interested in learning python you can find some information
at the `official python documentation site <http://docs.python.org>`_ and at
the `Python tutorial <http://docs.python.org/tutorial/index.html>`_.

Comments
--------

Comments in python start with a "#" character and extend to the end of the
line. If you want to have several consecutive lines as a comment, each line has
to start with a "#" character. Here are some examples::

  $py(
  a=1 # here is a comment
  # here is a comment
  # spanning several 
  # lines
  )

A word on indentation
---------------------

The indentation of lines (the number of spaces they start with) is part of the
syntax in python. This means that for python commands that span more than one
line, indentation matters. If you get an error message like "unexpected indent"
you know that the problem is the indentation of lines. As a rule of thumb,
python statements that follow a "$py" command should either all be in the same
line as the "$py" command and immediately follow the opening bracket or, if
there is more than one line, all should start in column one. Here are some
examples::

  $py( a=1)     # indentation error due to the space between "(" and "a"
  $py(a=1; b=1) # correct, spaces *within* the line are allowed
  $py(a=1)      # correct
  $py(     
    a=1         # indentation error since "a" is not in column 1 of the line
  )
  $py(     
  a=1           # correct
  )
  $py(
  a=1           # correct
  b=2
  )

Note that due to python indentation rules, the closing bracket ")" of the "$py"
command should be in column 1 if it is in a line of it's own. Otherwise, with
certain python statements, an indentation error may occur.

Defining variables
------------------

Python variable names start with a letter or a "_" and may be followed by an arbitrary number of letters, digits and the "_" character.

You define a variable by placing a variable name, a "=" character and a value. Here are some examples::

  $py(my_number= 1)
  $py(my_var1= 2)

Literals
++++++++

You often define variables with constant values, also called literals.
Integers, floating point numbers and strings can be written the same way as in
C. Here are some examples::

  $py(my_integer=3)
  $py(my_float1=1.23)
  $py(my_float2=3.1E8)
  $py(my_string="abc")
  $py(my_line="This is a line with LF at the end.\n")

Setting more than one variable
++++++++++++++++++++++++++++++

Python statements are separated by a ";" character or by a newline character. You can define more than one variable like this::

  $py(a=1; b=2; c=3)

or like this::
  
  $py(
  a=1
  b=2
  c=3
  )

Simple expressions
++++++++++++++++++

Simple arithmetic expressions in python are the same as in c. Here are some examples::

  $py(
  a=2+4
  b=1.4-3.8
  c=3*4
  d=a*b
  e=2**4 # 2**4==16
  )

Mathematical functions
++++++++++++++++++++++

Common mathematical functions are in the "math" package in python. You have to import this package once in order to be able to use these functions. Here is an example::

  $py(
  from math import * # import mathematical functions
  e= exp(1)  # exponential function
  a= sqrt(2) # square root
  )

String expressions
++++++++++++++++++

Strings can be concatenated with "+"::

  $py(a="ab"+"cd") # now a is "abcd"

The "%" operator works according to the string formatting rules for the
"printf" command in C. It is an infix operator, a format string must be
followed by a "%" and a single value or a tuple of values. A tuple is a comma
separated list of values enclosed in round brackets. Here are some examples::

  $py(
  a= "%02d" % 3 # a=="03"
  b= "%d %3.4f" % (2, 123.456789) # b= "2 123.4568"
  )

For loops
---------

This section describes the "$for" statement of pyexpander which is very close
to the for-statement in python. 

For loops in python are a bit different from C. A typical loop statement
consists of a variable or a tuple of variables, the keyword "in" and an
"iterable" datatype, typically a list. If you simply want to have a loop
variable starting with a number, increase by 1 at each run, and end with
another number, you typically use the "xrange" function. In pure python a
for-loop running from 0 to 3 would look like this::

  for i in xrange(4):
      print "i is now:",i

The "$for" statement in pyexpander is a bit different, but the specification of
the loop limit and loop variable are the same::

  $for(i in xrange(4))
  i now: $(i)
  $endfor

Note the the number given to "xrange" is *not* part of the iteration. In the
example above, i never has the value 4, the last value of i is 3.

If "xrange" is provided with two numbers, the first number is the start number
and the second number is the end number plus one.  Here is an example where i
runs from 3 to 5::

  $for(i in xrange(3,6))
  i now: $(i)
  $endfor

If "xrange" is provided with 3 numbers, the first ist the start, the second is
the end plus the step and the third is the step. Here is an example where i
takes the values 10, 8 and 6::

  $for(i in xrange(10, 4, -2))
  i now: $(i)
  $endfor

