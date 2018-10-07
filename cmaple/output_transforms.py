#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

output_transforms.py implements various helper functions for output.

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

import re,sys,io,csv
from pprint import pprint
from cmaple.tree_helpers import get_jsonpath_values
from collections import OrderedDict
import json
import _pickle
import logging
from autologging import logged, traced
from autologging import TRACE

logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))


@logged(logger)
@traced(logger)
def pretty_print(_object=None, file=sys.stdout):
    """Pretty Prints the '_object' to 'file'.


    """

    pprint(_object, file)


@logged(logger)
@traced(logger)
def tabbed_print(_object=None):
    """Alias for pretty_print.

    """

    pprint(_object)


@logged(logger)
@traced(logger)
def create_pickle(struct=None,file=''):
    """Pickles 'struct' to 'file'.

    """

    pickle_file = open(file, 'wb')
    _pickle.dump(struct, pickle_file)
    pickle_file.close()


@logged(logger)
@traced(logger)
def create_outline(_dict=None,tab_string='',file=sys.stdout,smart_labels=True,responses_only=False):
    """Creates an outline of '_dict' to 'file'.

    """

    def get_list_item_label(_dict):
        if 'name' in _dict:
            if type(_dict['name']) is str:
                return 'name', _dict['name']
        elif 'models' in _dict:
            if type(_dict['models']) is str:
                return 'models', _dict['models']
            elif type(_dict['models']) is dict:
                return 'models', list(_dict['models'].keys())[0]
        elif 'content-type' in _dict:
            if type(_dict['content-type']) is str:
                return 'content-type', _dict['content-type']
            elif type(_dict['models']) is dict:
                return 'content-type', list(_dict['content-type'].keys())[0]
        for key, val in _dict.items():
            if type(val) is str:
                if re.match(r'^[a-zA-Z]+$',val):
                    if re.match(r'^[A-Z]+$',val) or \
                            re.match(r'^[A-Z][a-z]+[A-Z][a-z]+$',val) or \
                            re.match(r'^[a-z]+[A-Z][a-z]+$',val):
                        return key, val
        return None
        
    def process_val(val, tab_string):
        if type(val) is dict:
            process_dict(val,tab_string)
        elif type(val) is list:
            process_list(val,tab_string)
        else:
            if type(val) is str and '-----BEGIN ' in val:
                val = 'Certificate Encoding Omitted...'
            print(tab_string+str(val),file=file)

    def process_list(_list, tab_string):
        print(tab_string+'list',file=file)
        tab_string += '\t'
        list_counter = 0
        for val in _list:
            if type(val) is dict:
                if smart_labels:
                    label = get_list_item_label(val)
                    if not label is None:
                        print(tab_string+label[0]+'='+label[1],file=file)
                    else:
                        list_counter+=1
                        print(tab_string+str(list_counter),file=file)
                else:
                    list_counter+=1
                    print(tab_string+str(list_counter),file=file)
                process_val(val,tab_string + '\t')
            else:
                process_val(val,tab_string)

    def process_dict(_dict,tab_string):
        print(tab_string+'dict',file=file)
        tab_string += '\t'
        for key, val in _dict.items():
            print(tab_string+key,file=file)
            process_val(val,tab_string+'\t')

    print(_dict)
    print('...in create outline...')
    if responses_only:
        _dict = get_jsonpath_values('$..json_dict',_dict)
        print(_dict)
    outline_str = ''
    process_val(_dict,tab_string)


@logged(logger)
@traced(logger)
def create_response_flatline(responses_dict,field_filter_regex='',file=None):
    """Creates a flatline dictionary for 'responses_dict'.

    """

    flatlines={}
    for response_url, response_dict in responses_dict.items():
        if response_dict['json_dict'] is None:
            continue
        pprint(response_dict['json_dict'])
        flatlined = flatten_json(response_dict['json_dict'])
        pprint(expand_flattened_json(flatlined))
        flatlined_keys = list(flatlined.keys())
        flatlined_keys.sort()
        flatlined_fields = []
        for flatlined_key in flatlined_keys:
            if not re.search(field_filter_regex, flatlined_key):
                flatlined_fields.append(flatlined_key)
        if 'type' in response_dict['json_dict']:
            qualifier = response_dict['json_dict']['type']
        else:
            qualifier = re.sub('\?[^?]+$','',response_url)
        flatlined_signature = qualifier + '~' + re.sub(r'items~[^,]+,*','',','.join(flatlined_fields))
        if not flatlined_signature in flatlines:
            csv_string = io.StringIO(newline=None)
            csv_dict_writer = csv.DictWriter(csv_string,fieldnames=flatlined_fields,extrasaction='ignore')
            flatlines[flatlined_signature] = {'writer':csv_dict_writer,'StringIO':csv_string,'signature':flatlined_signature}
            csv_dict_writer.writeheader()
        flatlines[flatlined_signature]['writer'].writerow(flatlined)
    return flatlines

