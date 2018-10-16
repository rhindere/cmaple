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

        *Parameters*

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
                        'TG reports requests per minute exceeding 120.  Sleeping for self._backoff_timer seconds...')
                    time.sleep(self.backoff_timer)
                else:
                    # Derive next_url
                    next_url = None

                    if 'data' in response_dict['json_dict'] \
                            and 'current_item_count' in response_dict['json_dict']['data']:
                        current_item_count = response_dict['json_dict']['data']['current_item_count']
                        index = response_dict['json_dict']['data']['index']
                        items_per_page = response_dict['json_dict']['data']['items_per_page']
                        this_url = response_dict['url']
                        if current_item_count < items_per_page:
                            next_url = None
                        else:
                            offset = items_per_page + index
                            if 'offset=' in this_url:
                                next_url = re.sub(r'offset=[^&]+', 'offset=' + str(offset), this_url)
                            else:
                                next_url = '{}&{}{}'.format(this_url, 'offset=', str(offset))
                        print('next_url=',next_url)
                    return response_dict, status, include_filtered, exclude_filtered, cache_hit, next_url
        else:
            return tree_helpers.process_json_request(**kwargs)


    @logged(logger)
    @traced(logger)
    def get_datetime_obj(self, year=2018, month=1, day=1, hour=0, minute=0, second=0, tz_str='Etc/GMT-0'):

        """Gets a Python datetime object representing the given parameters.

        Returns: Python datetime object

        *Parameters*

        year: integer, keyword, default=2018
            The datetime year
        month: integer, keyword, default=1
            The datetime month
        day: integer, keyword, default=1
            The datetime day
        hour: integer, keyword, default=0
            The datetime hour
        minute: integer, keyword, default=0
            The datetime minute
        second: integer, keyword, default=0
            The datetime second
        tz_str: string, keyword, default=Etc/GMT-0
            The datetime time zone
        """

        _datetime = tree_helpers.get_datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                                              tz_str=tz_str)

        return _datetime


    @logged(logger)
    @traced(logger)
    def get_datetime_str(self, year=2018, month=1, day=1, hour=0, minute=0, second=0, tz_str='Etc/GMT-0'):

        """Gets a datetime string for the given parameters.

        Returns: A datetime string formatted with strftime

        *Parameters*

        year: integer, keyword, default=2018
            The datetime year
        month: integer, keyword, default=1
            The datetime month
        day: integer, keyword, default=1
            The datetime day
        hour: integer, keyword, default=0
            The datetime hour
        minute: integer, keyword, default=0
            The datetime minute
        second: integer, keyword, default=0
            The datetime second
        tz_str: string, keyword, default=Etc/GMT-0
            The datetime time zone
        """

        _datetime = tree_helpers.get_datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                                              tz_str=tz_str)
        _strftime = tree_helpers.get_strftime(_datetime=_datetime)

        return _strftime


    @logged(logger)
    @traced(logger)
    def get_datetime_now_str(self):

        """Gets a datetime string for the current time formatted with strftime.

        Returns: A datetime string for the current time formatted with strftime

        *Parameters*

        None
        """

        _strftime = tree_helpers.get_strftime()

        return _strftime


    @logged(logger)
    @traced(logger)
    def get_datetime_delta_str(self, _strftime=None, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0,
                               hours=0, weeks=0):

        """Gets a datetime string for the delta with _strftime time formatted with strftime.

        Returns: A datetime string for the current time formatted with strftime

        *Parameters*

        _strftime: string, keyword, default=None
            The base time formatted with strftime
        days: integer, keyword, default=0
            The +- number of days
        seconds: integer, keyword, default=0
            The +- number of seconds
        microseconds: integer, keyword, default=0
            The +- number of microseconds
        milliseconds: integer, keyword, default=0
            The +- number of milliseconds
        minutes: integer, keyword, default=0
            The +- number of minutes
        hours: integer, keyword, default=0
            The +- number of hours
        weeks: integer, keyword, default=0
            The +- number of weeks
        """

        _strftime = tree_helpers.get_strftime_delta(_strftime=_strftime, days=days, seconds=seconds,
                                                    microseconds=microseconds, milliseconds=milliseconds,
                                                    minutes=minutes, hours=hours,
                                                    weeks=weeks)

        return _strftime

    @logged(logger)
    @traced(logger)
    def free_form(self, base_paths=None, id_list=None, element_paths=None, params=None, responses_dict=None):

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

        sample_path = 'api/v2/samples/search'

        url = self._prepare_url(url=sample_path, params=params)

        if responses_dict is None:
            responses_dict = self.responses_dict
        else:
            responses_dict = responses_dict

        for key, val in sample_search_paths.items():
            url = '{}&{}={}'.format(url, key, str(val))
            print(url)
            self.GET_API_path(url=url, responses_dict=responses_dict)

        return responses_dict


    @logged(logger)
    @traced(logger)
    def search_samples(self, sample_search_paths=None, params=None, responses_dict=None):

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

        sample_path = 'api/v2/samples/search'

        url = self._prepare_url(url=sample_path, params=params)

        if responses_dict is None:
            responses_dict = self.responses_dict
        else:
            responses_dict = responses_dict

        for key, val in sample_search_paths.items():
            url = '{}&{}={}'.format(url, key, str(val))
            print(url)
            self.GET_API_path(url=url, responses_dict=responses_dict)

        return responses_dict


    @logged(logger)
    @traced(logger)
    def get_samples(self, params=None, responses_dict=None):

        """Gets threatgrid samples.

        Returns: a responses dictionary

        *Parameters*

        params: dictionary, keyword, default=None
            Defines the search scope parameters (e.g. before=<strftime>).
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        sample_path = 'api/v2/samples'

        sample_path = self._prepare_url(url=sample_path, params=params)

        if responses_dict is None:
            responses_dict = self.responses_dict
        else:
            responses_dict = responses_dict

        responses = self.get_all_items(url=sample_path, responses_dict=responses_dict)

        return responses


    @logged(logger)
    @traced(logger)
    def walk_samples(self, sample_id_paths=None, params=None, responses_dict=None):

        """Walks threatgrid samples by id.

        Returns: a responses dictionary

        *Parameters*

        sample_id_paths: dictionary, keyword, default=None
            Defines the paths to retrieve for each id.
        params: dictionary, keyword, default=None
            Defines the search scope parameters (e.g. before=<strftime>).
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        sample_path = 'api/v2/samples'

        url = self._prepare_url(url=sample_path, params=params)

        responses = self.get_all_items(url=url)

        ids = tree_helpers.get_jsonpath_values('$..data.items[*].id', responses)

        if responses_dict is None:
            responses_dict = self.responses_dict
        else:
            responses_dict = responses_dict

        for id in ids:
            url = sample_path + '/' + str(id)
            for sample_id_path in sample_id_paths:
                url = url + '/' + sample_id_path
                url = self._prepare_url(url)
                print(url)
                self.GET_API_path(url=url, responses_dict=responses_dict)

        return responses_dict


    @logged(logger)
    @traced(logger)
    def _prepare_url(self, url=None, params=None):

        """Prepares the url by replacing parameter placeholders with values.
        This should only be called by internal methods.

        *Parameters*

        url: string, keyword, default=None
            The url to prepare.
        params: dictionary, keyword, default=None
            The parameters dictionary.
        """

        if not re.match(r'.+?\?[^/]+$', url):
            url = url + '?'
        else:
            url = url + '&'

        if not 'api_key=' in url:
            url = url + ('api_key=%s' % self.TG_API_key)
        else:
            if not 'api_key=%s' % self.TG_API_key in url:
                url = re.sub(r'api_key=[^&]+', 'api_key=%s' % self.TG_API_key, url)

        if params is not None:
            for key, val in params.items():
                url = url + '&{}={}'.format(key, str(val))

        return url
