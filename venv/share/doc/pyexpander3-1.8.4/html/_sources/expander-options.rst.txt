expander.py and expander3.py command line options
=================================================

``-h``
++++++

    Show help for command line options.

``--summary``
+++++++++++++

    Print a summary of the function of the program.

``-f FILE --file FILE``
+++++++++++++++++++++++

    Specify a FILE to process. This option may be used more than once to
    process more than one file but note than this option is not really needed.
    Files can also be specified directly after the other command line options.
    If not given, the program gets it's input from stdin.

``--eval``
++++++++++

    Evaluate PYTHONEXPRESSION in global context.

``-I PATH --include PATH``
++++++++++++++++++++++++++

    Add PATH to the list of include paths.

``-s --simple-vars``
++++++++++++++++++++

    Allow variables without brackets.

``-a --auto-continuation``
++++++++++++++++++++++++++

    Assume '\' at the end of lines with commands.

``-i --auto-indent``
++++++++++++++++++++++++++
    
    Automatically indent macros.

``--no-stdin-msg``
++++++++++++++++++++

    Do not print a message on stderr when the program is reading it's input
    from stdin.


