EPICS support in pyexpander
===========================

`EPICS <http://www.aps.anl.gov/epics>`_ is a framework for control systems
used at many research facilities, including the 
`Helmholtz-Zentrum Berlin <https://www.helmholtz-berlin.de>`_.

Pyexpander has three commands in order to support EPICS macro substitution 
which is usually done by the 
`msi <http://www.aps.anl.gov/epics/extensions/msi/index.php>`_ tool. 
These commands may also be useful for other applications. 

The idea in msi is to have a template file with macro placeholders in it and
process this file several times with different macro values at each run. In
this mechanism, the filename has only to be mentioned once. 

Here is a simple example, test.template has this content::

  record(calcout, "U3IV:$(name)") {
    field(CALC, "$(calc)")
    field(INPA, "U3IV:P4:rip:cvt CPP MS")
    field(OUT,  "U3IV:P4:rip:calcLRip.A PP MS")
  }

test.substitution has this content::

  $template("test.template")\
  $subst(
    name="set", 
    calc="A+B",
  )\
  $subst(
    name="set2",
    calc="C+D"
  )\

This is the result when test.template is processed::

  record(calcout, "U3IV:set") {
    field(CALC, "A+B")
    field(INPA, "U3IV:P4:rip:cvt CPP MS")
    field(OUT,  "U3IV:P4:rip:calcLRip.A PP MS")
  }
  record(calcout, "U3IV:set2") {
    field(CALC, "C+D")
    field(INPA, "U3IV:P4:rip:cvt CPP MS")
    field(OUT,  "U3IV:P4:rip:calcLRip.A PP MS")
  }

As you see, test.template was instantiated twice. In the pyexpander package
there is also a converter program, msi2pyexpander3.py, which can be used to convert
substitution files from the EPICS msi format to the pyexpander format.

This is how the three commands work:

Setting the name of the template file
.....................................

The "template" command is used to define the name of an substitution file. It
must be followed by a string expression enclosed in brackets. Note that the
filename is only defined within the current scope (see "variable scopes"). 

Here is an example::

  $template("test.template")

The "subst" command
...................

This command is used to substitute macros in the file whose name was defined
with the "template" command before. This command must be followed by an
opening bracket and an arbitrary list of named python parameters. This means
that each parameter definition consists of an unquoted name, an "=" and a
quoted string, several parameter definitions must be separated by commas. The
"subst" command takes these parameters and defines the variables in a new
scope. It then processes the file that was previously set with the "template"
command. Here is an example::

  $subst(
          AMS= "ams_",
          BASE= "UE112ID7R:",
          BASE1= "UE112ID7R:",
          BASE2= "UE112ID7R:S",
          BaseStatMopVer= "9",
        )\

The "pattern" command
.....................

This command is an alternative way to substitute macros in a file. The pattern command must be followed by an opening round bracket, a list of python tuples and a closing round bracket. Each tuple is a comma separated list of quoted strings enclosed in round brackets. Tuples must be separated by commas. Here is an example::

  $pattern(
            ( "DEVN", "SIGNAL"),
            ( "PAHRP", "PwrCavFwd"),
            ( "PAHRP", "PwrCavRet"),
            ( "PAHRP", "PwrCircOut"),
          )\

The first tuple defines the names of the variables, all following tuples define
values these variables get. For each following tuple the file defined by
"template" is included once. In the example above, the variable "DEVN" has
always the value "PAHRP", the variable "SIGNAL" has the values "PwrCavFwd",
"PwrCavRet" and "PwrCircOut". The file defined by the previous "template"
command is instantiated 3 times.

Differences to the EPICS msi tool
.................................

These are differences to msi:

- The file format of substitution files is different, but you can use
  msi2pyexpander3.py to convert them.
- Macros must always be defined. If a macro should be expanded and it is not
  defined at the time, the program stops with an exception. If you want the
  program to continue in this case, use the "default" command to provide
  default values for the macros that are sometimes not defined.
- Variables defined in a "subst" command are scoped, they are only defined for
  that single instantiation of the template file. 
- The template file commands "include" and "substitute" as they are known from
  msi are not implemented in this form. However, "include" in pyexpander
  has the same functionality as "include" in msi and "py" in pyexpander can be
  used to do the same as "substitute" in msi.

Here is an example how to convert a template file from msi to pyexpander. Note
that in pyexpander there is no principal difference between a template and a
substitution file, both have the same syntax. The msi template file is this::

  A variable with a default $(var=default value)
  Here we include a file:
  include "filename"
  Here we define a substitution:
  substitute "first=Joe,family=Smith"

Here is the same formulated for pyexpander::

  A variable with a default $default(var="default value")$(var)
  Here we include a file:
  $include("filename")
  Here we define a substitution:
  $py(first="Joe";family="Smith")
