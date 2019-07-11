#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

win_base.py implements generic REST functionality.  The class TerminalBase
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

from cmaple.terminal_objects import *
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
class TerminalBase(object):

    """
    This class defines generic Fabric API functionality.

    Classes sub classing this class will need to override specific methods and properties as called out in the
    method docstrings and inline comments.

    Method names not beginning with "_" are made available to cmaple_cli.py for use in operations config files.

    """

    def __init__(self):

        """__init__ TerminalBase inherits arguments from the parent class.  All argument validation is
        performed by the parent class.
        """

        # Override these in the parent class...
        self.credentials_dict = {}

        # These variables are inherited by the parent class...
        self.responses_dict = {}
        self.response_index = {}
        self._connection = None

        if self.restore_responses:
            tree_helpers.restore_responses(self.leaf_dir, self.responses_dict)

    def _connection_wrapper(self):
        """Must override in parent class

        *****Inherited from TerminalBase...*****

        """

        pass

    def _run_wrapper(self):
        """Must override in parent class

        *****Inherited from TerminalBase...*****

        """

        pass

    @logged(logger)
    @traced(logger)
    def _connect_terminal(self, kwargs):
        """Optional override in parent class.  Prepares the cmd

        *****Inherited from TerminalBase...*****

        Returns: a fabric connection object

        Establishes a terminal connection to the target host.
        This should only be called by internal methods.

        *Parameters*

        fabric_kwargs: dictionary, keyword, default=None
            The main fabric connection keywords.
        connect_kwargs: dictionary, keyword, default=None
            The parameters passed through by fabric to paramiko ssh.
        """

        connect_kwargs = {'password': kwargs['ssh_password'],
                          }

        self._connection = Connection(kwargs['ssh_host'], user=kwargs['ssh_username'], port=kwargs['ssh_port'],
                                      connect_kwargs=connect_kwargs)

        return self._connection

    @logged(logger)
    @traced(logger)
    def run_cmd(self, cmd=None, cmd_expect=None, responses_dict=None):
        """Optional override in parent class.  Prepares the cmd

        *****Inherited from TerminalBase...*****

        Prepares the cmd by replacing parameter placeholders with values.
        This should only be called by internal methods.

        *Parameters*

        cmd: string, keyword, default=None
            The cmd to prepare.
        params: dictionary, keyword, default=None
            The parameters dictionary.
        """

        if responses_dict is None:
            responses_dict = self.responses_dict

        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            self._run_wrapper(cmd=cmd, cmd_expect=cmd_expect, responses_dict=responses_dict)

        return response_dict

    @logged(logger)
    @traced(logger)
    def run_cmd(self, cmd=None, cmd_expect=None, responses_dict=None):
        """Optional override in parent class.  Prepares the cmd

        *****Inherited from TerminalBase...*****

        Prepares the cmd by replacing parameter placeholders with values.
        This should only be called by internal methods.

        *Parameters*

        cmd: string, keyword, default=None
            The cmd to prepare.
        params: dictionary, keyword, default=None
            The parameters dictionary.
        """

        if responses_dict is None:
            responses_dict = self.responses_dict

        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            self._run_wrapper(cmd=cmd, cmd_expect=cmd_expect, responses_dict=responses_dict)

        return response_dict

    @logged(logger)
    @traced(logger)
    def _task_factory(self, base_paths=None, params=None, responses_dict=None, query_dict=None):

        """Gets threatgrid samples.

        Returns: a responses dictionary

        *Parameters*

        sample_search_paths: dictionary, keyword, default=None
            Defines the search parameters (e.g. checksum=<sha256>).
        params: dictionary, keyword, default=None
            Defines the search scope parameters (e.g. before=<strftime>).
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        pass

    @logged(logger)
    @traced(logger)
    def chained_smart_send(self, base_paths=None, params=None, responses_dict=None, query_dict=None):

        """Gets threatgrid samples.

        Returns: a responses dictionary

        *Parameters*

        sample_search_paths: dictionary, keyword, default=None
            Defines the search parameters (e.g. checksum=<sha256>).
        params: dictionary, keyword, default=None
            Defines the search scope parameters (e.g. before=<strftime>).
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        def process_base_cmd(cmd_so_far, base_cmd, query_dict):
            pass

    def _recurse_CLI_child_cmds(self, url, use_cache=True, end_path_regex=None, include_filter_regex=None,
                                exclude_filter_regex=None, stop_on_error=False, filtered=False, cache_hit=False,
                                get_item_limit=None, responses_dict=None, parent_url='', parent_recursion_stack=[]):

        """Handles recursion of a given url path.  Normally not called directly but from a wrapper method.
        Begins at given API url path and recursively GET walks path and child paths until complete.  Automatically
        handles pagination and discovery of child urls.

        *****Inherited from RestBase...*****

        Returns a Python dictionary object containing the response results for all url path GETs.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        *Parameters*

        url : string
            The starting url of the path to recurse.  Must be a fully valid FMC api "GET" path.  url can include the
            host prefix or start from the resource path.  If the host prefix is missing, it will be added
            automatically.
        use_cache: boolean, keyword, default=False
            If set to True, any path that has already been requested will not generate a new request
        include_filter_regex: string, keyword, default=None
            A regex string defining which urls to include in walk.
        exclude_filter_regex: string, keyword, default=None
            A regex string defining which urls to exclude from walk.
        stop_on_error: boolean, keyword, default=False
            If set to True, walk will halt when a non positive status code response is received.
        get_item_limit: integer, keyword, default=25
            Specifies the number of items to return for each GET request.
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        parent_url: string, keyword, default=''
            Specifies the url of the parent of this child url.  Used to prevent recursion loops where the API model
            contains a circular object.
        """

        # if responses_dict is None:
        #     responses_dict = self.responses_dict
        #
        # if self.path_root not in url:
        #     url = self.path_root + url
        #
        # while True:
        #     logger.debug('recurse_API_child_gets: recursing with url %s' % (url))
        #     response_dict, status, include_filtered, exclude_filtered, cache_hit, next_url = \
        #         self._request_wrapper(recursed=False, url=url, responses_dict=responses_dict,
        #                               headers=self.request_headers,
        #                               method='get', credentials_dict=self.credentials_dict,
        #                               verify=self.verify, success_status_code=200,
        #                               include_filter_regex=include_filter_regex,
        #                               exclude_filter_regex=exclude_filter_regex,
        #                               use_cache=use_cache, stop_on_error=stop_on_error,
        #                               API_path_keywords_list=self._API_path_keywords_list,
        #                               get_item_limit=sd(locals(), 'get_item_limit', self))
        #
        #     logger.debug(pformat(response_dict))
        #
        #     child_urls = []
        #     child_types = []
        #     # Insert the parent url so we don't add it as a child of a child....securityzones...physical interfaces
        #     if response_dict['json_dict']:
        #         child_urls, child_types = self._get_child_urls(response_dict, url)
        #     response_dict['child_urls'] = child_urls
        #     response_dict['child_types'] = child_types
        #
        #     if status and self.persist_responses:
        #         self.response_counter += 1
        #         tree_helpers.persist_response(self.leaf_dir, self.path_root, self.response_counter, response_dict)
        #
        #     for child_url in child_urls:
        #         if child_url:
        #             # Check to make sure we aren't in a circular reference situation...
        #             if child_url == parent_url:
        #                 logger.warning('Circular reference detected for url %s' % url)
        #                 continue
        #             logger.debug('Recursing into recurse_API_child_gets with child url = %s' % (child_url))
        #             self._recurse_API_child_gets(child_url, include_filter_regex=include_filter_regex,
        #                                          exclude_filter_regex=exclude_filter_regex,
        #                                          use_cache=use_cache, stop_on_error=stop_on_error,
        #                                          get_item_limit=sd(locals(), 'get_item_limit', self),
        #                                          responses_dict=responses_dict, parent_url=url,
        #                                          parent_recursion_stack=parent_recursion_stack)
        #
        #     if next_url is not None:
        #         url = next_url
        #     else:
        #         break

        pass

    def walk_CLI_run_cmds(self, url, end_path_regex=None, include_filter_regex=None, exclude_filter_regex=None,
                           use_cache=True, stop_on_error=False, get_item_limit=None,
                           responses_dict=None):

        """Begins at given API url path and recursively GET walks path and child paths until complete.

        *****Inherited from RestBase...*****

        Returns a Python dictionary object containing the response results for all url path GETs.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        *Parameters*

        url : string
            The starting url of the path to walk.  Must be a fully valid FMC api "GET" path.  url can include the
            host prefix or start from the resource path.  If the host prefix is missing, it will be added
            automatically.
        use_cache: boolean, keyword, default=False
            If set to True, any path that has already been requested will not generate a new request
        include_filter_regex: string, keyword, default=None
            A regex string defining which urls to include in walk.
        exclude_filter_regex: string, keyword, default=None
            A regex string defining which urls to exclude from walk.
        stop_on_error: boolean, keyword, default=False
            If set to True, walk will halt when a non positive status code response is received.
        get_item_limit: integer, keyword, default=25
            Specifies the number of items to return for each GET request.
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        # logger.debug('walk_API_path_gets calling recurse_API_child_gets with url %s...' % (url))
        #
        # if responses_dict is None:
        #     responses_dict = self.responses_dict
        #
        # if self.path_root not in url:
        #     url = self.path_root + url
        # self._recurse_API_child_gets(url, include_filter_regex=include_filter_regex,
        #                              exclude_filter_regex=exclude_filter_regex,
        #                              use_cache=use_cache, stop_on_error=stop_on_error,
        #                              get_item_limit=sd(locals(), 'get_item_limit', self),
        #                              responses_dict=responses_dict)
        #
        # return responses_dict

        pass

