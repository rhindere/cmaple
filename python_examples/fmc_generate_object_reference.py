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

import re, sys, os, csv
sys.path.insert(0, r'C:\Users\rhindere\Documents\PycharmProjects\maple_project')
from cmaple.tree import CMapleTree
from cmaple import tree_helpers
import cmaple.output_transforms as output
from pprint import pprint
from collections import OrderedDict
import csv

##############################################################################################################
# Modify the values in this section for your environment
##############################################################################################################
maple_tree_name = 'tree_1'
# Path to a directory where the working directories and files will be created
maple_tree_dir = r'test_output'
# Path to the 'api-docs-fmcwithll.json' file
# CMAPLE bases most FMC operations on the current API model as defined in the file
# named ‘api-docs-fmcwithll.json’ and obtained from the target FMC. This file currently
# resides in the directory ‘/var/opt/CSCOpx/MDC/tomcat/vms/api/api-explorer/api’.
# This file provides the API model to CMAPLE:FMC which is used for many of the operations
# to derive urls, etc. This file can be copied from the target FMC using scp and placed
# in a directory of the users choice.
model_json_file = os.path.join('.', 'api-docs-fmcwithll.json')
# The host information for the source FMC (from which policies will be retrieved)
FMC_src_host = '10.1.101.40'
FMC_src_port = 443
FMC_src_leaf_name = 'fmc_leaf_1'
FMC_src_username = 'rest_admin'
FMC_src_password = 'C1sc0123'
##############################################################################################################

# Create a cmaple tree instance...
maple_tree = CMapleTree(logging_level='INFO', name=maple_tree_name,
                        tree_dir=maple_tree_dir)

# Attach a cmaple fmc leaf instance for the source fmc to the tree...

FMC_src_leaf = maple_tree.add_leaf_instance('fmc', name=FMC_src_leaf_name, json_file_path=model_json_file,
                                            FMC_host=FMC_src_host, FMC_port=FMC_src_port,
                                            FMC_username=FMC_src_username,
                                            FMC_password=FMC_src_password,
                                            default_get_item_limit=200,
                                            restore_responses=True,
                                            connect_device=True)

FMC_src_leaf.walk_API_path_gets(url='policy/accesspolicies')
FMC_src_leaf.walk_API_path_gets(url='policy/ftdnatpolicies')

csvfile = open('csv_file.csv', 'w', newline='')

FMC_src_leaf.build_response_pivot(csvfile)

