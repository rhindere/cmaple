#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

amp.py implements Cisco AMP specific REST functionality.
Generic REST functionality is inherited by sub classing RestBase.

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

from cmaple.rest_base import RestBase
import sys
import re
import cmaple.tree_helpers as tree_helpers
from cmaple.tree_helpers import set_default as sd
import cmaple.amp.amp_helpers as amp_helpers
from cmaple.amp.amp_api_resources import amp_path_model
import cmaple.input_validations as input_validations
import cmaple.output_transforms as output_transforms
import json
import urllib3
from pprint import pprint, pformat
import logging
from autologging import logged, traced
from autologging import TRACE
import time
import base64
from objectpath import *

#Define global variables...
_DEFAULT_GET_ITEM_LIMIT = 25

# Create a logger tree.fmc...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))

@logged(logger)
@traced(logger)
class AMP(RestBase):

    """
    This class defines the API interface for the FMC.

    Inherits generic REST functionality from RestBase.

    Overrides methods in RestBase where necessary.

    Method names not beginning with "_" are made available to cmaple_cli.py for use in operations config files.

    """

    def __init__(self, **kwargs):

        """__init__ receives a kwargs dict to define parameters.  This allows __init__ to pass these parameters
        to the superclass.

        Returns an AMP leaf object.

        *Parameters*

        AMP_host: string, keyword, default=None
            The ip address or fqdn of ThreatGrid
        AMP_API_client_ID: string, keyword, default=None
            The AMP API client ID
        AMP_API_key: string, keyword, default=None
            The AMP API key.
        API_path_delimiter: string, keyword, default='/'
            The default delimiter for the API path.
        API_version: string, keyword, default='v2'
            The API version supported by the target ThreatGrid.
        verify: boolean, keyword, default=False
            If True, verify the certificate.  If False disable verification.
        default_get_item_limit: integer, keyword, default=400
            The default number of items to request in a GET request.
        rpm_retries: integer, keyword, default=5
            The number of times to retry in response to a 429 error.
        backoff_timer: integer, keyword, default=30
            The interval to wait between retry attempts
        persist_responses: boolean, keyword, default=True
            If True, responses will be pickle persisted by url into the leaf's working directory.
        restore_responses: boolean, keyword, default=False
            If True, pickled persistent responses will be restored prior to all other operations.
        leaf_dir: string, keyword, default=None
            Provided by CMapleTree when this leaf type is instantiated.  Contains the directory where working files
            for the leaf instance are stored.
        """

        kwarg_defaults = {'AMP_host': None, 'AMP_API_client_ID': None, 'AMP_API_key': None, 'API_path_delimiter': '/',
                          'API_version': 'v1', 'verify': False, 'default_get_item_limit': 400, 'rpm_retries': 5,
                          'backoff_timer': 30, 'persist_responses': True, 'restore_responses': False,
                          'leaf_dir': None}

        for key, val in kwargs.items():
            kwarg_defaults[key] = val

        self.__dict__.update(kwarg_defaults)

        super(AMP, self).__init__()

        # Attributes inherited from leaf_base to override in this class
        self.next_link_query = '$..next'
        self.credentials_dict = {'username': self.AMP_API_client_ID, 'password': self.AMP_API_key}

        if not self.verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disables insecure warning for self signed certs...
        self._url_host = 'https://' + self.AMP_host + '/'
        self.request_headers = {"ACCEPT":"application/json", "Content-Type":"application/json", "Authorization":""}
        self._auth_headers = self.request_headers
        self._auth_token_time = None
        self._requests_per_minute_time = None
        self._requests_counter = 0
        self._auth_token = None
        self._refresh_token = None
        self._refresh_token_count = 0
        self.path_root = self._url_host
        self._API_path_keywords_list = []
        # Build the reference dictionaries...

    @logged(logger)
    @traced(logger)
    def _request_wrapper(self, recursed=False, **kwargs):

        """Wraps all requests for an AMP leaf in order to handle AMP specifics.
        This should only be called by internal methods.

        *Parameters*

        recursed: boolean, keyword, default=False
            Signals if this is the top level call.
        \*\*kwargs: dictionary
            Used to pass through arguments to wrapped methods.
        """

        if not recursed:

            for i in range(1, self.rpm_retries):
                response_dict, status, include_filtered, exclude_filtered, cache_hit = \
                    self._request_wrapper(recursed=True, **kwargs)
                if response_dict['status_code'] == 429 and not exclude_filtered:
                    # Pop the url from the responses_dict so we don't trigger a cache hit on the next request...
                    self.responses_dict.pop(kwargs['url'])
                    if i == (self.rpm_retries - 1):
                        logger.error('Requests per minute code 429 retry count exceeded.  Exiting...')
                        sys.exit()
                    logger.info(
                        'AMP reports requests per minute exceeding 120.  Sleeping for self._backoff_timer seconds...')
                    time.sleep(self.backoff_timer)
                else:
                    next_link = tree_helpers.get_jsonpath_values(self.next_link_query, response_dict)

                    next_url = None

                    if next_link:
                        next_url = next_link[0][0]
                        response_dict['next_link'] = next_url
                    else:
                        next_url = None

                    return response_dict, status, include_filtered, exclude_filtered, cache_hit, next_url
        else:
            return tree_helpers.process_json_request(**kwargs)

    @logged(logger)
    @traced(logger)
    def _get_child_urls(self,response_dict, parent_url):

        """This method retrieves the url for all child objects of this response.
        This should only be called by internal methods.

        Returns: child_url for this anomalous type

        *Parameters*

        response_dict: dictionary
            The response for which to find child urls.
        parent_url: string
            The parent url of this response.  Used to prevent circular object references.
        """

        child_links = tree_helpers.get_objectpath_values('$..links', response_dict)
        child_urls = []
        child_types = {}
        for child_link in child_links:
            for key, val in child_link.items():
                if not val == parent_url:
                    child_urls.append(val)
                    if key not in child_types:
                        child_types[key] = {'urls': [], 'type_dicts': []}
                    child_types[key]['urls'].append(val)
                    child_types[key]['type_dicts'].append({key: val})
        return child_urls, child_types
