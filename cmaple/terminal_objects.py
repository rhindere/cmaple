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
# paramiko imports...
import traceback
import paramiko
from paramiko_expect import SSHClientInteraction
from multissh import MultiSSHRunner

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
        self.index['Expect'] = {'_class': Expect, 'members': {}}
        self.index['CMD'] = {'_class': CMD, 'members': {}}
        self.index['CMDSet'] = {'_class': CMDSet, 'members': {}}
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

    def __init__(self, name, server=None, hostname=None, prompt=None, port=22, protocol='ssh'):

        """__init__
        Under Construction.
        """

        self.name = name
        self.server = server
        self.hostname = hostname
        self.prompt = prompt
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
        self.group = []

    def add_server(self, server, user, credential):

        self.group.append({'server': server, 'user': user, 'credential': credential, 'client': None})

    def run_cmd(self, cmd):

        return cmd.run_cmd(self.group)


@logged(logger)
@traced(logger)
class ThreadingServerGroup(SerialServerGroup):
    """
    Under construction.
    """

    def __init__(self, *args, **kwargs):
        """__init__
        Under Construction.
        """
        super(ThreadingServerGroup, self).__init__(*args, **kwargs)

        self.multissh_runner = None
        self.multissh_len = None

    def run_cmd(self, cmd):

        if self.multissh_runner is None:
            self.multissh_runner = MultiSSHRunner(processes=len(self.group))
        for server in self.group:
            self.multissh_runner.add_ssh_job(server['server'].hostname,
                                             connect_timeout=10, username=server['user'].user,
                                             password=server['credential'].credential,
                                             interaction=cmd.run_cmd)

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
        self.credential_type = credential_type


@logged(logger)
@traced(logger)
class Expect(object):
    """
    Under construction.
    """

    def __init__(self, name, pattern=None, response=None, callback=None):
        """__init__
        Under Construction.
        """

        self.name = name
        self.pattern = pattern
        self.response = response
        self.callback = callback


