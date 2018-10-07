#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

threatgrid.py implements Cisco ThreatGrid specific REST functionality.
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
import cmaple.threatgrid.threatgrid_helpers as threatgrid_helpers
#from cmaple.threatgrid.threatgrid_api_resources import threatgrid_path_model
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
_API_AUTH_PATH = '/api/fmc_platform/{API_version}/auth/generatetoken'
_DEFAULT_GET_ITEM_LIMIT = 25

# Create a logger tree.fmc...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))

@logged(logger)
@traced(logger)
class TG(RestBase):

    """
    This class defines the API interface for the FMC.

    Inherits generic REST functionality from RestBase.

    Overrides methods in RestBase where necessary.

    Method names not beginning with "_" are made available to cmaple_cli.py for use in operations config files.

    """

    def __init__(self, **kwargs):

        """__init__ receives a kwargs dict to define parameters.  This allows __init__ to pass these parameters
        to the superclass.

        Returns a ThreatGrid leaf object.

        Parameters
        ----------
        TG_host: string, keyword, default=None
            The ip address or fqdn of ThreatGrid
        TG_API_key: string, keyword, default=None
            The ThreatGrid API key.
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

        kwarg_defaults = {'TG_host': None, 'TG_API_key': None, 'API_path_delimiter': '/', 'API_version': 'v2',
                          'verify': False, 'default_get_item_limit': 400, 'rpm_retries': 5, 'backoff_timer': 30,
                          'persist_responses': True, 'restore_responses': False, 'leaf_dir': None}

        for key, val in kwargs.items():
            kwarg_defaults[key] = val

        self.__dict__.update(kwarg_defaults)

        super(TG, self).__init__()

        # Attributes inherited from leaf_base to override in this class
        self.next_link_query = '$..next'
        self.credentials_dict = None

        self.TG_host = input_validations.validate_ip_host(self.TG_host)
        self.TG_credentials_dict = {}
        if not self.verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disables insecure warning for self signed certs...
        self._url_host = 'https://' + self.TG_host + '/'
        self.request_headers = {}
        self._auth_headers = self.request_headers
        self._auth_token_time = None
        self._requests_per_minute_time = None
        self._requests_counter = 0
        self._auth_token = None
        self._refresh_token = None
        self._refresh_token_count = 0
        self.path_root = self._url_host
        self._API_path_keywords_list = []

    @logged(logger)
    @traced(logger)
    def _request_wrapper(self, recursed=False, **kwargs):

        """Wraps all requests for a TG leaf in order to handle TG specifics.
        This should only be called by internal methods.

        Parameters
        ----------
        recursed: boolean, keyword, default=False
            Signals if this is the top level call.
        **kwargs: dictionary
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
                        'TG reports requests per minute exceeding 120.  Sleeping for self._backoff_timer seconds...')
                    time.sleep(self.backoff_timer)
                else:
                    return response_dict, status, include_filtered, exclude_filtered, cache_hit
        else:
            return tree_helpers.process_json_request(**kwargs)
