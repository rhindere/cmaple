#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

rest_base.py implements generic REST functionality.  The class TerminalBase
is designed to be sub classed only.

Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied."""

__author__ = "Ron Hinderer (rhindere@cisco.com)"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco DEVNET"

import sys
import os
import re
import cmaple.tree_helpers as tree_helpers
from cmaple.tree_helpers import set_default as sd
import cmaple.input_validations as input_validations
import cmaple.output_transforms as output_transforms
from collections import OrderedDict
from pprint import pprint, pformat
import logging
from autologging import logged, traced
from autologging import TRACE
# fabric and invoke imports...
from fabric import Connection
from fabric.tasks import task, Task
from fabric.group import SerialGroup, ThreadingGroup
from invoke import Responder

import time

# Create a logger...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))
# Define global variables


@logged(logger)
@traced(logger)
class TerminalObjectsMaster(object):

    """
    Under construction.
    """

    def __init__(self):

        """__init__
        Under Construction.
        """

        self.index = {}
        self.index['members'] = {}
        self.index['Server'] = {'_class': Server, 'members': {}}
        self.index['SerialServerGroup'] = {'_class': SerialServerGroup, 'members': {}}
        self.index['ThreadingServerGroup'] = {'_class': ThreadingServerGroup, 'members': {}}
        self.index['Credential'] = {'_class': Credential, 'members': {}}
        self.index['User'] = {'_class': User, 'members': {}}
        self.index['CMD'] = {'_class': CMD, 'members': {}}
        self.index['CMDSet'] = {'_class': CMDSet, 'members': {}}
        self.index['CMDWatcher'] = {'_class': CMDWatcher, 'members': {}}
        self.index['CMDResponder'] = {'_class': CMDResponder, 'members': {}}
        self.index['CMDResult'] = {'_class': CMDResult, 'members': {}}
        self.index['PeriodicCMDSet'] = {'_class': PeriodicCMDSet, 'members': {}}

    def add_object(self, _type, name, **kwargs):

        """
        Under construction.
        """

        if name not in self.index['members']:
            self.index[_type]['members'][name] = self.index[_type]['_class'](name, **kwargs)
            return self.index[_type]['members'][name]
        else:
            return None


@logged(logger)
@traced(logger)
class User(object):

    """
    Under construction.
    """

    def __init__(self, name, user=None):

        """__init__
        Under Construction.
        """

        self.name = name
        self.user = user


@logged(logger)
@traced(logger)
class Server(object):

    """
    Under construction.
    """

    def __init__(self, name, host=None, ip=None, port=22, protocol='ssh'):

        """__init__
        Under Construction.
        """

        self.name = name
        self.host = host
        self.port = port
        self.protocol = protocol


@logged(logger)
@traced(logger)
class SerialServerGroup(object):
    """
    Under construction.
    """

    def __init__(self, name):
        """__init__
        Under Construction.
        """

        # Override these in the parent class...
        self.name = name
        self.group = SerialGroup()
        self.connections = []

    def add_server(self, server, user, credential):

        connection = Connection(server.host, user=user.user, connect_kwargs=credential.connect_kwargs)
        self.group.append(connection)

    def run_cmd(self, cmd):

        return cmd.run_cmd(self.group)


@logged(logger)
@traced(logger)
class ThreadingServerGroup(object):
    """
    Under construction.

    """

    def __init__(self):
        """__init__
        Under Construction.

        """

        # Override these in the parent class...
        pass


@logged(logger)
@traced(logger)
class Credential(object):
    """
    Under construction.
    """

    def __init__(self, name, credential_type=None, credential=None):
        """__init__
        Under Construction.
        """

        # Override these in the parent class...
        self.name = name
        self.credential = credential
        if credential_type == 'password':
            self.connect_kwargs = {'password': self.credential,
                                   }


@logged(logger)
@traced(logger)
class CMD(object):
    """
    Under construction.

    """

    def __init__(self, name, cmd=None, shell=False):
        """__init__
        Under Construction.
        """

        # Override these in the parent class...
        self.name = name
        self.cmd = cmd
        self.watchers = []
        self.responders = []
        self.shell = shell

    def run_cmd(self, group):

        # print('rc =', self.cmd)
        # print('rc =', self.responders)
        # print('rc =', self.watchers)
        #responder = Responder(pattern='Password', response='C1sc0123')
        # for conn in group:
            # conn.open()
            # print(conn.is_connected)
            # conn.run(self.cmd, pty=True, echo_stdin=True, watchers=self.responders, shell=False, echo=True)
            # print(conn.is_connected)

        return group.run(self.cmd, pty=True, echo_stdin=True, watchers=self.responders, shell=False, echo=True)

    def add_watcher(self, watcher):

        self.watchers.append(watcher)
        self.responders.append(watcher.responder)


@logged(logger)
@traced(logger)
class CMDSet(object):
    """
    Under construction.

    """

    def __init__(self, name, **kwargs):
        """__init__
        Under Construction.

        """

        # Override these in the parent class...
        self.name = name
        self.cmds = []

    def add_cmd(self, cmd):

        self.cmds.append(cmd)

    def run_cmd(self, group):

        results = {}
        for cmd in self.cmds:
            result = cmd.run_cmd(group)
            results.update(result)

        return results


@logged(logger)
@traced(logger)
class RunSet(object):
    """
    Under construction.
    """

    def __init__(self):
        """__init__
        Under Construction.
        """

        # Override these in the parent class...
        pass


@logged(logger)
@traced(logger)
class CMDWatcher(object):
    """
    Under construction.
    """

    def __init__(self, name, pattern=None, response=None):
        """__init__
        Under Construction.
        """

        self.name = name
        self.pattern = pattern
        self.response = response
        self.responder = Responder(pattern=pattern, response=response)


@logged(logger)
@traced(logger)
class CMDResponder(object):
    """
    Under construction.
    """

    def __init__(self, name, pattern=None, response=None):
        """__init__
        Under Construction.
        """

        # Override these in the parent class...
        self.name = name
        self.responder = Responder(pattern=pattern, response=response)


@logged(logger)
@traced(logger)
class CMDResult(object):
    """
    Under construction.

    """

    def __init__(self):
        """__init__
        Under Construction.

        """

        # Override these in the parent class...
        pass


@logged(logger)
@traced(logger)
class PeriodicCMDSet(object):
    """
    Under construction.

    """

    def __init__(self):
        """__init__
        Under Construction.

        """

        # Override these in the parent class...
        pass


