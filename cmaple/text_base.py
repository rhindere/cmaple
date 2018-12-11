#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

rest_base.py implements generic REST functionality.  The class TextBase
is designed to be sub classed only.

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

import sys
import os
import re
import cmaple.tree_helpers as tree_helpers
from cmaple.tree_helpers import set_default as sd
import cmaple.input_validations as input_validations
import cmaple.output_transforms as output_transforms
from collections import OrderedDict
from pprint import pprint, pformat
import logging
from autologging import logged, traced
from autologging import TRACE
import time

# Create a logger...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))
# Define global variables

@logged(logger)
@traced(logger)
class TextBase(object):

    """
    This class defines generic text functionality.

    Classes sub classing this class will need to override specific methods and properties as called out in the
    method docstrings and inline comments.

    Method names not beginning with "_" are made available to cmaple_cli.py for use in operations config files.

    """

    def __init__(self):

        """__init__ TextBase inherits arguments from the parent class.  All argument validation is
        performed by the parent class.
        """

        if self.restore_responses:
            tree_helpers.restore_responses(self.leaf_dir, self.responses_dict)

