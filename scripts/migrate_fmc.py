#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

migrate_fmc.py - Example script to migrate policies from one FMC to
another using the API.

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

from cmaple.tree import CMapleTree
import cmaple.output_transforms as output
from pprint import pprint

# Create a cmaple tree instance...
maple_tree = CMapleTree(logging_level='INFO', name='amp_test',
                        tree_dir=r'C:\Users\rhindere\Documents\maple_working_dir')

# Attach a cmaple fmc leaf instance for the source fmc to the tree...
model_json_file=r'C:\Users\rhindere\Documents\PycharmProjects\maple_project\cmaple\fmc\api-docs-fmcwithll.json'

FMC_src_leaf = maple_tree.add_leaf_instance('fmc', name='src_fmc', json_file_path=model_json_file,
                                            FMC_host='10.1.101.40', FMC_username='rest_admin', FMC_password='C1sc0123',
                                            default_get_item_limit=200)

# Get all device records
dr = FMC_src_leaf.get_all_items(url='devices/devicerecords')
# Get a list of all the device ids
did = FMC_src_leaf.query_json_field(query_field='items.id',json_to_query=dr)
# Run multiple get iterating over values in the device id list substituting each value in the list for ~id~
# Define the query url.  ~id~ is the value to substitute for each item 
drs = 'devices/devicerecords/~id~'
drq = FMC_src_leaf.query_with_list(query_url=drs, query_list=did)
pp_drq = output.pretty_print(_object=drq)
# Get all physical interfaces for each device
# Run multiple get iterating over values in the device id list substituting each value in the list for ~id~
# Define the query url.  ~id~ is the value to substitute for each item 
piu = 'devices/devicerecords/~id~/physicalinterfaces'
piq = FMC_src_leaf.query_with_list(query_url=piu, query_list=did)
pp_piq = output.pretty_print(_object=piq)
# Get the nat policies
nat = FMC_src_leaf.walk_API_path_gets(url='policy/ftdnatpolicies')
pp_nat = output.pretty_print(_object=nat)
# Get the access policies
ap = FMC_src_leaf.walk_API_path_gets(url='policy/accesspolicies')
pp_ap = output.pretty_print(_object=ap)
# All finished with the source fmc, add a leaf to the tree for the destination fmc
FMC_dst_leaf = maple_tree.add_leaf_instance('fmc', name='dst_fmc', json_file_path=model_json_file,
                                            FMC_host='10.1.101.39', FMC_username='rest_admin', FMC_password='C1sc0123',
                                            default_get_item_limit=200)
# Get the source leaf directory so we can read the source response data
src_leaf_dir = FMC_src_leaf.get_leaf_dir()
# Run the migrate method
migrate = FMC_dst_leaf.or_migrate_config(source_config_path=src_leaf_dir)
