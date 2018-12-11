#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

cmaple_set_policy_logging.py - Example showing retrieving an access policies
rules and toggling the logBegin setting.
Replace operational parameters as required.

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

import os, sys
#sys.path.insert(0, r'C:\Users\rhindere\Documents\PycharmProjects\maple_project')

from cmaple.tree import CMapleTree
from pprint import pprint
import sys

maple_tree = CMapleTree(logging_level='INFO', name='cmaple_tree_1', tree_dir=r'.')
model_json_file = r'api-docs-fmcwithll.json'
FMC_leaf = maple_tree.add_leaf_instance('fmc',name='fmc_1', json_file_path=model_json_file,
                                        FMC_host='10.1.101.39', FMC_username='rest_admin', FMC_password='C1sc0123',
                                        default_get_item_limit=200)

# Use smart_get_object_id to retrieve object ids by objectpath query...
smart_ap_url = "policy/accesspolicies/$..items[@.name is 'test_migration_policy_1'].id"
ap_id = FMC_leaf.smart_get_object_id(url=smart_ap_url)
accessrule_items = FMC_leaf.GET_API_path(url='policy/accesspolicies/%s/accessrules' % ap_id, responses_dict={})
id_list = FMC_leaf.query_json_field(query_field="items[@.type is 'AccessRule'].id", json_to_query=accessrule_items)
accessrule_json = FMC_leaf.query_with_list(query_url='policy/accesspolicies/%s/accessrules/~id~' % ap_id,
                                           query_list=id_list,
                                           responses_dict={})

for rule_url, rule_dict in accessrule_json.items():
    rule_json = rule_dict['json_dict']
    new_json = FMC_leaf.set_json_properties(rule_json, {'logBegin': not rule_json['logBegin']})
    print('nj=')
    pprint(new_json)
    prep_json = FMC_leaf.prep_put_json(json_dict=new_json)
    print('pj=')
    pprint(prep_json)
    put_response = FMC_leaf.put_json_request(url=rule_url, json_dict=prep_json)
    pprint(put_response)
