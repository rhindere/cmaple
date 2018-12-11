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

# Create a logger for cmaple.asa.asa_helpers...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))


@logged(logger)
@traced(logger)
def get_all_reference_dicts(ASA_instance):

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
    resource_tuple_list = tree_helpers.get_jsonpath_full_paths_and_values('$.features.*.[*]',ASA_instance._json_dict)
    all_paths = tree_helpers.get_jsonpath_full_paths_and_values('$..path',resource_tuple_list)
    # pprint(all_paths)
    # sys.exit()
    # pprint(resource_tuple_list)
    for i in range(0,len(resource_tuple_list)):
        resource_dict = resource_tuple_list[i][1]
        base_path = resource_dict['resourcePath']
        resource_key = re.sub('/','',base_path)
        API_version = resource_dict['apiVersion']
        resource_path_dict[resource_key] = ''
        # models_list = tree_helpers.get_jsonpath_full_paths_and_values('$..models.*.id',resource_dict)
        # for model in models_list:
        #     if not model is None:
        #         model_path = model[0]
        #         model_ID = model[1]
        #         if not model_ID in models_dict:
        #             properties_path = model_path
        #             properties_path_list = properties_path.split('.')
        #             properties_path_list.pop()
        #             properties_path_list.append('properties')
        #             properties_path = '.'.join(properties_path_list)
        #             models_dict[model_ID] = tree_helpers.get_jsonpath_values(properties_path,resource_dict)[0]
        if not resource_dict['models']:
            model_ID = resource_key + 'NullModel'
        else:
            model_ID = list(resource_dict['models'])[0]
        operations_list = resource_dict['operations']
        for operation in operations_list:
            if not operation is None:
                if not model_ID == 'bulk':
                    path = re.sub('^/api/','',operation['path'])
                else:
                    path = 'bulk'
                method = operation['method']
                if model_ID not in model_path_dict:
                    model_path_dict[model_ID] = {'methods': {}, 'model': resource_dict['models']}
                if method not in model_path_dict[model_ID]['methods']:
                    model_path_dict[model_ID]['methods'][method] = path
                if path not in path_model_dict:
                    path_model_dict[path] = {'methods': {}, 'model': resource_dict['models']}
                if method not in path_model_dict[path]['methods']:
                    path_model_dict[path]['methods'][method] = model_ID
                if path not in operations_dict:
                    operations_dict[path] = {'methods':{},'operation_path':path, 'model': resource_dict['models']}
                if method not in operations_dict[path]['methods']:
                    operations_dict[path]['methods'][method] = operation
    # pprint(resource_path_dict)
    for path in operations_dict.keys():
        operation_path = operations_dict[path]['operation_path']
        all_API_paths_list.append(path)
        path_parts = operation_path.split('/')
        # print(path_parts)
        if len(path_parts) == 0:
            continue
        resource_path = path_parts[0]
        if resource_path and resource_path in resource_path_dict:
            base_path = resource_path_dict[resource_path]
        else:
            continue
        add_paths_to_dict(path_parts, paths_dict, API_path_keywords_list)
    
    all_API_paths_list.sort()
    # pprint(all_API_paths_list)
    API_path_dict = {}

    def build_API_path_dict(API_path_dict, API_path_parts):
        API_path_part = API_path_parts.pop(0)
        if API_path_part not in API_path_dict:
            API_path_dict[API_path_part] = {}
        if len(API_path_parts) > 0:
            build_API_path_dict(API_path_dict[API_path_part], API_path_parts)

    for API_path in all_API_paths_list:
        build_API_path_dict(API_path_dict, API_path.split('/'))

    return OrderedDict(sorted(resource_path_dict.items())), \
           OrderedDict(sorted(operations_dict.items())), \
           OrderedDict(sorted(model_path_dict.items())), \
           OrderedDict(sorted(paths_dict.items())), \
           API_path_keywords_list, \
           all_API_paths_list, \
           path_model_dict, \
           models_dict, \
           API_path_dict


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