@logged(logger)
@traced(logger)
class CMD(object):
    """
    Under construction.
    """

    def __init__(self, name, cmd=None, callback=None):
        """__init__
        Under Construction.
        """

        self.name = name
        self.cmd = cmd
        self.pre_expect_pattern = None
        self.post_expect_pattern = None
        self.place_holder_objects = {}
        self.callback = callback

    def replace_place_holders(self, place_holder_string):
        if place_holder_string is None:
            return None
        new_string = place_holder_string
        place_holders = re.findall(r'\{([^}]+)\}', place_holder_string)
        for place_holder in place_holders:
            place_holder = re.sub(r'\{|\}', '', place_holder)
            class_name, attr_name = place_holder.split('.')
            replace_val = getattr(self.place_holder_objects[class_name], attr_name)
            new_string = new_string.replace('{'+place_holder+'}', replace_val)
        return new_string

    def run_cmd(self, group):
        # Use SSH client to login
        results = {}
        error_encountered = False
        errors = {'connect': [], 'pre_expect': [], 'send_command': [], 'post_expect': []}
        for server in group.group:
            self.place_holder_objects['server'] = server['server']
            self.place_holder_objects['user'] = server['user']
            self.place_holder_objects['credential'] = server['credential']
            hostname = server['server'].server
            prompt = server['server'].prompt
            username = server['user'].user
            password = server['credential'].credential
            print(hostname)
            if hostname not in results:
                results[hostname] = []
            client = None
            if server['client'] is None or (server['client'] is not None
                                            and not server['client'].get_transport().is_active()):
                logger.debug('need a new client for server %s...', hostname)
                # Create a new SSH client object
                server['client'] = paramiko.SSHClient()

                # Set SSH key parameters to auto accept unknown hosts
                server['client'].load_system_host_keys()
                server['client'].set_missing_host_key_policy(paramiko.AutoAddPolicy())

                # Connect to the host
                try:
                    server['client'].connect(hostname=hostname, username=username, password=password)
                    server['interact'] = SSHClientInteraction(server['client'], timeout=10, display=True)
                    server['interact'].expect(prompt)
                except Exception as e:
                    results[hostname].append({'hostname': hostname, 'command': None, 'result': 'connection failed',
                                              'error': True, 'error_message': e, 'error_stage': 'connect'}
                                             )
                    errors['connect'].append(results[-1])
                    error_encountered = True
                    logger.error('Error connecting to server %s and command %s with exception %s' %
                                 (hostname, self.cmd, e))
                    continue

            else:
                logger.debug('client is good for server %s...' % hostname)

            client = server['client']
            interact = server['interact']

            send_cmd = self.replace_place_holders(self.cmd)
            pre_expect_pattern = self.replace_place_holders(self.pre_expect_pattern)
            post_expect_pattern = self.replace_place_holders(self.post_expect_pattern)

            logger.debug('starting pre_expect with pattern %s for command %s' % (self.pre_expect_pattern, self.cmd))
            if self.pre_expect_pattern is not None:
                try:
                    logger.debug('new pre_expect_pattern %s', pre_expect_pattern)
                    interact.expect(pre_expect_pattern)
                    logger.debug('passed pre_expect with pattern %s for command %s' % (pre_expect_pattern, self.cmd))
                except Exception as e:
                    results[hostname].append({'hostname': hostname, 'command': self.cmd,
                                              'send_cmd': send_cmd,
                                              'pre_expect_pattern': pre_expect_pattern,
                                              'post_expect_pattern': post_expect_pattern,
                                              'result': interact.current_output_clean,
                                              'error': True, 'error_message': e, 'error_stage': 'pre_expect'}
                                             )
                    errors['pre_expect'].append(results[-1])
                    error_encountered = True
                    logger.error('Error with pre expect output %s for server %s and command %s with exception %s' %
                                 (pre_expect_pattern, hostname, self.cmd, e))
                    continue

            try:
                logger.debug('new cmd %s', send_cmd)
                interact.send(send_cmd)
                logger.debug('starting post_expect with pattern %s for command %s' % (self.post_expect_pattern, self.cmd))
            except Exception as e:
                results[hostname].append({'hostname': hostname, 'command': self.cmd,
                                          'send_cmd': send_cmd,
                                          'pre_expect_pattern': pre_expect_pattern,
                                          'post_expect_pattern': post_expect_pattern,
                                          'result': interact.current_output_clean,
                                          'error': True, 'error_message': e, 'error_stage': 'send_command'}
                                         )
                errors['send_command'].append(results[-1])
                error_encountered = True
                logger.error('Error sending command %s for server %s with exception %s' %
                             (self.cmd, hostname, e))
                continue

            if self.post_expect_pattern is not None:
                try:
                    logger.debug('new post_expect_pattern %s', post_expect_pattern)
                    interact.expect(post_expect_pattern)
                    logger.debug('passed post_expect with pattern %s for command %s' % (post_expect_pattern, self.cmd))
                except Exception as e:
                    results[hostname].append({'hostname': hostname, 'command': self.cmd,
                                              'send_cmd': send_cmd,
                                              'pre_expect_pattern': pre_expect_pattern,
                                              'post_expect_pattern': post_expect_pattern,
                                              'result': interact.current_output_clean,
                                              'error': True, 'error_message': e, 'error_stage': 'post_expect'}
                                             )
                    errors['post_expect'].append(results[-1])
                    error_encountered = True
                    logger.error('Error expecting output %s for server %s and command %s with exception %s' %
                                 (post_expect_pattern, hostname, self.cmd, e))
                    continue

            results[hostname].append({'hostname': hostname, 'command': self.cmd,
                                      'send_cmd': send_cmd,
                                      'pre_expect_pattern': pre_expect_pattern,
                                      'post_expect_pattern': post_expect_pattern,
                                      'result': interact.current_output_clean,
                                      'error': False, 'error_message': None, 'error_stage': None}
                                     )
            logger.debug('Success sending command %s for server %s' %
                         (self.cmd, hostname))

        return results, error_encountered, errors

    def add_pre_expect(self, expect):

        self.pre_expect_pattern = expect.pattern

    def add_post_expect(self, expect):

        self.post_expect_pattern = expect.pattern


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
        self.place_holder_objects = {}

    def add_cmd(self, cmd):

        self.cmds.append(cmd)

    def run_cmd(self, group):
        results = []
        errors = None
        error_encountered = False
        for cmd in self.cmds:
            cmd_result, cmd_error_encountered, cmd_errors = cmd.run_cmd(group)
            results.append(cmd_result)
            if cmd_error_encountered:
                errors.extend(cmd_errors)
                error_encountered = True
        for server in group.group:
            try:
                if server['client'] is not None:
                    server['client'].close()
            except Exception as e:
                logger.error('Error closing connection for server %s and command set %s with exception %s' % 
                             (server['hostname'], self.name, e))
        return {'results': results, 'error_encountered': error_encountered, 'errors': errors}

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


