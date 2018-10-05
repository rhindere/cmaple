Introduction to pyexpander
==========================

Macro substitution
------------------

Note: The examples below use "expander3.py", the python 3 implementation of
pyexpander. You have to call "expander.py" if you installed the python 2
implementation of pyexpander. 

For some projects there is the need to replace macros in a text file with
values defined in other files or the command line. There are already other
macro replacement tools that can do this but if you want to calculations or
string operations and insert the results of this into your file, the list of
possible tools becomes much shorter.

Pyexpander combines the python programming language with a simple macro
replacement scheme in order to give the user both, ease of use and the
power of a full featured scripting language. 

Even without being familiar with python you can use pyexpander to perform
calculations or string operations and use the results in your macro
replacements.

Here is a very simple example, this is the content of file "letter.txt"::

  Dear $(salutation) $(surname),
  
  this is a simple pyexpander example.

Applying this command::

  expander3.py --eval 'salutation="Mr";surname="Smith"' -f letter.txt

gives this result::

  Dear Mr Smith,
  
  this is a simple pyexpander example.


Here is more advanced example::

  $py(start=0; end=5)\
   x |  x**2
  ---|------
  $for(x in range(start,end+1))\
  $("%2d | %3d" % (x,x*x))
  $endfor\

Applying expander.py to a file with the content shown above gives the following
result::

   x |  x**2
  ---|------
   0 |   0
   1 |   1
   2 |   4
   3 |   9
   4 |  16
   5 |  25

And here we show how pyexpander compares with the well known m4 macro
processor. We have taken the 
`m4 <http://en.wikipedia.org/wiki/M4_(computer_language)>`_ example with small
modifications from Wikipedia::

  divert(-1)
  # This starts the count at ONE as the incr is a preincrement.
  define(`H2_COUNT', 0)
  # The H2_COUNT macro is redefined every time the H2 macro is used.
  define(`H2',
          `define(`H2_COUNT', incr(H2_COUNT))<h2>H2_COUNT. $1</h2>')
  divert(0)dnl Diversion to 0 means back to normal. dnl macro removes this line.
  H2(First Section)
  H2(Second Section)
  H2(Conclusion)

Here is the same example formulated in pyexpander::

  $py(
  # This starts the count at ONE as the incr is a preincrement.
  H2_COUNT=0
  # H2_COUNT is incremented each time H2 is called.
  def H2(st):
      global H2_COUNT
      H2_COUNT+=1
      return "<h2>%d. %s</h2>" % (H2_COUNT,st)
  )\
  $# the following makes H2 callable without another pair of enclosing brackets:
  $extend(H2)\
  $H2("First Section")
  $H2("Second Section")
  $H2("Conclusion")

Both produce this output::

  <h2>1. First Section</h2>
  <h2>2. Second Section</h2>
  <h2>3. Conclusion</h2>

The advantages of pyexpander are:

- simple syntax definition, all expander commands start with a dollar ("$")
  sign followed by word characters, parameters or python code enclosed in
  brackets or both.
- the full power of the python programming language can be used, all operators,
  functions and modules.
- *any* python expression can be used to insert text.
- There is also a python library, pyexpander.py, which you can use to develop
  other macro tools based on pyexpander.

If you are not familiar with the python programming language, you should have
a look at :doc:`python 3 introduction for pyexpander <python3>`. 

If you intend to use the python 2 version of pyexpander, you should look at
:doc:`python 2 introduction for pyexpander <python2>`. 

For a detailed description of the pyexpander language see 
:doc:`reference <reference-expander>`.
