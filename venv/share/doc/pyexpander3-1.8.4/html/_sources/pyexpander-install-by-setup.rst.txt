Installing pyexpander by running setup.py
=========================================

Note that installing pyexpander this way is a kind of last resort method. You
usually want to install the program with pip or as a debian or rpm package.
These methods are described in:

`Installing pyexpander <pyexpander-install>`_.

Install from source (tar.gz or zip file)
----------------------------------------

Download the file here:

* `pyexpander downloads at Bitbucket <https://bitbucket.org/goetzpf/pyexpander/downloads>`_
* `mirror of pyexpander downloads at Sourceforge <https://sourceforge.net/projects/pyexpander/files/?source=navbar>`_

unpack the tar.gz file with::

  tar -xzf <PACKAGENAME>

or unpack the zip file with::

  unzip <PACKAGENAME>

The pyexpander distribution contains the install script "setup.py". If you install
pyexpander from source you always invoke this script with some command line options. 

The following chapters are just *examples* how you could install pyexpander. For a
complete list of all possibilities see 
`Installing Python Modules <https://docs.python.org/3/install/index.html#install-index>`_.

Note that the python interpreter you use to start setup.py determines for which python version pyexpander is installed. 

In order to install for python 2.x use::

  python2 setup.py [options]

In order to install for python 3.x use::

  python3 setup.py [options]

Whenever ``python`` is mentioned in a command line in the following text remember
to use ``python2`` or ``python3`` instead.

Install as root to default directories
++++++++++++++++++++++++++++++++++++++

This method will install pyexpander on your systems default python library and
binary directories.

Advantages:

- You don't have to modify environment variables in order to use pyexpander.
- All users on your machine can easily use pyexpander.

Disadvantages:

- You must have root or administrator permissions to install pyexpander.
- Files of pyexpander are mixed with other files from your system in the same
  directories making it harder to uninstall pyexpander.

For installing pyexpander this way, as user "root" enter::

  python setup.py install

Install to a separate directory
+++++++++++++++++++++++++++++++

In this case all files of pyexpander will be installed to a separate directory.

Advantages:

- All pyexpander files are below a directory you specify, making it easy to uninstall
  pyexpander.
- If you have write access that the directory, you don't need root or
  administrator permissions.

Disadvantages:

- Each user on your machine who wants to use pyexpander must have the correct
  settings of the environment variables PATH and PYTHONPATH.

For installing pyexpander this way, enter::

  python setup.py install --prefix <DIR>

where <DIR> is your install directory.

In order to use pyexpander, you have to change the environment variables PATH and
PYTHONPATH. Here is an example how you could do this::

  export PATH=<DIR>/bin:$PATH
  export PYTHONPATH=<DIR>/lib/python<X.Y>/site-packages:$PYTHONPATH

where <DIR> is your install directory and <X.Y> is your python version number.
You get your python version with this command::

  python -c 'from sys import *;stdout.write("%s.%s\n"%version_info[:2])'

You may want to add the environment settings ("export...") to your shell setup,
e.g. $HOME/.bashrc or, if your are the system administrator, to the global
shell setup.

Install in your home
++++++++++++++++++++

In this case all files of pyexpander are installed in a directory in your home called
"pyexpander".

Advantages:

- All pyexpander files are below $HOME/pyexpander, making it easy to uninstall pyexpander.
- You don't need root or administrator permissions.

Disadvantages:

- Only you can use this installation.
- You need the correct settings of environment variables PATH and
  PYTHONPATH.

For installing pyexpander this way, enter::

  python setup.py install --home $HOME/pyexpander

You must set your environment like this::

  export PATH=$HOME/pyexpander/bin:$PATH
  export PYTHONPATH=$HOME/pyexpander/lib/python:$PYTHONPATH

You may want to add these lines to your shell setup, e.g. $HOME/.bashrc.

