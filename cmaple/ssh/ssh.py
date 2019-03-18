#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

ssh.py implements Cisco ssh specific ssh functionality.  Generic
ssh functionality is inherited by sub classing FabricBase.

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

from cmaple.terminal_base import TerminalBase
import sys
import re
import cmaple.tree_helpers as tree_helpers
from cmaple.tree_helpers import set_default as sd
import cmaple.ssh.ssh_helpers as ssh_helpers
import cmaple.input_validations as input_validations
import cmaple.output_transforms as output_transforms
from pprint import pformat
import logging
from autologging import logged, traced
import time

#Define global variables...

# Create a logger tree.ssh...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))


@logged(logger)
@traced(logger)
class SSH(TerminalBase):
    """
    This class defines a generic ssh interface.

    Inherits generic primitive functionality from FabricBase.

    Overrides methods in FabricBase where necessary.

    Method names not beginning with "_" are made available to cmaple_cli.py for use in operations config files.

    """

    def __init__(self, **kwargs):

        """__init__ receives a kwargs dict to define parameters.  This allows __init__ to pass these parameters
        to the superclass.

        Returns an ssh object.

        *Parameters*

        ssh_host: string, keyword, default=None
            The ip address or fqdn of the ssh
        ssh_port: integer, keyword, default=443
            The TCP/IP ssh management port
        ssh_username: string, keyword, default=None
            The username for ssh
        ssh_password: string, keyword, default=None
            The password for ssh
        ssh_version: string, keyword, default='v2'
            The target ssh version.
        ssh_key: string, keyword, default='Default'
            The target ssh key.
        verify: boolean, keyword, default=False
            If True, verify the certificate.  If False disable verification.
        persist_responses: boolean, keyword, default=True
            If True, responses will be pickle persisted by url into the leaf's working directory.
        restore_responses: boolean, keyword, default=False
            If True, pickled persistent responses will be restored prior to all other operations.
        leaf_dir: string, keyword, default=None
            Provided by CMapleTree when this leaf type is instantiated.  Contains the directory where working files
            for the leaf instance are stored.
        """

        kwarg_defaults = {'verify': False, 'cmd_retries': 5, 'backoff_timer': 30,
                          'persist_responses': True, 'restore_responses': False, 'leaf_dir': None}

        for key, val in kwargs.items():
            kwarg_defaults[key] = val

        self.__dict__.update(kwarg_defaults)

        super(SSH, self).__init__()

        # Attributes inherited from leaf_base to override in this class

        # Validate critical attributes
        # TODO move these checks into the termminal objects...
        # self.ssh_host = input_validations.validate_ip_host(self.ssh_host)
        # self.ssh_user = input_validations.validate_string_value(self.ssh_username, 'ssh username')
        # self.ssh_password = input_validations.validate_string_value(self.ssh_password, 'ssh password')
        
        # Add class specific attributes
        if self.restore_responses:
            response_cmd = list(self.responses_dict.keys())[0]

    # Methods inherited from leaf_base to override in this class
    ##############################################################################################################
    @logged(logger)
    @traced(logger)
    def _run_wrapper(self, group_list, cmd_list, recursed=False, **kwargs):

        """Wraps all requests for an ssh leaf in order to handle ssh specifics such at re-auth and rate limit.
        This should only be called by internal methods.

        *Parameters*

        recursed: boolean, keyword, default=False
            Signals if this is the top level call.
        \*\*kwargs: dictionary
            Used to pass through arguments to wrapped methods.
        """

        # if not recursed:
        #
        #     pass
        #
        # else:
        #
        return tree_helpers.process_cmd_request(group_list=group_list, cmd_list=cmd_list, **kwargs)

    @logged(logger)
    @traced(logger)
    def _get_child_cmds(self, response_dict, parent_cmd):

        """This method retrieves the url for all child objects of this response.
        This should only be called by internal methods.

        Returns: child_url for this anomalous type

        *Parameters*

        response_dict: dictionary
            The response for which to find child urls.
        parent_url: string
            The parent url of this response.  Used to prevent circular object references.
        """

        pass

    #Begin class specific methods
    ################################################################################################################
    @logged(logger)
    @traced(logger)
    def _get_cmd_dict(self, json_file_path=''):

        """Reads the current json ssh API model into a Python dictionary and build all required reference
        dictionaries.

        Returns a Python dictionary object containing json model.

        Processing the json model file takes up to one minute.  Therefore, this method will check to see if the model
        has changed since the last run.  It it is the same it will restore the json model dictionary and all derived
        reference dictionaries from pickled files.
        
        Pickles all newly created Python dictionaries if required.

        *Parameters*

        json_file_path: string, keyword, default=None
            The path to the json model file.  This file is typically named 'api-docs-sshwithll.json' and obtained
            from the target ssh.  Typically resides in the directory
            /var/opt/CSCOpx/MDC/tomcat/vms/api/api-explorer/api.
            This file provides the API model to MAPLE:ssh which is used for many of the operations to derive urls, etc.
        """

        pass

    @logged(logger)
    @traced(logger)
    def get_all_models_dict(self):
        """Returns the model dictionary created from the model input file.
        
        Returns a Python dictionary created from the json model input file.

        """
        
        return self._models_dict
    
    @logged(logger)
    @traced(logger)
    def get_all_CLI_cmds_list(self):
        """Returns a list of all valid API paths for the ssh host.
        
        Returns a list of all the valid API paths for this ssh host.  Contains the domain id for the ssh but container and object
        will be required as indicated by placeholders {containerUUID} and {objectId}.

        """
        
        return list(self._all_CLI_cmds_list)
