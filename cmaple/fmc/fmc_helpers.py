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

import json
import importlib
import cmaple.tree_helpers as tree_helpers
#global_helpers = importlib.import_module('.tree_helpers', 'cmaple')
import logging
from collections import OrderedDict
from autologging import logged, traced
from autologging import TRACE
from pprint import pformat,pprint
import time
import sys
import re
import csv

# Create a logger for cmaple.fmc.fmc_helpers...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))


def build_response_pivot(responses_dict, csvfile):

    def recurse_child_types(_dict, fields, url_stack, field_stack, field_metadata, rows, parent_dict, parent_path):
        child_final_vals = {}
        rows.append(OrderedDict())
        rows[-1].update(parent_dict)
        rows[-1]['Parent_Path'] = parent_path
        row_pointer = rows[-1]
        for child_key, child_val in _dict['json_dict'].items():
            if type(child_val) is not dict and type(child_val) is not list:
                if child_key not in headers:
                    headers.append(child_key)
                rows[-1][child_key] = str(child_val)
                child_final_vals[child_key] = str(child_val)
            elif child_key == 'metadata':
                skip_keys = ['timestamp',
                             'lastUser',
                             'parentType',
                             'count']

                def gather_metadata(metadata_dict, metadata_fields, parent_key):
                    for metadata_key, metadata_val in metadata_dict.items():
                        if metadata_key in skip_keys:
                            continue
                        if type(metadata_val) is dict:
                            metadata_fields[metadata_key] = [{}]
                            gather_metadata(metadata_val, metadata_fields[metadata_key][-1], parent_key +
                                            ('~' + metadata_key if not parent_key == '' else metadata_key))
                        else:
                            this_key = parent_key + ('~' + metadata_key if not parent_key == '' else metadata_key)
                            if this_key not in headers:
                                headers.append(this_key)
                            metadata_fields[this_key] = str(metadata_val)
                            rows[-1][this_key] = str(metadata_val)

                fields[child_key] = [{}]
                gather_metadata(child_val, fields[child_key][-1], 'metadata')
        if child_final_vals:
            fields.update(child_final_vals)
        if 'child_types' in _dict and _dict['child_types']:
            child_types = _dict['child_types']
            for child_type_key, child_type_val in child_types.items():
                this_path = parent_path
                child_field_names = child_type_key.split('~')
                child_fields = fields
                field_metadata = {}
                tree_helpers.deep_update(field_metadata, fields)
                last_field = child_field_names.pop()
                for child_field_name in child_field_names:
                    if child_field_name not in child_fields:
                        child_fields[child_field_name] = []
                    this_path += '~' + child_field_name
                    child_fields[child_field_name].append({})
                    child_fields = child_fields[child_field_name][-1]
                for type_dict in child_type_val['type_dicts']:
                    child_url = type_dict['url']
                    if not child_url == 'literal':
                        if child_url in responses_dict:
                            child_dict = responses_dict[child_url]
                            if child_url not in url_stack and last_field not in field_stack:
                                if last_field not in child_fields:
                                    child_fields[last_field] = []
                                child_fields[last_field].append({})
                                url_stack.append(child_url)
                                field_stack.append(last_field)
                                circular = recurse_child_types(child_dict, child_fields[last_field][-1], url_stack,
                                                               field_stack, field_metadata, rows, parent_dict,
                                                               this_path + (
                                                                   '~' + last_field if not this_path == '' else last_field))
                                url_stack.pop()
                                field_stack.pop()
                            else:
                                return True
                    elif child_url == 'literal':
                        if last_field not in child_fields:
                            child_fields[last_field] = []
                        child_fields[last_field].append({})
                        for literal_key, literal_val in type_dict['dict'].items():
                            child_fields[last_field][-1][literal_key] = str(literal_val)

    flatlined_responses = {}
    headers = ['Parent_Type', 'Parent_Name', 'Parent_ID', 'Parent_Path', 'type', 'name', 'id']
    rows = []

    for key, val in responses_dict.items():
        parent_type = ''
        if val['json_dict'] is None:
            continue
        if 'type' in val['json_dict'] and 'id' in val['json_dict']:
            parent_type = val['json_dict']['type']
            parent_id = val['json_dict']['id']
        else:
            continue
        if 'name' in val['json_dict']:
            parent_name = val['json_dict']['name']
        if parent_type not in flatlined_responses:
            flatlined_responses[parent_type] = []
        flatlined_responses[parent_type].append({})
        parent_dict = OrderedDict({'Parent_Type': parent_type, 'Parent_Name': parent_name, 'Parent_ID': parent_id,
                                   'Parent_Path': parent_type, 'type': '', 'name': '', 'id': ''})
        recurse_child_types(val, flatlined_responses[parent_type][-1], [], [parent_type], [], rows, parent_dict, parent_type)

    csv_dict_writer = csv.DictWriter(csvfile, dialect='excel', fieldnames=headers)
    csv_dict_writer.writeheader()
    for type_row in rows:
        csv_dict_writer.writerow(type_row)
    return csvfile

