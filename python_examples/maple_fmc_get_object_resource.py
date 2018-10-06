#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

maple_amp_test.py - Example script for MAPLE amp API operations.

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

from maple.tree import MapleTree
from pprint import pprint

# Create a maple tree instance...
maple_tree = MapleTree(logging_level='INFO', name='amp_test', tree_dir=r'C:\Users\rhindere\Documents\maple_working_dir')

# Attach a maple fmc leaf instance to the tree...
model_json_file=r'C:\Users\rhindere\Documents\PycharmProjects\maple_project\maple\fmc\api-docs-fmcwithll.json'
FMC_leaf = maple_tree.add_leaf_instance('fmc',name='10.1.101.39_Global',
                                        json_file_path=model_json_file, FMC_host='10.1.101.39',
                                        FMC_username='rest_admin', FMC_password='C1sc0123',
                                        default_get_item_limit=200)

# Use the fmc leaf method walk_API_resource_gets to recursively walk the resource paths.
# Use the key parameter "include_filter_regex" with pattern r'/object' to exclude all resource paths except "object"
FMC_leaf.walk_API_resource_gets(include_filter_regex=r'/object')
pprint(FMC_leaf.responses_dict)
