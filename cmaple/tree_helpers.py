#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

tree_helpers.py implements various helper function common to most leaf type.

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


import ipaddress
import socket
import requests
import sys
import os
import json
from pprint import pprint
import re
import logging
import collections
from collections import OrderedDict
from autologging import logged, traced
from autologging import TRACE
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
import xmltodict
import objectpath
import shelve
from time import gmtime,strftime
from datetime import datetime, timedelta
import calendar
import pytz
import _pickle
from dateutil import parser as date_parser

# Create a logger for this module...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))


@logged(logger)
@traced(logger)
def get_strftime(_datetime=datetime.utcnow(), strf_str=r'%Y-%m-%dT%H:%M:%SZ'):

    return _datetime.strftime(strf_str)


@logged(logger)
@traced(logger)
def get_strftime_delta(_strftime=get_strftime(), days=0, seconds=0, microseconds=0,
                       milliseconds=0, minutes=0, hours=0, weeks=0, strf_str=r'%Y-%m-%dT%H:%M:%SZ'):

    _datetime = datetime.strptime(_strftime, strf_str)
    return (_datetime + timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds,
                                  minutes=minutes, hours=hours, weeks=weeks)).strftime(strf_str)


@logged(logger)
@traced(logger)
def get_utc_timestamp(year=2018, month=1, day=1, hour=0, minute=0, second=0, tz_str='Etc/GMT-0'):

    mytz = pytz.timezone(tz_str)
    dt = datetime(year, month, day, hour, minute, second)
    dt = mytz.normalize(mytz.localize(dt, is_dst=True))
    return calendar.timegm(dt.utctimetuple())


@logged(logger)
@traced(logger)
def get_datetime(year=2018, month=1, day=1, hour=0, minute=0, second=0, tz_str='Etc/GMT-0'):

    mytz = pytz.timezone(tz_str)
    dt = datetime(year, month, day, hour, minute, second)
    dt = mytz.normalize(mytz.localize(dt, is_dst=True))
    return dt


@logged(logger)
@traced(logger)
def persist_response(leaf_dir, response_counter, response_dict):
    """Pickles the response to the leaf working directory.

    """
    url = response_dict['url']
    pickle_file_name = ('%06d' % response_counter) + '_' + re.sub('[^a-zA-Z0-9]','~',url) + '.response_pickle'
    with open(os.path.join(leaf_dir,pickle_file_name),'wb') as f:
        _pickle.dump(response_dict,f)


@logged(logger)
@traced(logger)
def restore_responses(leaf_dir, responses_dict):
    """Restores pickled responses from the leaf working directory to the leaf's responses_dict.

    """
    leaf_dir_files = os.listdir(leaf_dir)
    for leaf_dir_file in leaf_dir_files:
        if '.response_pickle' in leaf_dir_file:
            with open(os.path.join(leaf_dir,leaf_dir_file), "rb") as f:
                response_dict = _pickle.load(f)
                url = response_dict['url']
                responses_dict[url] = response_dict

@logged(logger)
@traced(logger)
def query_json_field_from_url(query_url=None, json_to_query=None):
    """Returns a list of all objectpath matches based on query string 'json_to_query'.

    """
    query_field = re.match(r'.+?~([^~]+)~', query_url).group(1)
    query_values = get_objectpath_values('$..' + query_field, json_to_query)
    return query_values


@logged(logger)
@traced(logger)
def query_with_list(query_url=None, query_list=None):
    """Iterates over query list substituting each element for the value enclosed in ~.

    """
    query_field = re.match(r'.+?~([^~]+)~', query_url).group(1)
    values_seen = []
    for query_value in query_list:
        if not query_value in values_seen:
            values_seen.append(query_value)
            url = query_url.replace('~' + query_field + '~', str(query_value))
            self.GET_API_path(url)

@logged(logger)
@traced(logger)
def query_json_field(query_field=None, json_to_query=None):
    """Returns a list of all objectpath matches based on query string 'json_to_query'.

    """
    query_values = get_objectpath_values('$..' + query_field, json_to_query)
    return query_values

@logged(logger)
@traced(logger)
def deep_update_od(d, u):
    """Deep copies OrderedDict u to dictionary d.

    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = deep_update(d.get(k, collections.OrderedDict()), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

@logged(logger)
@traced(logger)
def deep_update(d, u):
    """Deep copies dictionary u to dictionary d.

    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = deep_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

@logged(logger)
@traced(logger)
def store_json_response_by_url(r, url, good_status_code, responses_dict,
                               include_filter_regex=None, exclude_filter_regex=None,
                               include_filtered=False, exclude_filtered=False, cache_hit=False):
    """Stores the REST response to the leafs responses_dict.

    """
    if not url in responses_dict:
        responses_dict[url] = {'url':None, 'headers':None,'error':None,'json_dict':None,'status_code':None,'null_response':False,'filtered':False,'cache_hit':False}
    
    responses_dict[url]['url'] = url
    responses_dict[url]['include_filtered'] = include_filtered
    responses_dict[url]['exclude_filtered'] = exclude_filtered
    responses_dict[url]['include_filter_regex'] = include_filter_regex    
    responses_dict[url]['exclude_filter_regex'] = exclude_filter_regex    
    responses_dict[url]['cache_hit'] = cache_hit
    
    try:
        if getattr(r,'status_code'):
            responses_dict[url]['status_code'] = r.status_code
    except AttributeError:
        pass

    if not r is None:
        if r.headers:
            responses_dict[url]['headers'] = r.headers
        if r.status_code == good_status_code:
            if r.text:
                if not re.match(r'.+?\.xml$',url):
                    responses_dict[url]['json_dict'] = json.loads(r.text)
                else:
                    responses_dict[url]['json_dict'] = xmltodict.parse(r.text)
        else:
            if r.text:
                responses_dict[url]['error'] = r.text
    else:
        responses_dict[url]['null_response'] = True

    if not include_filtered or exclude_filtered or cache_hit or r.status_code != good_status_code:
        return False
    else:
        return True