@logged(logger)
@traced(logger)
def csv_to_flatlined(csv_list=None):

    flatlined_list = []
    keys_string = csv_list.pop(0)
    keys = keys_string.split(',')
    csv_records = csv.reader(csv_list,dialect='excel')
    for csv_record in csv_records:
        record_dict = dict(zip(keys,csv_record))
        flatlined_list.append(record_dict)
    return flatlined_list

@logged(logger)
@traced(logger)
def csv_to_bulk_post_body(file_path=None):

    csv_list = create_list_from_csv(file_path)
    post_body_list = []
    flatlined_list = csv_to_flatlined(csv_list)
    for flatlined in flatlined_list:
        post_body_list.append(expand_flattened_json(flatlined))
    post_body_json = json.dumps(post_body_list)
    return post_body_json

@logged(logger)
@traced(logger)
def create_list_from_csv(file_path=None):

    csv_file = open(file_path, 'r')
    csv_list = []

    for line in csv_file.readlines():
        if not line == '\n':
            csv_list.append(line.strip())

    csv_file.close()

    return csv_list

@logged(logger)
@traced(logger)
def create_csv_from_flatline(flatlined=None,field_filter_regex='',file=None):
    flatlined_keys = list(flatlined.keys())
    flatlined_keys.sort()
    flatlined_fields = []
    field_name_string = ''
    field_value_string = ''
    for flatlined_key in flatlined_keys:
        print(flatlined_key)
        if not re.search(field_filter_regex, flatlined_key):
            flatlined_fields.append(flatlined_key)
    for flatlined_field in flatlined_fields:
        field_name_string += flatlined_field + ','
        value_string = str(flatlined[flatlined_field])
        if ',' in value_string:
            value_string = '"' + value_string + '"'
        field_value_string += value_string + ','
    return field_name_string + '\n' + field_value_string

@logged(logger)
@traced(logger)
def flatten_json(y):
    
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '~')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + '%06d' % (i) + '~')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

    flat = flatten(y)
    return flat

@logged(logger)
@traced(logger)
def expand_flattened_json(flattened_json_dict):
    
    def recurse_flattened_json_dict(key, val, json_dict):
    
        key_parts = key.split('~')
        key_part = key_parts.pop(0)
        if not key_parts:
            if type(val) is str:
                if 'false' == val.lower():
                    val = 'false'
                elif 'true' == val.lower():
                    val = 'true'
            json_dict[key_part] = val
            return
        elif re.match(r'\d{6}',key_parts[0]):
            list_index = int(key_parts[0])
            if not key_part in json_dict:
                if len(key_parts) == 1:
                    if 'false' == val.lower():
                        val = 'false'
                    if 'true' == val.lower():
                        val = 'true'
                    json_dict[key_part] = [val]
                    return
                else:
                    json_dict[key_part] = [{}]
            elif list_index > len(json_dict[key_part])-1:
                if len(key_parts) == 1:
                    json_dict[key_part].append(val)
                    return
                else:
                    json_dict[key_part].append({})
            recurse_flattened_json_dict('~'.join(key_parts[1:]), val, json_dict[key_part][-1])
        else:
            if not key_part in json_dict:
                json_dict[key_part] = {}
            recurse_flattened_json_dict('~'.join(key_parts), val, json_dict[key_part])
    
    json_dict = {}
    flattened_keys = list(flattened_json_dict.keys())
    flattened_keys.sort()
    for key in flattened_keys:
        recurse_flattened_json_dict(key, flattened_json_dict[key], json_dict)

    return json_dict