@logged(logger)
@traced(logger)
def get_all_reference_dicts(FMC_instance):

    def add_paths_to_dict(path_parts, paths_dict, API_path_keywords_list):
        if path_parts:
            path_part = path_parts.pop(0)
            if not path_part in paths_dict:
                paths_dict[path_part] = {}
                if not path_part in API_path_keywords_list and not path_part.startswith('{'):
                    API_path_keywords_list.append(path_part)
            paths_dict = OrderedDict(sorted(paths_dict.items()))
            add_paths_to_dict(path_parts,paths_dict[path_part],API_path_keywords_list)
        else:
            return

    paths_dict = {}
    resource_path_dict = {}
    operations_dict = {}
    model_path_dict = {}
    path_model_dict = {}
    models_dict = {}
    API_path_keywords_list = []
    all_API_paths_list = []
    # Get the base paths
    resource_tuple_list = tree_helpers.get_jsonpath_full_paths_and_values('$.features.*.[*]',FMC_instance._json_dict)
    for i in range(0,len(resource_tuple_list)):
        resource_key = re.sub(r'features.|\[[0-9]+\]|\.','',resource_tuple_list[i][0])
        resource_dict = resource_tuple_list[i][1]
        base_path = resource_dict['basePath']
        API_version = resource_dict['apiVersion']
        # resource_root = FMC_instance._url_host + '/api' + base_path + '/' + API_version + '/domain/' + FMC_instance.FMC_domain_ID + '/'
        resource_path_dict[resource_key] = ''
        models_list = tree_helpers.get_jsonpath_full_paths_and_values('$..models.*.id',resource_dict)
        for model in models_list:
            if not model is None:
                model_path = model[0]
                model_ID = model[1]
                if not model_ID in models_dict:
                    properties_path = model_path
                    properties_path_list = properties_path.split('.')
                    properties_path_list.pop()
                    properties_path_list.append('properties')
                    properties_path = '.'.join(properties_path_list)
                    models_dict[model_ID] = tree_helpers.get_jsonpath_values(properties_path,resource_dict)[0]
        operations_list = tree_helpers.get_jsonpath_values('$..operations',resource_dict)
        for operation_list in operations_list:
            model_ID = None
            for operation in operation_list:
                if not operation is None:
                    path = re.sub('^/','',operation['path'])
                    method = tree_helpers.get_jsonpath_values('$..method',operation)[0]
                    if model_ID is None:
                        for example in operation['examples']:
                            if not 'override' in example['url']:
                                if 'responseData' in example:
                                    if 'type' in example['responseData']:
                                        model_ID = example['responseData']['type']
                                        break
                    if not path in operations_dict:
                        operations_dict[path] = {'methods': {}, 'operation_path': operation['path']}
                    operations_dict[path]['methods'][method] = operation
            if not model_ID:
                model_ID = operation_list[-1]['type']['modelId']
            # model_path_dict[model_ID] = path
            path = operation_list[-1]['path']
            path = re.sub('^/', '', path)
            model_path_dict[model_ID] = path
            path_model_dict[path] = model_ID
    for path in operations_dict.keys():
        operation_path = operations_dict[path]['operation_path']
        all_API_paths_list.append(path)
        path_parts = operation_path.split('/')
        path_parts.pop(0) # Get rid of the first '/'
        resource_path = path_parts[0]
        if resource_path in resource_path_dict:
            base_path = resource_path_dict[resource_path]
        else:
            continue
        add_paths_to_dict(path_parts,paths_dict,API_path_keywords_list)

    all_API_paths_list.sort()
    return OrderedDict(sorted(resource_path_dict.items())), OrderedDict(sorted(operations_dict.items())), \
           OrderedDict(sorted(model_path_dict.items())), OrderedDict(sorted(paths_dict.items())), \
           API_path_keywords_list, all_API_paths_list, path_model_dict, models_dict

@logged(logger)
@traced(logger)
def get_type_and_id_tuple_list(base_path,json_dict):
    type_list = tree_helpers.get_jsonpath_values(base_path+'.type',json_dict)
    id_list = tree_helpers.get_jsonpath_values(base_path+'.id',json_dict)
    return zip(type_list,id_list)

@logged(logger)
@traced(logger)
def validate_FMC_domain(FMC_Domain,FMC_domain_dict):
    
    def fmc_domain_string(FMC_domain_dict):
        return FMC_domain_dict.keys().join('\n')
    
    if FMC_Domain == 'Global':
        return FMC_Domain
    elif not isinstance(FMC_Domain,str):
        logger.error('A string value must be provided for the %s, provided value is of type %s...' % ('FMC Domain',type(FMC_Domain)))
        raise
    elif not FMC_Domain.startswith('Global/'):
        logger.error('The provided value for the "FMC Domain" is not "Global".',
                     'If a sub domain is the target, it must be prefixed with "Global/".',
                     'The provided value = %s...' % FMC_Domain)
        raise
    elif FMC_Domain not in FMC_domain_dict:
        logger.error('The provided value for the "FMC Domain" (%s) does not exist in the FMC.' % FMC_Domain,
                     'Valid domains names as follows:\n%s' % fmc_domain_string(FMC_domain_dict))
        raise
        
@logged(logger)
@traced(logger)
def get_domain_dict(headers):
    
    domains_dict = {}
    domain_list = json.loads(headers['DOMAINS'])
    for domain_dict in domain_list:
        domains_dict[domain_dict['name']] = domain_dict['uuid']
    return domains_dict
