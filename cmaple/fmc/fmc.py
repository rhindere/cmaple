#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

ssh.py implements Cisco FMC specific REST functionality.  Generic
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
import cmaple.fmc.fmc_helpers as fmc_helpers
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
_API_AUTH_PATH = '/api/fmc_platform/{API_version}/auth/generatetoken'

# Create a logger tree.fmc...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))

@logged(logger)
@traced(logger)
class FMC(RestBase):
    """
    This class defines the API interface for the FMC.

    Inherits generic REST functionality from RestBase.

    Overrides methods in RestBase where necessary.

    Method names not beginning with "_" are made available to cmaple_cli.py for use in operations config files.

    """
    def __init__(self, **kwargs):

        """__init__ receives a kwargs dict to define parameters.  This allows __init__ to pass these parameters
        to the superclass.

        Returns an FMC leaf object.

        *Parameters*

        json_file_path: string, keyword, default=None
            The path to the json model file.  This file is typically named 'api-docs-fmcwithll.json' and obtained
            from the target FMC.  Typically resides in the directory
            /var/opt/CSCOpx/MDC/tomcat/vms/api/api-explorer/api.
            This file provides the API model to MAPLE:FMC which is used for many of the operations to derive urls, etc.
        FMC_host: string, keyword, default=None
            The ip address or fqdn of the FMC
        FMC_port: integer, keyword, default=443
            The TCP/IP FMC management port
        FMC_username: string, keyword, default=None
            The username for FMC
        FMC_password: string, keyword, default=None
            The password for FMC
        FMC_domain: string, keyword, default='Global'
            The target FMC domain.
        API_path_delimiter: string, keyword, default='/'
            The default delimiter for the API path.
        API_version: string, keyword, default='v1'
            The API version supported by the target FMC.
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

        kwarg_defaults = {'json_file_path':None, 'FMC_host':None, 'FMC_port':None, 'FMC_username':None,
                          'FMC_password':None, 'FMC_domain':'Global', 'API_path_delimiter':'/', 'API_version':'v1',
                          'verify':False, 'default_get_item_limit':400, 'rpm_retries':5, 'backoff_timer':30,
                          'persist_responses':True, 'restore_responses':False, 'leaf_dir': None,
                          'connect_device': True}

        for key, val in kwargs.items():
            kwarg_defaults[key] = val

        self.__dict__.update(kwarg_defaults)

        super(FMC, self).__init__()
        
        #Attributes inherited from leaf_base to override in this class
        self.next_link_query = '$..next'
        self.credentials_dict = {'username':self.FMC_username,'password':self.FMC_password}

        #Validate critical attributes
        self.FMC_host = input_validations.validate_ip_host(self.FMC_host)
        self.FMC_user = input_validations.validate_string_value(self.FMC_username,'fmc username')
        self.FMC_password = input_validations.validate_string_value(self.FMC_password,'fmc password')
        
        #Add class specific attributes
        self.domain_ID_dict = {}
        self._url_host = 'https://' + self.FMC_host
        if self.FMC_port and not int(self.FMC_port) == int(443):
            self._url_host += ':' + str(self.FMC_port)
        self._auth_url = self._url_host + _API_AUTH_PATH.replace('{API_version}',self.API_version)
        self.request_headers = {'Content-Type': 'application/json'}
        self._auth_headers = self.request_headers
        self._auth_token_time = None
        self._requests_per_minute_time = None
        self._requests_counter = 0
        self._auth_token = None
        self._refresh_token = None
        self._refresh_token_count = 0
        if self.connect_device:
            self._get_token_and_domains()
            self.FMC_domain = fmc_helpers.validate_FMC_domain(self.FMC_domain,self.domain_ID_dict)
            self.FMC_domain_ID = self.domain_ID_dict[self.FMC_domain]
        else:
            if self.restore_responses:
                response_url = list(self.responses_dict.keys())[0]
                self.FMC_domain_ID = re.match(r'.+?/domain/([^/]+)',response_url).group(1)
        self.path_root = '{}/{}/{}/{}/{}/{}/'.format(self._url_host,'api','fmc_config',self.API_version,'domain',
                                                   self.FMC_domain_ID)
        # This cache will be used by _get_child_urls to store responses to handle anomaly cases
        self.anomalous_response_cache = {}

        # Load the model and build the reference dictionaries...
        self._get_json_dict(self.json_file_path)
    #Methods inherited from leaf_base to override in this class
    ##############################################################################################################
    @logged(logger)
    @traced(logger)
    def or_migrate_config(self, source_config_path=None):

        """Migrates objects stored in source_config_path to this FMC instance.

        *Parameters*

        source_config_path: string, keyword, default=None
            The path to the working directory of the source FMC leaf.
        """
        def get_url_type(url, response_dict):
            url_type = None
            if 'items' in response_dict['json_dict']:
                url_type = 'item_list'
            elif not response_dict['child_urls']:
                url_type = 'end_object'
            else:
                for child_url in response_dict['child_urls']:
                    if url in child_url:
                        url_type = 'container'

            if not url_type:
                return 'composite_object'
            else:
                return url_type

        def get_parametered_urls_from_child_url(child_url):

            parametered_urls = []
            for url in source_responses_urls:
                if '?' in url:
                    non_parametered_url = re.sub(r'\?.+$', '', url)
                    if child_url == non_parametered_url:
                        parametered_urls.append(url)

            if not parametered_urls:  # didn't find any parametered urls...
                parametered_urls.append(child_url)
            return parametered_urls

        def prep_composite_json(json_dict):

            def recurse_path(id_path_parts, json_dict):
                path_part = id_path_parts.pop(0)
                if type(json_dict) is list:
                    list_index = int(re.match(r'.+?([0-9])+.+', path_part).group(1))
                    return recurse_path(id_path_parts, json_dict[list_index])
                elif not path_part == 'id' and path_part in json_dict:
                    #json_dict = json_dict[path_part]
                    return recurse_path(id_path_parts, json_dict[path_part])
                else:
                    if 'id' in json_dict:
                        if json_dict['id'] in id_mappings:
                            new_id = id_mappings[json_dict['id']]
                            json_dict['id'] = new_id
                        else:
                            json_dict['id'] = 'unsupported'
                    else:
                        json_dict['id'] = 'unsupported'
                    if json_dict['id'] == 'unsupported':
                        return False
                    else:
                        return True

            composite_ids = tree_helpers.get_jsonpath_full_paths_and_values('$..id', json_dict)
            for composite_id in composite_ids:
                id_path = composite_id[0]
                id_path_parts = id_path.split('.')
                base_key = id_path_parts[0]
                if not base_key in json_dict:
                    # Must have been a list and one element already deleted...
                    # All or nothing for now but may change?
                    continue
                if not recurse_path(id_path_parts, json_dict):
                    logger.warning('Object %s is unsupported for migration...' % json_dict[base_key])
                    logger.warning('\tRemoving from parent container with json\n%s' % json_dict)
                    logger.warning('\tObject will need to be added manually...')
                    json_dict.pop(base_key)

            return json_dict

        def prep_migration_json(url, response_dict, object_type):
            json_copy = {}
            tree_helpers.deep_update(json_copy, response_dict['json_dict'])
            pop_keys = ['id', 'metadata', 'links']
            new_json = {}
            for key, val in json_copy.items():
                if key in pop_keys:
                    continue
                elif type(json_copy[key]) is dict and 'refType' in json_copy[key]:
                    if json_copy[key]['refType'] == 'list':
                        continue
                elif object_type == 'container' and type(json_copy[key]) is dict and 'id' in json_copy[key]:
                    id = json_copy[key]['id']
                    for child_url in response_dict['child_urls']:
                        if re.match('.+?/' + id, child_url):
                            child_response = self.source_responses_dict[child_url]
                            child_json = {}
                            tree_helpers.deep_update(child_json, child_response['json_dict'])
                            child_json.pop('id')
                            new_json[key] = child_json
                            child_response['processed'] = True
                else:
                    new_json[key] = val

            if object_type == 'composite_object':
                new_json = prep_composite_json(new_json)
            return new_json

        def get_item_id(url, name, type, response_dict):
            item_id = None
            if type in name_to_id_mappings and name in name_to_id_mappings[type]:
                item_id = name_to_id_mappings[type][name]
            else:
                if not type in name_to_id_mappings:
                    # Strip off any parameters before sending url to self.get_all_items...
                    url = re.sub('\?.+','',url)
                    item_responses = self.get_all_items(url=url, responses_dict={})
                    name_to_id_mappings[type] = {}
                    name_to_id_mappings[type]['item_responses'] = item_responses
                response_urls = list(name_to_id_mappings[type]['item_responses'].keys())
                for response_url in response_urls:
                    if 'items' in name_to_id_mappings[type]['item_responses'][response_url]['json_dict']:
                        for item in name_to_id_mappings[type]['item_responses'][response_url]['json_dict']['items']:
                            if item['name'] == name:
                                item_id = item['id']
                            name_to_id_mappings[type][name] = item['id']
                    else:
                        logger.warning('No enumeration items returned for url %s.')
                        name_to_id_mappings[type][name] = 'unsupported'
            return item_id

        def post_json_wrapper(response_dict, object_type):
            source_id = response_dict['json_dict']['id']
            url = response_dict['url']
            migration_url = prepare_url_for_migration(url, response_dict, id_mappings)
            if migration_url is None:
                logger.warning('Could not obtain migration url for url %s. \
                                Marking as unsupported' % url)
                new_item_id = 'unsupported'
                status = 'unsupported'
                posted_response = None
            else:
                new_json = prep_migration_json(url, response_dict, object_type)
                posted_response = self.post_json_request(migration_url, new_json)
                status = ''
                new_item_id = ''
                if not posted_response['status_code'] == 201:
                    error_text = posted_response['error']
                    name_exists_patterns = ['.+?exists',
                                            '.+?Read only Resource',
                                            '.+?Object Type in route did not match payload',
                                            '.+?Cannot modify',
                                            '.+?Post not allowed']
                    name_exists_pattern = '|'.join(name_exists_patterns)
                    name_exists_match = re.match(name_exists_pattern, error_text, re.I)
                    if name_exists_match:
                        logger.warning('Detected existing item %s using error text %s' % (new_json, error_text))
                        if 'name' in new_json:
                            name = new_json['name']
                            _type = new_json['type']
                            new_item_id = get_item_id(migration_url, name, _type, response_dict)
                            if new_item_id is None:
                                new_item_id = 'unsupported'
                                status = 'unsupported'
                            else:
                                status = 'exists'
                        else:
                            new_item_id = 'unsupported'
                            status = 'exists'
                    else:
                        logger.warning('Could not obtain migration id for json\n%s.  Marking as \
                                        unsupported' % new_json)
                        new_item_id = 'unsupported'
                        status = 'unsupported'
                else:
                    status = 'success'
                    new_item_id = posted_response['json_dict']['id']

            id_mappings[source_id] = new_item_id
            response_dict['processed'] = True
            return status, new_item_id, posted_response

        def post_container(url, response_dict):

            posted_response = post_json_wrapper(response_dict, 'container')

            return True

        def is_read_only_object(response_dict):

            metadata = tree_helpers.get_jsonpath_values('$..metadata',response_dict['json_dict'])[0]
            if 'readOnly' in metadata and metadata['readOnly']['state']:
                return True
            else:
                return False

        def post_end_object(url, response_dict):

            id = response_dict['json_dict']['id']
            type = response_dict['json_dict']['type']
            name = response_dict['json_dict']['name']
            if type in name_to_id_mappings and name in name_to_id_mappings[type]:
                logger.info('post_end_object: end_object type %s with name %s already exists on target FMC...' % (type, name))
                id_mappings[id] = name_to_id_mappings[type][name]
                return True

            posted_response = post_json_wrapper(response_dict, 'end_object')

            return True

        def post_composite_object(url, response_dict):

            posted_response = post_json_wrapper(response_dict, 'composite_object')
            return True

        def prepare_url_for_migration(url, response_dict, id_mapping):

            type = response_dict['json_dict']['type']
            #Handle exceptions to url construct here...
            if type == 'AccessRule':
                if 'metadata' in response_dict['json_dict']:
                    if 'section' in response_dict['json_dict']['metadata']:
                        section = response_dict['json_dict']['metadata']['section']
                        if re.match(r'.+?\?[^/]+$', url):
                            url += '&section=%s' % section
                        else:
                            url += '?section=%s' % section

            elif type == 'PhysicalInterface':
                # First we need to find the source device associated with this interface on the source fmc...
                # Get the device record...
                device_url = re.match(r'(.+?/devices/devicerecords/[^/]+)', url).group(1)
                device_record = self.source_responses_dict[device_url]
                device_name = device_record['json_dict']['name']
                device_id = device_record['json_dict']['id']
                device_type = device_record['json_dict']['type']
                if not device_id in id_mapping: # we've already found this devices new id if a mapping exists...
                    # Strip the source device id...
                    device_url = prepare_url_for_migration(device_url, device_record, id_mapping)
                    new_device_id = get_item_id(device_url, device_name, device_type, response_dict)
                    if new_device_id is None:
                        logger.warning('Could not obtain new_device_id for PhysicalInterface with url %s, type %s \
                                        and name %s.  Returning None...' % (url, device_type, device_name))
                        return None
                    else:
                        id_mapping[device_id] = new_device_id

            # # Replace the host with ours
            # url = re.sub(r'https://[^/]+', 'https://' + self.FMC_host, url)

            # Replace the path root with ours
            url = re.sub(r'https://.+?domain/[^/]+/', self.path_root, url)
            # get the id
            id = response_dict['json_dict']['id']
            # Strip the id's
            url = re.sub('/' + id, '', url)
            # Replace any source container ids with the new ones...
            url_parts = re.split(r'/+', url)
            for url_part in url_parts:
                if url_part in id_mapping:
                    url = url.replace(url_part, id_mapping[url_part])

            return url

        # TODO handle params (url not needed) and replace domain id and id before posting
        def process_child_urls(url, response_dict, parent_url):
            print('processing child url %s for migration' % url, file=sys.stderr)
            if 'type' in response_dict['json_dict']:
                if response_dict['json_dict']['type'] in exclude_types:
                    logger.warning('type %s matched exclude pattern.  Skipping...' % response_dict['json_dict']['type'])
                    return
            else:
                types = tree_helpers.get_jsonpath_values('$..type', response_dict['json_dict'])
                if not types:
                    logger.warning('No type found (empty set?) for response_dict %s.  Skipping...' % response_dict['json_dict'])
                    return
            if 'processed' in response_dict:
                logger.info('url %s already processed' % url)
                return
            url_type = get_url_type(url, response_dict)
            if url_type == 'container':  # Got a container, need to create it
                post_container(url, response_dict)
            if response_dict['json_dict']:
                if 'child_urls' in response_dict:
                    if response_dict['child_urls']:
                        for child_url in response_dict['child_urls']:
                            extended_child_urls = get_parametered_urls_from_child_url(child_url)
                            for extended_child_url in extended_child_urls:
                                if extended_child_url == parent_url: # circular parent/child (securityzones/physicalint)
                                    logger.warning('Encountered circular parent %s and child %s' % \
                                                   (parent_url, extended_child_url))
                                    continue
                                if extended_child_url in self.source_responses_dict:
                                    child_url_response = self.source_responses_dict[extended_child_url]
                                    process_child_urls(extended_child_url, child_url_response, url)
                                else:
                                    logger.warning('No source response found for child url %s in source url response \
                                                    %s' % (extended_child_url, url))

                    # Create this object
                    if url_type == 'end_object':
                        post_end_object(url, response_dict)
                    elif url_type == 'composite_object':
                        post_composite_object(url, response_dict)
            return

        def recurse_migrate_config(source_responses_dict):
            for url, response_dict in self.source_responses_dict.items():
                source_domain_id = re.match(r'.+?/domain/([^/]+)', url).group(1)
                id_mappings[source_domain_id] = self.FMC_domain_ID
                process_child_urls(url, response_dict, '')

        self.source_responses_dict = OrderedDict()

        exclude_types = ['Device',]

        id_mappings = {}
        name_to_id_mappings = {}
        tree_helpers.restore_responses(source_config_path, self.source_responses_dict)
        source_responses_urls = list(self.source_responses_dict.keys())
        recurse_migrate_config(self.source_responses_dict)

    @logged(logger)
    @traced(logger)
    def _request_wrapper(self, recursed=False, **kwargs):

        """Wraps all requests for an FMC leaf in order to handle FMC specifics such at re-auth and rate limit.
        This should only be called by internal methods.

        *Parameters*

        recursed: boolean, keyword, default=False
            Signals if this is the top level call.
        \*\*kwargs: dictionary
            Used to pass through arguments to wrapped methods.
        """

        time_diff = time.time() - self._auth_token_time
        if time_diff > 1500:  # 1500 = 25 minutes...
            logger.info('Refreshing authentication token...')
            if self._refresh_token_count < 3:
                self._refresh_token_count += 1
            else:
                logger.info('Token has been refreshed the maximum of 3 times, requesting new token...')
                self._refresh_token_count = 0
                self._auth_headers.pop('X-auth-access-token')
                self._auth_headers.pop('X-auth-refresh-token')
            self._get_token_and_domains()

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
                        'FMC reports requests per minute exceeding 120.  Sleeping for self._backoff_timer seconds...')
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
    def _handle_anomalous_types(self, type_dict):

        """This method handles API model anomalies in order to find child_urls for these object types.
        This should only be called by internal methods.

        Returns: child_url for this anomalous type

        *Parameters*

        type_dict: The anomalous type dictionary from the json request.
        """

        logger.warning('Handling anomalous type dict %s' % type_dict)
        # turn off response persistence
        persist_responses = self.persist_responses
        self.persist_responses = False
        child_url = ''
        type = type_dict['dict']['type']
        id = type_dict['dict']['id']
        name = type_dict['dict']['name']
        if type == 'PhysicalInterface':
            if not type in self.anomalous_response_cache:
                responses_dict = self.walk_API_path_gets(url='devices/devicerecords', responses_dict={})
                device_ids = tree_helpers.get_objectpath_values("$..items[@.type is 'Device'].id", responses_dict)
                for device_id in device_ids:
                    responses_dict = self.GET_API_path(url='devices/devicerecords/%s' % device_id,
                                                       responses_dict=responses_dict)
                    responses_dict = self.GET_API_path(url='devices/devicerecords/%s/physicalinterfaces' % device_id,
                                                       responses_dict=responses_dict)
                self.anomalous_response_cache[type] = responses_dict
            device_ids = tree_helpers.get_objectpath_values("$..items[@.type is 'Device'].id",
                                                            self.anomalous_response_cache[type])
            interface_ids = tree_helpers.get_objectpath_values("$..items[@.type is 'PhysicalInterface'].id",
                                                               self.anomalous_response_cache[type])

            for device_id in device_ids:
                device_interface_url = '{}{}{}/{}'.format(self.path_root, 'devices/devicerecords/', device_id,
                                                          'physicalinterfaces')
                device_interfaces = None
                for url, val in self.anomalous_response_cache[type].items():
                    if device_interface_url in url:
                        device_interfaces = val
                interface_ids = tree_helpers.get_objectpath_values("$..items[@.type is 'PhysicalInterface'].id",
                                                                   device_interfaces)
                for interface_id in interface_ids:
                    if interface_id == id:
                        child_url = \
                            '{}{}{}/{}{}'.format(self.path_root, 'devices/devicerecords/', device_id,
                                                 'physicalinterfaces/', interface_id)
        # Restore persist response state
        self.persist_responses = persist_responses
        return child_url

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

        def recurse_for_child_dicts(json_dict, parent_key, type_list):
            if type(json_dict) is dict or type(json_dict) is OrderedDict:
                if 'type' in json_dict and not parent_key == '':
                    parent_key += '~' + json_dict['type']
                for key, val in json_dict.items():
                    if type(val) is dict or type(val) is OrderedDict:
                        if 'type' in val:
                            type_list.append({'key': key, 'parent_key': parent_key, 'dict': val})
                        elif 'refType' in val:
                            type_list.append({'key': key, 'parent_key': parent_key, 'dict': val})
                        recurse_for_child_dicts(val, (parent_key + '~' if not parent_key == '' else '') + key, type_list)
                    elif type(val) is list:
                        for val_member in val:
                            val_dict = {key: val_member}
                            # recurse_for_child_dicts(val_dict, (parent_key + '~' if not parent_key == '' else '') + key, type_list)
                            recurse_for_child_dicts(val_dict, parent_key, type_list)
            elif type(json_dict) is list:
                for json_member in json_dict:
                    recurse_for_child_dicts(json_member, parent_key, type_list)

        anomalous_types = ['PhysicalInterface',
                           ]

        response_self_link = None
        response_self_id = None
        url = response_dict['url']
        child_urls = []
        child_types = {}
        if 'id' in response_dict['json_dict']:
            response_self_id = response_dict['json_dict']['id']
        else:
            logger.warning('id node not found for url %s...' % (url))
        temp_response_dict = response_dict['json_dict'].copy()
        if 'metadata' in temp_response_dict:
            temp_response_dict.pop('metadata')
        type_list = []
        recurse_for_child_dicts(temp_response_dict, '', type_list)

        for type_dict in type_list:
            child_url = ''
            if type_dict['key'] == 'literals':
                child_url = 'literal'
                # continue

            lower_first_func = lambda s: s[:1].lower() + s[1:] if s else ''
            id_type = ''
            if 'type' in type_dict['dict']:
                id_type = type_dict['dict']['type']
                if id_type in anomalous_types:
                    child_url = self._handle_anomalous_types(type_dict)
            else:
                id_type = 'missing_type_attribute'
                logger.warning('type attribute missing for child dict %s...' % type_dict)

            if child_url == '':
                if not id_type in self._models_path_dict \
                    and not type_dict['key'] in self._models_path_dict \
                    and not lower_first_func(id_type) in self._models_path_dict \
                    and not id_type.lower() in self._models_path_dict \
                        and not 'links' in type_dict['dict']:
                    logger.warning('no url found for child dict %s...' % type_dict)
                else:
                    logger.debug('child dict = %s' % type_dict)
                    if 'links' in type_dict['dict']:
                        if 'self' in type_dict['dict']['links']:
                            child_url = type_dict['dict']['links']['self']
                        else:
                            logger.warning(
                                'Child dictionary %s has a links node but self url is missing...' % type_dict)
                    elif not id_type == 'missing_type_attribute':
                        if id_type in self._models_path_dict:
                            child_url = self._models_path_dict[id_type]
                        elif type_dict['key'] in self._models_path_dict:
                            child_url = self._models_path_dict[type_dict['key']]
                        elif lower_first_func(id_type) in self._models_path_dict:
                            child_url = self._models_path_dict[lower_first_func(id_type)]
                        else:
                            child_url = self._models_path_dict[id_type.lower()]

                        logger.debug('child_model_url = %s' % (child_url))
                        if '{containerUUID}' in child_url:
                            if not response_self_id:
                                logger.warning(
                                    'Child type url %s needs a {containerUUID} but no parent id found...' % (child_url))
                            else:
                                child_url = child_url.replace('{containerUUID}', response_self_id)
                        if '{objectId}' in child_url:
                            if 'id' in type_dict['dict']:
                                object_id = type_dict['dict']['id']
                                child_url = child_url.replace('{objectId}', object_id)
                            else:
                                logger.warning('Child type url %s needs an {objectId} but no id found...' % (child_url))
            if not child_url == '':
                # Safeguard to prevent child url returning parent url - deployabledevice
                if not child_url == re.sub('\?.+', '', response_dict['url']):
                    # Add the root path in if missing...
                    if self.path_root not in child_url and not child_url == 'literal':
                        child_url = self.path_root + child_url
                    type_parent = type_dict['parent_key']
                    if type_parent == '':
                        type_parent = id_type
                    else:
                        type_parent = type_parent + '~' + id_type
                    if type_parent not in child_types:
                        child_types[type_parent] = {'urls': [], 'type_dicts': []}
                    child_types[type_parent]['urls'].append(child_url)
                    type_dict['url'] = child_url
                    child_types[type_parent]['type_dicts'].append(type_dict)
                    if not child_url == 'literal':
                        child_urls.append(child_url)
                else:
                    logger.warning('Child url %s resolved to parent url' % child_url)
            else:
                logger.warning('no url found for child dict %s ' % type_dict)
        return child_urls, child_types

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

        """Returns a list of all valid API paths for the FMC host.

        Returns a list of all the valid API paths for this FMC host.  Contains the domain id for the FMC but container
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

        """Reads the current json FMC API model into a Python dictionary and build all required reference
        dictionaries.

        Returns a Python dictionary object containing json model.

        Processing the json model file takes up to one minute.  Therefore, this method will check to see if the model
        has changed since the last run.  It it is the same it will restore the json model dictionary and all derived
        reference dictionaries from pickled files.
        
        Pickles all newly created Python dictionaries if required.

        *Parameters*

        json_file_path: string, keyword, default=None
            The path to the json model file.  This file is typically named 'api-docs-fmcwithll.json' and obtained
            from the target FMC.  Typically resides in the directory
            /var/opt/CSCOpx/MDC/tomcat/vms/api/api-explorer/api.
            This file provides the API model to MAPLE:FMC which is used for many of the operations to derive urls, etc.
        """

        last_model_specs = {'last_model_file_size':None, 'last_model_mod_date': None}
        last_model_file = '{}.{}'.format(self.json_file_path, 'last.pickle')
        last_model_file_size = os.path.getsize(self.json_file_path)
        last_model_mod_date = os.path.getmtime(self.json_file_path)
        self._json_dict = None
        if os.path.exists(last_model_file):
            with open(last_model_file, 'rb') as f:
                last_model_specs = _pickle.load(f)
            if last_model_file_size == last_model_specs['last_model_file_size'] and \
                    last_model_mod_date == last_model_specs['last_model_mod_date']:
                last_model_pickle = '{}.{}'.format(self.json_file_path, 'pickle')
                if os.path.exists(last_model_pickle):
                    with open(last_model_pickle, 'rb') as f:
                        self._json_dict = _pickle.load(f)

        if self._json_dict is None:
            # Made it this far so we need to load file from disk
            last_model_specs['last_model_file_size'] = last_model_file_size
            last_model_specs['last_model_mod_date'] = last_model_mod_date
            with open(last_model_file, 'wb') as f:
                _pickle.dump(last_model_specs, f)
            self._json_dict = json.load(open(self.json_file_path, 'r'))

        reference_dicts_file = '{}.{}'.format(self.json_file_path, 'reference_pickle')
        reference_dicts = {}
        self._models_path_dict = None
        if os.path.exists(reference_dicts_file):
            with open(reference_dicts_file, 'rb') as f:
                reference_dicts = _pickle.load(f)
            if last_model_file_size == reference_dicts['last_model_file_size'] and \
                    last_model_mod_date == reference_dicts['last_model_mod_date']:
                self._resources_path_dict = reference_dicts['_resources_path_dict']
                self._operations_dict = reference_dicts['_operations_dict']
                self._models_path_dict = reference_dicts['_models_path_dict']
                self._paths_hierarchy = reference_dicts['_paths_hierarchy']
                self._API_path_keywords_list = reference_dicts['_API_path_keywords_list']
                self._all_API_paths_list = reference_dicts['_all_API_paths_list']
                self._path_models_dict = reference_dicts['_path_models_dict']
                self._models_dict = reference_dicts['_models_dict']

        if self._models_path_dict is None:
            self._resources_path_dict, self._operations_dict, self._models_path_dict, \
            self._paths_hierarchy, self._API_path_keywords_list, self._all_API_paths_list, \
            self._path_models_dict, self._models_dict = fmc_helpers.get_all_reference_dicts(self)

            reference_dicts['_resources_path_dict'] = self._resources_path_dict
            reference_dicts['_operations_dict'] = self._operations_dict
            reference_dicts['_models_path_dict'] = self._models_path_dict
            reference_dicts['_paths_hierarchy'] = self._paths_hierarchy
            reference_dicts['_API_path_keywords_list'] = self._API_path_keywords_list
            reference_dicts['_all_API_paths_list'] = self._all_API_paths_list
            reference_dicts['_path_models_dict'] = self._path_models_dict
            reference_dicts['_models_dict'] = self._models_dict

            reference_dicts['last_model_file_size'] = last_model_file_size
            reference_dicts['last_model_mod_date'] = last_model_mod_date

            with open(reference_dicts_file, 'wb') as f:
                _pickle.dump(reference_dicts, f)

    def get_all_models_dict(self):
        """Returns the model dictionary created from the model input file.
        
        Returns a Python dictionary created from the json model input file.

        """
        
        return self._models_dict
    
    def get_domain_id(self, domain='Global'):
        """Returns the id of the given domain.
        
        Returns the id of the domain name given in the arugment.  This is the id to use in API calls 
        for the respective domain.

        *Parameters*

        domain : string
            The domain name for which to retrieve the id.
        """
                
        return self.domain_ID_dict[domain]
            
    def get_all_API_paths_list(self):
        """Returns a list of all valid API paths for the FMC host.
        
        Returns a list of all the valid API paths for this FMC host.  Contains the domain id for the FMC but container and object
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
            request_templates_dict[key] = fmc_helpers.build_request_template_from_model(val)

    def _build_flattened_model_dict_by_name(self,model_name):
        """
        Under construction...
        """

        flatlined = output_transforms.flatten_json(self._models_dict[model_name])

        return flatlined

    def _get_token_and_domains(self):
        """
        Under construction...
        """

        # Get a security token valid for 30 minutes.  Record the time to check for validity
        self._auth_token_time = time.time()
        response_dict, status, include_filtered, exclude_filtered, cache_hit = \
            tree_helpers.process_json_request(url=self._auth_url, responses_dict=self.responses_dict,
                                              method='post', headers=self._auth_headers, stop_on_error=True,
                                              credentials_dict=self.credentials_dict, success_status_code=204,
                                              verify=self.verify)

        auth_headers = response_dict['headers']
        self._auth_token = auth_headers.get('X-auth-access-token', default=None)
        self._refresh_token = auth_headers.get('X-auth-refresh-token', default=None)
        if self._auth_token is None:
            logger.error('auth_token not found.  Returned headers = ', auth_headers, '\nExiting...')
            sys.exit()
        self.domain_ID_dict = fmc_helpers.get_domain_dict(auth_headers)
        self.request_headers['X-auth-access-token'] = self._auth_token
        self._auth_headers['X-auth-access-token'] = self._auth_token
        self._auth_headers['X-auth-refresh-token'] = self._refresh_token

    def build_response_pivot(self, csvfile):

        fmc_helpers.build_response_pivot(self.responses_dict, csvfile)

    # Begin TODO, rework and under construction
    ################################################################################################################
    def _convert_model_to_request_template(self,model_dict):
        """
        Under construction...
        """
        
        pass

    def _get_model(self):
        """
        Under construction...
        """
        
        pass
        
    def _get_request_template_by_model_ID(self,model_ID):
        """
        Under construction...
        """
        
        pass
    
    def _get_request_template_by_path(self,model_ID):
        """
        Under construction...
        """
        
        pass
    
    def _transform_responses(self,responses_dict,field_filter_regex=None):
        """
        Under construction...
        """
        pass
        
    def _get_API_path_request_template(self):
        """
        Under construction...
        """
        
        pass
    
    def _refresh_API_gets(self):
        """
        Under construction...
        """
        # Walk the existing responses and refreshes the data (accounts for oob changes, etc.)

        pass
