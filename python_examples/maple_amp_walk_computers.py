#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

maple_amp_walk_computers.py - Example script for MAPLE amp API operations.

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
import re, sys
import _pickle

AMP_API_client_ID = 'your AMP API ID'
AMP_API_key = 'your AMP API key'

maple_tree = MapleTree(logging_level='INFO', name='amp_test',
                       tree_dir=r'C:\Users\rhindere\Documents\maple_working_dir')
AMP_leaf = maple_tree.add_leaf_instance('amp',name='Hackathon', AMP_host='api.amp.cisco.com',
                                        AMP_API_client_ID=AMP_API_client_ID, AMP_API_key=AMP_API_key,
                                        default_get_item_limit=200)

AMP_leaf.walk_API_path_gets('v1/computers')
pprint(AMP_leaf.responses_dict)

