#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

win_base.py implements generic REST functionality.  The class RestBase
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
import xmltodict
from collections import OrderedDict
from pprint import pprint, pformat
import logging
from autologging import logged, traced
from autologging import TRACE
import time
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

# Create a logger...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))
# Define global variables

@logged(logger)
@traced(logger)
class XMLBase(object):

    """

    <todo add doc string>

    """

    def __init__(self):

        """

        <todo add doc string>

        """

        self.xml = ''
        self.xml_dict = {}

    def xml_to_dict(self, xml):
        return tree_helpers.listify_xml_dict(xmltodict.parse(xml))

    def dict_to_xml(self, xml_dict):
        return xmltodict.unparse(xml_dict, pretty=True)

    def load_xml_from_file(self, xml_file):
        with open(xml_file) as fd:
            self.xml = fd.read()
            self.xml_dict = self.xml_to_dict(self.xml)
        return self.xml_dict

    def write_xml_to_file(self, xml_file):
        with open(xml_file, 'w', encoding='utf-8') as fd:
            self.xml = self.dict_to_xml(self.xml_dict)
            fd.write(self.xml)
