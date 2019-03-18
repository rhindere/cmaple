#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

ssh.py implements Cisco BPS specific REST functionality.  Generic
REST functionality is inherited by sub classing RestBase.

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
import os
import re
import cmaple.tree_helpers as tree_helpers
from cmaple.tree_helpers import set_default as sd
import cmaple.bps.bps_helpers as bps_helpers
import cmaple.input_validations as input_validations
import cmaple.output_transforms as output_transforms
import json
import urllib3
from pprint import pprint, pformat
import logging
from autologging import logged, traced
from autologging import TRACE
import time
from objectpath import *
from collections import OrderedDict
import _pickle

#Define global variables...
_API_AUTH_PATH = '/api/{API_version}/auth/session'

# Create a logger tree.bps...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))

@logged(logger)
@traced(logger)
class BPS(RestBase):
    """
    This class defines the API interface for the BPS.

    Inherits generic REST functionality from RestBase.

    Overrides methods in RestBase where necessary.

    Method names not beginning with "_" are made available to cmaple_cli.py for use in operations config files.

    """

    def __init__(self, **kwargs):

        """__init__ receives a kwargs dict to define parameters.  This allows __init__ to pass these parameters
        to the superclass.

        Returns an BPS leaf object.

        *Parameters*

        json_file_path: string, keyword, default=None
            The path to the json model file.  This file is typically named 'api-docs-all.json' and obtained
            from the BPS binary image.  Unzip the binary image then open the extracted file in 7-Zip.  This file
            is located in the directory "rest-api-docs\api\".
            This file provides the API model to cMAPLE:BPS which is used for many of the operations to derive urls, etc.
        BPS_host: string, keyword, default=None
            The ip address or fqdn of the BPS
        BPS_port: integer, keyword, default=443
            The TCP/IP BPS management port
        BPS_username: string, keyword, default=None
            The username for BPS
        BPS_password: string, keyword, default=None
            The password for BPS
        BPS_context: string, keyword, default='Default'
            The target BPS context.
        API_path_delimiter: string, keyword, default='/'
            The default delimiter for the API path.
        API_version: string, keyword, default='v1'
            The API version supported by the target BPS.
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

        kwarg_defaults = {'paths_file': None, 'BPS_host': None, 'BPS_port': None, 'BPS_username': None,
                          'BPS_password': None, 'BPS_domain': 'Default', 'API_path_delimiter':'/', 'API_version': 'v1',
                          'verify': False, 'default_get_item_limit': 100, 'rpm_retries': 5, 'backoff_timer': 30,
                          'persist_responses': True, 'restore_responses': False, 'leaf_dir': None}

        for key, val in kwargs.items():
            kwarg_defaults[key] = val

        self.__dict__.update(kwarg_defaults)

        super(BPS, self).__init__()

        #Attributes inherited from leaf_base to override in this class
        self.next_link_query = '$..next'
        self.credentials_dict = {'username':self.BPS_username,'password':self.BPS_password}

        #Validate critical attributes
        self.BPS_host = input_validations.validate_ip_host(self.BPS_host)
        self.BPS_user = input_validations.validate_string_value(self.BPS_username,'bps username')
        self.BPS_password = input_validations.validate_string_value(self.BPS_password,'bps password')
        
        #Add class specific attributes
        self.domain_ID_dict = {}
        self._url_host = 'https://' + self.BPS_host
        if self.BPS_port and not int(self.BPS_port) == int(443):
            self._url_host += ':' + str(self.BPS_port)
        self._auth_url = self._url_host + _API_AUTH_PATH.replace('{API_version}',self.API_version)
        self.request_headers = {'Content-Type': 'application/json'}
        self._auth_headers = self.request_headers
        self.apiKey = None
        self.sessionId = None

        self._get_session()

        self._auth_token_time = None
        self._requests_per_minute_time = None
        self._requests_counter = 0
        self._refresh_token = None
        self._refresh_token_count = 0
        if self.restore_responses:
            response_url = list(self.responses_dict.keys())[0]
        # self.path_root = '{}/{}/'.format(self._url_host,'api')
        self.path_root = self._url_host
        # This cache will be used by _get_child_urls to store responses to handle anomaly cases

        # Load the model and build the reference dictionaries...
        self._API_path_keywords_list = []
        self._json_dict = None
        # self._get_json_dict(self.json_file_path)
        self._all_API_paths_list = open(self.paths_file, 'r').readlines()
        # # pprint(self._json_dict)
        # self._resources_path_dict, self._operations_dict, self._models_path_dict, \
        # self._paths_hierarchy, self._API_path_keywords_list, self._all_API_paths_list, \
        # self._path_models_dict, self._models_dict, self._API_path_dict = bps_helpers.get_all_reference_dicts(self)
        # pprint(self._API_path_dict)
        # sys.exit()

    #Methods inherited from leaf_base to override in this class
    ##############################################################################################################
    @logged(logger)
    @traced(logger)
    def _request_wrapper(self, recursed=False, **kwargs):

        """Wraps all requests for an BPS leaf in order to handle BPS specifics such at re-auth and rate limit.
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
                        'BPS reports requests per minute exceeding 120.  Sleeping for self._backoff_timer seconds...')
                    time.sleep(self.backoff_timer)
                else:

                    # Derive next_url
                    next_url = None
                    current_offset = None
                    current_limit = None
                    current_total = None
                    # if 'rangeInfo' in response_dict['json_dict']:
                    #     if 'offset' in response_dict['json_dict']['rangeInfo']:
                    #         current_offset = response_dict['json_dict']['rangeInfo']['offset']
                    #     if 'limit' in response_dict['json_dict']['rangeInfo']:
                    #         current_limit = response_dict['json_dict']['rangeInfo']['limit']
                    #     if 'total' in response_dict['json_dict']['rangeInfo']:
                    #         current_total = response_dict['json_dict']['rangeInfo']['total']
                    #     this_url = response_dict['url']
                    #     if (current_offset + current_limit) >= current_total:
                    #         next_url = None
                    #     else:
                    #         offset = current_offset + current_limit
                    #         if 'offset=' in this_url:
                    #             next_url = re.sub(r'offset=[^&]+', 'offset=' + str(offset), this_url)
                    #         else:
                    #             next_url = '{}&{}{}'.format(this_url, 'offset=', str(offset))
                    #     print('next_url=', next_url)
                    return response_dict, status, include_filtered, exclude_filtered, cache_hit, next_url
        else:
            return tree_helpers.process_json_request(**kwargs)

    @logged(logger)
    @traced(logger)
    def _get_child_urls(self, response_dict, parent_url):

        """This method retrieves the url for all child objects of this response.
        This should only be called by internal methods.

        Returns: child_url for this anomalous type

        *Parameters*

        response_dict: dictionary
            The response for which to find child urls.
        parent_url: string
            The parent url of this response.  Used to prevent circular object references.
        """

        child_urls = tree_helpers.get_objectpath_values('$..href', response_dict)
        return child_urls, {}

    #Begin class specific methods
    ################################################################################################################
    def walk_API_resource_gets(self, include_filter_regex=None, exclude_filter_regex=None, responses_dict=None,
                               use_cache=True, stop_on_error=False, get_item_limit=None):

        """Recursively walks the API resource paths.

        Returns a Python dictionary object containing the response results for all url path GETs.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        *Parameters*

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

        if responses_dict is None:
            responses_dict = self.responses_dict

        for root_path, resource_paths in self._paths_hierarchy.items():
            for resource_path, resource_dict in resource_paths.items():
                url = root_path + '/' + resource_path
                logger.debug('walk_API_resource_gets calling recurse_API_child_gets with url %s...' % (url))
                self._recurse_API_child_gets(url, include_filter_regex=include_filter_regex,
                                             exclude_filter_regex=exclude_filter_regex,
                                             use_cache=use_cache, stop_on_error=stop_on_error,
                                             responses_dict=responses_dict, get_item_limit=sd(locals(), 'get_item_limit', self))

        return self.responses_dict

    def get_all_API_paths_list(self):

        """Returns a list of all valid API paths for the BPS host.

        Returns a list of all the valid API paths for this BPS host.  Contains the domain id for the BPS but container
        and object will be required as indicated by placeholders {containerUUID} and {objectId}.
        """

        return list(self._all_API_paths_list)

    def prep_put_json(self, json_dict=None):

        json_copy = {}
        tree_helpers.deep_update(json_copy, json_dict)
        pop_keys = ['metadata', 'links']
        new_json = {}
        for key, val in json_copy.items():
            if key in pop_keys:
                continue
            else:
                new_json[key] = val

        return new_json

    def _get_json_dict(self, json_file_path=''):

        """Reads the current json BPS API model into a Python dictionary and build all required reference
        dictionaries.

        Returns a Python dictionary object containing json model.

        Processing the json model file takes up to one minute.  Therefore, this method will check to see if the model
        has changed since the last run.  It it is the same it will restore the json model dictionary and all derived
        reference dictionaries from pickled files.
        
        Pickles all newly created Python dictionaries if required.

        *Parameters*

        json_file_path: string, keyword, default=None
            The path to the json model file.  This file is typically named 'api-docs-bpswithll.json' and obtained
            from the target BPS.  Typically resides in the directory
            /var/opt/CSCOpx/MDC/tomcat/vms/api/api-explorer/api.
            This file provides the API model to MAPLE:BPS which is used for many of the operations to derive urls, etc.
        """

        self._json_dict = json.load(open(self.json_file_path, 'r'))

    def get_all_models_dict(self):
        """Returns the model dictionary created from the model input file.
        
        Returns a Python dictionary created from the json model input file.

        """
        
        return self._models_dict
    
    def get_all_API_paths_list(self):
        """Returns a list of all valid API paths for the BPS host.
        
        Returns a list of all the valid API paths for this BPS host.  Contains the domain id for the BPS but container and object
        will be required as indicated by placeholders {containerUUID} and {objectId}.

        """
        
        return list(self._all_API_paths_list)
    
    def post_csv_template_bulk(self,url=None,file_path=None):

        """Reads a csv file containing flatlined records (flattened with output_transforms.flatten_json(json_dict) and
        posts all records with a bulk post.  Target API must support bulk post for the given url.

        Returns - No return value.

        *Parameters*

        url: string, keyword, default=None
            The target url to post records.
        file_path: string, keyword, default=None
            The full path to the file containing the csv records.
        """

        bulk_post_body = output_transforms.csv_to_bulk_post_body(file_path)
        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            self._request_wrapper(recursed=False, url=url, json_body=expanded_json,
                                  responses_dict=self.responses_dict, headers=self.request_headers,
                                  method='post', credentials_dict=self.credentials_dict, verify=self.verify,
                                  success_status_code=201)

        logger.debug(pformat(response_dict))

    def smart_get_url_list(self, url, responses_dict=None):

        """Used to intelligently retrieve and substitute object ids from provided names.

        Returns a Python dictionary object containing the response results.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        *Parameters*

        url: string
            The url of the path to intelligently GET.
            Example: policy/accesspolicies/$.items[@.name is 'access_1'].id/accessrules/$.items[@.name is 'rule_1').id
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        kwargs = locals()
        logger.debug('GET_smart: in GET_smart with url %s' % (url))
        if responses_dict is None:
            responses_dict = self.responses_dict

        path_parts = url.split('/')
        url_path = self.path_root
        current_url_path = url_path
        objectpath_results = None
        response_dict = {}
        while path_parts:
            path_part = path_parts.pop(0)
            if path_part in self._resources_path_dict:
                url_path += path_part
                continue
            elif path_part.startswith('$'):
                objectpath_results = tree_helpers.get_objectpath_values(path_part, response_dict)
                if objectpath_results:
                    prev_urls = response_dict.keys()
                    response_dict = {}
                    urls_processed = []
                    for prev_url in prev_urls:
                        prev_url = re.sub(r'\?.+$','',prev_url)
                        if prev_url in urls_processed:
                            continue
                        urls_processed.append(prev_url)
                        for objectpath_result in objectpath_results:
                            self._collect_responses(prev_url + '/' + objectpath_result, response_dict, responses_dict)
            else:
                prev_urls = []
                if response_dict:
                    prev_urls = list(response_dict.keys())
                    for i in range(0,len(prev_urls)):
                        prev_urls[i] += '/' + path_part
                else:
                    url_path += '/' + path_part
                    prev_urls.append(url_path)
                response_dict = {}
                urls_processed = []
                for prev_url in prev_urls:
                    prev_url = re.sub(r'\?.+$', '', prev_url)
                    if prev_url in urls_processed:
                        continue
                    urls_processed.append(prev_url)
                    self._collect_responses(prev_url, response_dict, responses_dict)
        return response_dict

    def _get_session(self):
        """
        Under construction...
        """

        # Get a security token valid for 30 minutes.  Record the time to check for validity
        self._auth_token_time = time.time()
        json_body = json.dumps(self.credentials_dict)
        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            tree_helpers.process_json_request(url=self._auth_url, responses_dict=self.responses_dict,
                                              method='post', headers=self._auth_headers, stop_on_error=True,
                                              credentials_dict=self.credentials_dict, success_status_code=200,
                                              verify=self.verify, json_body=json_body)

        auth_headers = response_dict['headers']
        pprint(response_dict)
        self.apiKey = response_dict['json_dict']['apiKey']
        self.sessionId = response_dict['json_dict']['sessionId']
        print(self.sessionId)
        if self.apiKey is None:
            logger.error('apiKey not found.  Returned headers = ', auth_headers, '\nExiting...')
            sys.exit()
        self.request_headers['X-API-KEY'] = self.apiKey

    # def login(self, enableRequestPrints = False):
    #     service = 'https://' + self.ipstr + '/api/v1/auth/session'
    #     jheaders = {'content-type': 'application/json'}
    #     jdata = json.dumps({'username':self.username, 'password':self.password})
    #     r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
    #     if(enableRequestPrints):
    #         self.pretty_print_requests(r)
    #     if(r.status_code == 200):
    #         apiKey = r.json().get('apiKey')
    #         self.session.headers['X-API-KEY'] = apiKey
    #         print 'Login successful. Welcome ' + self.username
    #     else:
    #     	print r.status_code
    #     	print r.content
    #     	sys.exit(0)

    def smart_get_object_id(self, url, responses_dict=None):

        """Used to intelligently retrieve an id based on item name.

        Returns a Python dictionary object containing the response results.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        *Parameters*

        url: string
            The url of the path to intelligently GET.
            Example: policy/accesspolicies/$.items[@.name is 'access_1'].id/accessrules/$.items[@.name is 'rule_1').id
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        logger.debug('GET_smart: in GET_smart with url %s' % (url))
        if responses_dict is None:
            responses_dict = self.responses_dict

        path_parts = url.split('/')
        url_path = self.path_root
        current_url_path = url_path
        objectpath_results = None
        response_dict = {}
        while path_parts:
            path_part = path_parts.pop(0)
            if path_part in self._resources_path_dict:
                url_path += path_part
                continue
            elif path_part.startswith('$'):
                objectpath_results = tree_helpers.get_objectpath_values(path_part, response_dict)
                if objectpath_results:
                    if len(objectpath_results) == 1:
                        return objectpath_results[0]
                    else:
                        return objectpath_results
            else:
                prev_urls = []
                if response_dict:
                    prev_urls = list(response_dict.keys())
                    for i in range(0,len(prev_urls)):
                        prev_urls[i] += '/' + path_part
                else:
                    url_path += '/' + path_part
                    prev_urls.append(url_path)
                response_dict = {}
                urls_processed = []
                for prev_url in prev_urls:
                    prev_url = re.sub(r'\?.+$', '', prev_url)
                    if prev_url in urls_processed:
                        continue
                    urls_processed.append(prev_url)
                    self._collect_responses(prev_url, response_dict, responses_dict)
        return None  # No id found

    def _build_request_templates(self):
        """
        Under construction...
        """
        
        request_templates_dict = {}
        for key, val in self._all_models.items():
            request_templates_dict[key] = bps_helpers.build_request_template_from_model(val)

    def _build_flattened_model_dict_by_name(self,model_name):
        """
        Under construction...
        """

        flatlined = output_transforms.flatten_json(self._models_dict[model_name])

        return flatlined
