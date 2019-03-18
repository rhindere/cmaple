#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

ssh_helpers.py implements various ssh helper functions.

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
import logging
from collections import OrderedDict
from autologging import logged, traced
from autologging import TRACE
from pprint import pformat,pprint
import time
import sys
import re

# Create a logger for cmaple.fmc.fmc_helpers...
logger = logging.getLogger(re.sub('\.[^.]+$', '', __name__))


@logged(logger)
@traced(logger)
def get_all_reference_dicts(SSH_instance):

    pass

@logged(logger)
@traced(logger)
def process_run_cmd(**kwargs):

    pass

