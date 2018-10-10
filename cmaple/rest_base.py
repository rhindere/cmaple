#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

rest_base.py implements generic REST functionality.  The class RestBase
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
import cmaple.input_validations as input_validations
import cmaple.output_transforms as output_transforms
import json
import urllib3
import shelve
from collections import OrderedDict
from pprint import pprint, pformat
import logging
from autologging import logged, traced
from autologging import TRACE
import time
from objectpath import *

# Create a logger...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))
# Define global variables
_DEFAULT_GET_ITEM_LIMIT = 400


@logged(logger)
@traced(logger)
class RestBase(object):

    """
    This class defines generic REST API functionality.

    Classes sub classing this class will need to override specific methods and properties as called out in the
    method docstrings and inline comments.

    Method names not beginning with "_" are made available to cmaple_cli.py for use in operations config files.

    """

    def __init__(self):

        """__init__ RestBase inherits arguments from the parent class.  All argument validation is
        performed by the parent class.
        """

        self.response_counter = 0
        self.credentials_dict = {} # Need to supply this in the parent class...
        self.next_link_query = '' # Need to supply this in the parent class...

        if not self.verify: # Disables insecure warning for self signed certs...
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        _DEFAULT_GET_ITEM_LIMIT = self.default_get_item_limit
        self.responses_dict = {}

    def _request_wrapper(self):
        """Must override in parent class"""
        pass

    def _get_child_urls(self):
        """Must override in parent class"""
        pass

    def _prepare_url_for_migration(self):
        """Must override in parent class"""
        pass

    def or_migrate_config(self):
        """Must override in parent class"""
        pass

    def put_json_request(self, url, json_dict, responses_dict=None):

        """Generic wrapper for a REST API Put request.

        Returns a Python dictionary object containing the response results for the Post.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        Parameters
        ----------
        url: string
            The url of the path to POST.  Must be a fully valid FMC api "GET" path.  url can include the
            host prefix or start from the resource path.  If the host prefix is missing, it will be added
            automatically.
        json_dict: dictionary, argument
            The Python dictionary containing the request json
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        if responses_dict is None:
            responses_dict = self.responses_dict

        if self.path_root not in url:
            url = self.path_root + url

        json_string = json.dumps(json_dict)
        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            self._request_wrapper(recursed=False, url=url, json_body=json_string,
                                  responses_dict=responses_dict, headers=self.request_headers,
                                  method='put', credentials_dict=self.credentials_dict, verify=self.verify,
                                  success_status_code=200)
        return response_dict

    def post_json_request(self, url, json_dict, responses_dict=None):

        """Generic wrapper for a REST API Post request.

        Returns a Python dictionary object containing the response results for the Post.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        Parameters
        ----------
        url: string
            The url of the path to POST.  Must be a fully valid FMC api "GET" path.  url can include the
            host prefix or start from the resource path.  If the host prefix is missing, it will be added
            automatically.
        json_dict: dictionary, argument
            The Python dictionary containing the request json
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        if responses_dict is None:
            responses_dict = self.responses_dict

        if self.path_root not in url:
            url = self.path_root + url

        json_string = json.dumps(json_dict)
        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            self._request_wrapper(recursed=False, url=url, json_body=json_string,
                                  responses_dict=responses_dict, headers=self.request_headers,
                                  method='post', credentials_dict=self.credentials_dict, verify=self.verify,
                                  success_status_code=201)
        return response_dict

    def get_json_request(self, url, responses_dict=None):

        """Generic wrapper for a REST API GET request.

        Returns a Python dictionary object containing the response results for the Post.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        Parameters
        ----------
        url: string
            The url of the path to GET.  Must be a fully valid FMC api "GET" path.  url can include the
            host prefix or start from the resource path.  If the host prefix is missing, it will be added
            automatically.
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """

        if responses_dict is None:
            responses_dict = self.responses_dict

        if self.path_root not in url:
            url = self.path_root + url

        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            self._request_wrapper(recursed=False, url=url,
                                  responses_dict=responses_dict, headers=self.request_headers,
                                  method='get', credentials_dict=self.credentials_dict, verify=self.verify,
                                  success_status_code=200)
        return response_dict

    def get_all_items(self, url, use_cache=True, end_path_regex=None, include_filter_regex=None,
                      exclude_filter_regex=None, stop_on_error=False, filtered=False, cache_hit=False,
                      get_item_limit=_DEFAULT_GET_ITEM_LIMIT, responses_dict=None):

        """Performs a get to retrieve the "Items" listing for the url.

        Returns a Python dictionary object containing the response results.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        Parameters
        ----------
        url : string
            The url for which to retrieve the items list.  Must be a fully valid FMC api "GET" path.  url can include
            the host prefix or start from the resource path.  If the host prefix is missing, it will be added
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

        if responses_dict is None:
            responses_dict = self.responses_dict

        if self.path_root not in url:
            url = self.path_root + url

        while True:
            logger.debug('get_all_items: recursing with url %s' % (url))
            response_dict, status, include_filtered, exclude_filtered, cache_hit = \
                self._request_wrapper(recursed=False, url=url, responses_dict=responses_dict,
                                      headers=self.request_headers,
                                      method='get', credentials_dict=self.credentials_dict,
                                      verify=self.verify, success_status_code=200,
                                      include_filter_regex=include_filter_regex,
                                      exclude_filter_regex=exclude_filter_regex,
                                      use_cache=use_cache, stop_on_error=stop_on_error,
                                      API_path_keywords_list=self._API_path_keywords_list,
                                      get_item_limit=get_item_limit)

            logger.debug(pformat(response_dict))
            next_link = tree_helpers.get_jsonpath_values(self.next_link_query, response_dict)

            if status and self.persist_responses:
                self.response_counter += 1
                tree_helpers.persist_response(self.leaf_dir, self.response_counter, response_dict)

            if next_link:
                next_url = next_link[0][0]
                response_dict['next_link'] = next_url
                url = next_url
            else:
                break

        return responses_dict

    def _recurse_API_child_gets(self, url, use_cache=True, end_path_regex=None, include_filter_regex=None,
                                exclude_filter_regex=None, stop_on_error=False, filtered=False, cache_hit=False,
                                get_item_limit=_DEFAULT_GET_ITEM_LIMIT, responses_dict=None, parent_url=''):

        """Handles recursion of a given url path.  Normally not called directly but from a wrapper method.
        Begins at given API url path and recursively GET walks path and child paths until complete.  Automatically
        handles pagination and discovery of child urls.

        Returns a Python dictionary object containing the response results for all url path GETs.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        Parameters
        ----------
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

        if responses_dict is None:
            responses_dict = self.responses_dict

        if self.path_root not in url:
            url = self.path_root + url

        while True:
            logger.debug('recurse_API_child_gets: recursing with url %s' % (url))
            response_dict, status, include_filtered, exclude_filtered, cache_hit = \
                self._request_wrapper(recursed=False, url=url, responses_dict=responses_dict,
                                      headers=self.request_headers,
                                      method='get', credentials_dict=self.credentials_dict,
                                      verify=self.verify, success_status_code=200,
                                      include_filter_regex=include_filter_regex,
                                      exclude_filter_regex=exclude_filter_regex,
                                      use_cache=use_cache, stop_on_error=stop_on_error,
                                      API_path_keywords_list=self._API_path_keywords_list,
                                      get_item_limit=get_item_limit)

            logger.debug(pformat(response_dict))
            next_link = tree_helpers.get_jsonpath_values(self.next_link_query, response_dict)

            child_urls = []
            # Insert the parent url so we don't add it as a child of a child....securityzones...physical interfaces
            if response_dict['json_dict']:
                child_urls = self._get_child_urls(response_dict, url)
            response_dict['child_urls'] = child_urls

            if status and self.persist_responses:
                self.response_counter += 1
                tree_helpers.persist_response(self.leaf_dir, self.response_counter, response_dict)

            for child_url in child_urls:
                if child_url:
                    # Check to make sure we aren't in a circular reference situation...
                    if child_url == parent_url:
                        logger.warning('Circular reference detected for url %s' % url)
                        continue
                    logger.debug('Recursing into recurse_API_child_gets with child url = %s' % (child_url))
                    self._recurse_API_child_gets(child_url, include_filter_regex=include_filter_regex,
                                                 exclude_filter_regex=exclude_filter_regex,
                                                 use_cache=use_cache, stop_on_error=stop_on_error,
                                                 get_item_limit=get_item_limit, responses_dict=responses_dict,
                                                 parent_url=url)
            if next_link:
                next_url = next_link[0][0]
                response_dict['next_link'] = next_url
                url = next_url
            else:
                break

    def walk_API_path_gets(self,url,end_path_regex=None,include_filter_regex=None,exclude_filter_regex=None,
                           use_cache=True,stop_on_error=False,get_item_limit=_DEFAULT_GET_ITEM_LIMIT,
                           responses_dict=None):

        """Begins at given API url path and recursively GET walks path and child paths until complete.
        
        Returns a Python dictionary object containing the response results for all url path GETs.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        Parameters
        ----------
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

        logger.debug('walk_API_path_gets calling recurse_API_child_gets with url %s...' % (url))

        if responses_dict is None:
            responses_dict = self.responses_dict

        if self.path_root not in url:
            url = self.path_root + url

        self._recurse_API_child_gets(url, include_filter_regex=include_filter_regex,
                                    exclude_filter_regex=exclude_filter_regex,
                                    use_cache=use_cache,stop_on_error=stop_on_error,
                                    get_item_limit=get_item_limit, responses_dict=responses_dict)
    
        return responses_dict

    def _collect_responses(self, url, response_dict, responses_dict):

        """Utility method called by wrappers to request all pages for a given url.  Normally not called directly.

        Returns a Python dictionary object containing the response results.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        Parameters
        ----------
        url: string
            The url of the path to GET.  Must be a fully valid FMC api "GET" path.
        response_dict: dictionary
            A dictionary reference updated by this method to include all responses.
        responses_dict: dictionary, keyword, default=None
            Allows the caller to override the default behavior to store responses in the self.responses_dict.  Useful
            if caller would like to keep the responses isolated.
        """
        
        while True:
            response_struct = self.get_json_request(url, responses_dict=responses_dict)
            logger.debug(pformat(response_struct))
            response_dict.update({url: response_struct})
            next_link = tree_helpers.get_objectpath_values(self.next_link_query,
                                                           response_struct['json_dict'])
            if next_link:
                next_url = next_link[0]
                url = next_url
            else:
                break
        return response_dict

    def post_csv_template(self,url=None,file_path=None):

        """Reads a csv file containing flatlined records (flattened with output_transforms.flatten_json(json_dict) and
        posts each record individually to the target.

        Returns - No return value.

        Parameters
        ----------
        url: string, keyword, default=None
            The target url to post records.
        file_path: string, keyword, default=None
            The full path to the file containing the csv records.
        """

        csv_file = open(file_path,'r')
        csv_list = []
        for line in csv_file.readlines():
            if not line == '\n':
                csv_list.append(line.strip())
        flatlined_list = output_transforms.csv_to_flatlined(csv_list)
        for flatlined in flatlined_list:
            expanded = output_transforms.expand_flattened_json(flatlined)
            expanded_json = json.dumps(expanded)
            response_dict, status, include_filtered, exclude_filtered, cache_hit = \
                self._request_wrapper(recursed=False, url=url, json_body=expanded_json,
                                      responses_dict=self.responses_dict, headers=self.request_headers,
                                      method='post', credentials_dict=self.credentials_dict, verify=self.verify,
                                      success_status_code=201)

            logger.debug(pformat(response_dict))

    def write_csv_template_from_response(self, response_json=None, file=sys.stdout):

        """Flatlines response_json and writes to a csv record.

        Returns - The csv records.

        Parameters
        ----------
        response_json: list, keyword, default=None
            The list of responses to write to csv.
        file: file_handle, keyword, default=sys.stdout
            The file_handle target for the csv records.
        """

        flatlined = output_transforms.flatten_json(response_json[0])
        flatlined_csv = output_transforms.create_csv_from_flatline(flatlined, field_filter_regex='metadata', file=None)
        return flatlined_csv

    def GET_responses_by_jsonpath(self, jsonpath, responses_dict=None):

        """Returns responses matching a jsonpath query.

        Returns - The matching responses.

        Parameters
        ----------
        jsonpath: string
            The jsonpath query to match responses.
        responses_dict: dictionary, keyword, default=None
            The response dictionary to query.
        """

        results = list(Tree(responses_dict).execute(jsonpath))
        return results

    def GET_API_path(self, url, include_filter_regex=None, exclude_filter_regex=None,stop_on_error=False,
                     use_cache=False, responses_dict=None, get_item_limit=_DEFAULT_GET_ITEM_LIMIT):

        """Wrapper for a REST GET request.

        Returns a Python dictionary object containing the response results for the GET.

        By default stores all responses in self.responses_dict unless a dictionary is passed in using the
        responses_dict parameter.

        Parameters
        ----------
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

        if responses_dict is None:
            responses_dict = self.responses_dict

        if self.path_root not in url:
            url = self.path_root + url

        response_keys = ['response_dict', 'status', 'include_filtered', 'exclude_filtered', 'cache_hit']
        logger.debug('GET_API_path: getting url %s' % (url))
        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            self._request_wrapper(recursed=False, url=url, responses_dict=responses_dict,
                                  headers=self.request_headers,
                                  method='get', credentials_dict=self.credentials_dict,
                                  verify=self.verify, success_status_code=200,
                                  include_filter_regex=include_filter_regex,
                                  exclude_filter_regex=exclude_filter_regex,
                                  use_cache=use_cache, stop_on_error=stop_on_error,
                                  API_path_keywords_list=self._API_path_keywords_list,
                                  get_item_limit=get_item_limit)

        if status and self.persist_responses:
            self.response_counter += 1
            tree_helpers.persist_response(self.leaf_dir, self.response_counter, response_dict)

        logger.debug(pformat(responses_dict))
        return responses_dict

    def query_json_field_from_url(self, query_url=None, json_to_query=None):

        """Returns a list of json fields matching an objectpath query.

        Returns - A list of the matching fields.

        Parameters
        ----------
        query_url: string, keyword, default=None
            The url for which to query fields.
        json_to_query: dictionary, keyword, default=None
            The json dictionary to query.
        """

        query_field = re.match(r'.+?~([^~]+)~', query_url).group(1)
        query_values = tree_helpers.get_objectpath_values('$..' + query_field, json_to_query)
        return query_values

    def query_with_list(self, query_url=None, query_list=None):

        """Iterates over and substitutes the values in query_list in query_url

        Returns - All responses obtained.

        Parameters
        ----------
        query_url: string, keyword, default=None
            The url for which to query fields.
        query_list: list, keyword, default=None
            The list of values to iterate over and substitute in query_url.
        """

        query_field = re.match(r'.+?~([^~]+)~', query_url).group(1)
        values_seen = []
        print(query_field)

        for query_value in query_list:
            if not query_value in values_seen:
                values_seen.append(query_value)
                url = query_url.replace('~' + query_field + '~', str(query_value))
                print(url)
                self.GET_API_path(url)

        return self.responses_dict

    def query_json_field(self, query_field=None, json_to_query=None):

        """Returns a list of objects matching the query_field query.

        Returns - A list of the matching objects

        Parameters
        ----------
        query_field: string, keyword, default=None
            The field for which to query fields.
        json_to_query: dictionary, keyword, default=None
            The json dictionary to query.
        """

        query_values = tree_helpers.get_objectpath_values('$..' + query_field, json_to_query)
        return query_values

    def set_json_properties(self, json_dict=None, properties_dict=None):

        """Sets properties in json_dict from properties_dict.

        Returns - The modified json_dict.

        Parameters
        ----------
        json_dict: dictionary, keyword, default=None
            The json_dict to modify.
        properties_dict: dictionary, keyword, default=None
            The properties to modify {property:value}.
        """

        def recurse_property_matches(json_dict):
            if type(json_dict) is dict or type(json_dict) is OrderedDict:
                for key, val in json_dict.items():
                    if key in properties_dict:
                        json_dict[key] = properties_dict[key]
                    if type(val) is dict or type(val) is OrderedDict:
                        recurse_property_matches(val)
                    elif type(val) is list:
                        for val_member in val:
                            recurse_property_matches(val_member)
            elif type(json_dict) is list:
                for json_member in json_dict:
                    recurse_property_matches(json_member)

        recurse_property_matches(json_dict)

        return json_dict

    def _set_json_properties_by_objectpath(self, json_dict=None, properties_dict=None):

        """Sets properties in json_dict from properties_dict.

        Returns - The modified json_dict.

        Parameters
        ----------
        json_dict: dictionary, keyword, default=None
            The json_dict to modify.
        properties_dict: dictionary, keyword, default=None
            The properties to modify {property:value}.
        """

        def recurse_path(id_path_parts, json_dict):
            path_part = id_path_parts.pop(0)
            if type(json_dict) is list:
                list_index = int(re.match(r'.+?([0-9])+.+', path_part).group(1))
                return recurse_path(id_path_parts, json_dict[list_index])
            elif not path_part == 'id':
                json_dict = json_dict[path_part]
                return recurse_path(id_path_parts, json_dict)
            else:
                if json_dict['id'] in id_mappings:
                    new_id = id_mappings[json_dict['id']]
                    json_dict['id'] = new_id
                else:
                    json_dict['id'] = 'unsupported'
                if json_dict['id'] == 'unsupported':
                    return False
                else:
                    return True

        def recurse_property_matches(json_dict, type_list):
            if type(json_dict) is dict or type(json_dict) is OrderedDict:
                for key, val in json_dict.items():
                    if type(val) is dict or type(val) is OrderedDict:
                        if 'type' in val:
                            type_list.append({'key': key, 'dict': val})
                        elif 'refType' in val:
                            type_list.append({'key': key, 'dict': val})
                        recurse_property_matches(val, type_list)
                    elif type(val) is list:
                        for val_member in val:
                            val_dict = {key: val_member}
                            recurse_property_matches(val_dict, type_list)
            elif type(json_dict) is list:
                for json_member in json_dict:
                    recurse_property_matches(json_member, type_list)

        recurse_property_matches(json_dict, properties_dict)

    def get_leaf_dir(self):

        return self.leaf_dir