@logged(logger)
@traced(logger)
def get_empty_ordered_dict():
    """Returns an empty OrderedDict.  Mainly for use with maple_cli.

    """
    return OrderedDict()


@logged(logger)
@traced(logger)
def get_empty_dict():
    """Returns an empty dictionary.  Mainly for use with maple_cli.

    """
    return {}


@logged(logger)
@traced(logger)
def process_json_request(url, responses_dict, headers, method, credentials_dict, json_body="",
                         verify=False, success_status_code=200, include_filter_regex=None,
                         exclude_filter_regex=None, use_cache=False,
                         stop_on_error=False, API_path_keywords_list=[], get_item_limit=25):
    """Generic request wrapper for all REST methods.

    """

    print('Processing url %s...' % url, file=sys.stderr)
    store_status = None
    logger.debug('Processing json request method %s for url %s...' % (method,url))
    exclude_filtered = False
    include_filtered = True
    cache_hit = False
    if exclude_filter_regex and re.search(exclude_filter_regex, url):
        logger.debug('URL %s matched exclude filter regex %s, filtering...' % (url, exclude_filter_regex))
        exclude_filtered = True
    elif include_filter_regex and not re.search(include_filter_regex, url):
        logger.debug('URL %s did not match include filter regex %s, filtering...' % (url, include_filter_regex))
        include_filtered = False
    if use_cache and url in responses_dict:
        logger.debug('url %s was found in the cache...' % (url))
        cache_hit = True
    r = None
    if not exclude_filtered and include_filtered and not cache_hit:
        if credentials_dict:
            auth = requests.auth.HTTPBasicAuth(credentials_dict['username'],credentials_dict['password'])
        else:
            auth = ''
        try:
            request_method = getattr(requests, method)
        except Exception as err:
            logger.error("Error getting method reference for method %s, error message--> "+str(err))
            sys.exit(str(err))
        try:
            logger.debug('Requesting url %s with method %s and expecting %s...' % (url,method,success_status_code))
            if method == 'get':
                url_no_parameters = re.sub(r'\?[^?]+$','',url)
                last_path_part = re.search('[^/]+$',url_no_parameters).group(0)
                logger.debug('last_part_part = %s' % last_path_part)
                if last_path_part in API_path_keywords_list:
                    if 'limit=' in url:
                        url = re.sub(r'limit=\d+','limit='+str(get_item_limit),url)
                    else:
                        delimiter = ''
                        if '?' in url:
                            delimiter = '&'
                        else:
                            delimiter = '?'
                        url = url+delimiter+'limit='+str(get_item_limit)
            r = request_method(url=url, headers=headers, auth=auth, verify=verify, data=json_body)
            if (r.status_code == success_status_code):
                logger.debug('Request for url %s with method %s was successful.  Return status = %s...' % (url,method,str(r.status_code)))
                logger.debug('    Headers = %s' % (r.headers))
                logger.debug('    Response text = %s' % (r.text))
            else:
                # sys.exit()
                logger.warning('Request for url %s with method %s unsuccessful. Status code %s with response %s...' % (url,method, r.status_code, r.text))
                if stop_on_error:
                    logger.error('Request for url %s with method %s unsuccessful. Status code %s with response %s...'
                                 % (url, method, r.status_code, r.text))
                    logger.error('stop_on_error set to True, exiting...')
                    sys.exit()
        except Exception as err:
            logger.warning("Error in processing json request--> "+str(err))
            if stop_on_error:
                logger.error("Error in processing json request--> " + str(err))
                logger.error('stop_on_error set to True, exiting...')
                sys.exit()

    store_status = store_json_response_by_url(r, url, success_status_code, responses_dict, include_filter_regex, exclude_filter_regex,
                                              include_filtered, exclude_filtered, cache_hit)
    if r:
        r.close()
                
    return responses_dict[url], store_status, include_filtered, exclude_filtered, cache_hit


# @traced(logger) #trace logging disabled due to jsonpath spewing...need to put this in a class
@logged(logger)
def get_jsonpath_values(json_query,json_struct):
    """Queries json_struct with json_query using jsonpath.

    """

    jsonpath_query = parse(json_query)
    return [match.value for match in jsonpath_query.find(json_struct)]


# @traced(logger) #trace logging disabled due to jsonpath spewing...need to put this in a class
@logged(logger)
def get_objectpath_values(json_query, json_struct):
    """Queries json_struct with json_query using objectpath.

    """

    return list(objectpath.Tree(json_struct).execute(json_query))


# @traced(logger) #trace logging disabled due to jsonpath spewing...need to put this in a class
@logged(logger)
def get_jsonpath_full_paths_and_values(json_query,json_struct):
    """Queries json_struct with json_query using jsonpath.

    Returns a list of tuples with the jsonpath path and the respective values.
    """

    jsonpath_query = parse(json_query)
    tuple_list = [(str(match.full_path),match.value) for match in jsonpath_query.find(json_struct)]
    return tuple_list

