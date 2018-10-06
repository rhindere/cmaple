#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

maple_cli.py is a high level interface to the functionality provided by
MAPLE (Multi-purpose API Programming Language Extension).  maple_cli.py
enables the following use cases:

    - Allows non programmers to use the advanced API capabilities of
    MAPLE without writing code.  Users of maple_cli.py define API
    operations in an operations config file using a simple macro syntax
    - maple_cli.py operations config files can be easily shared and
    reused.
    - maple_cli.py can be compiled to a binary for use on systems
    independent of a local Python installation.

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

import configparser
import collections
import argparse
import sys
import os
import re
from maple.tree import MapleTree
from maple.input_validations import *
import maple.output_transforms as output
from pprint import pprint
import logging
from autologging import logged, traced
from autologging import TRACE

#Global variables...
this_module = sys.modules[__name__]
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s')
console_handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
file_handler = logging.FileHandler('maple_cli.log', mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info('Starting new maple_cli session...')

run_results = {}

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return(v)

class MyParser(argparse.ArgumentParser):

    def print_help(self, file=None):
        if file is None:
            file = sys.stdout
        self._print_message(self.format_help(), file)
        if len(sys.argv) >= 3:
            if sys.argv[2] == 'fmc':
                self.show_fmc_leaf_help()
            elif sys.argv[2] == 'amp':
                self.show_amp_leaf_help()
            elif sys.argv[2] == 'threatgrid':
                self.show_tg_leaf_help()
            else:
                print('leaf type %s not found...' % sys.argv[2])
                print('\tcurrent leaf types = fmc, amp, threatgrid')
                sys.exit()
        else:
            self.show_all_leafs()

    def show_all_leafs(self):
        self.show_fmc_leaf_help()
        self.show_amp_leaf_help()
        self.show_tg_leaf_help()

    def show_fmc_leaf_help(self):
        import maple.fmc.fmc
        print('FMC Leaf operations supported in this release...')
        print('================================================')
        self.show_rest_base_help()
        for name, cls in maple.fmc.fmc.FMC.__dict__.items():
            if not name.startswith('_'):
                print(name)
                print('\t',end='')
                print(cls.__doc__)

    def show_amp_leaf_help(self):
        import maple.amp.amp
        print('AMP Leaf operations supported in this release...')
        print('================================================')
        self.show_rest_base_help()
        for name, cls in maple.amp.amp.AMP.__dict__.items():
            if not name.startswith('_'):
                print(name)
                print('\t',end='')
                print(cls.__doc__)

    def show_tg_leaf_help(self):
        import maple.threatgrid.threatgrid
        print('AMP Leaf operations supported in this release...')
        print('================================================')
        self.show_rest_base_help()
        for name, cls in maple.threatgrid.threatgrid.TG.__dict__.items():
            if not name.startswith('_'):
                print(name)
                print('\t',end='')
                print(cls.__doc__)

    def show_rest_base_help(self):
        import maple.rest_base
        for name, cls in maple.rest_base.RestBase.__dict__.items():
            if not name.startswith('_') and not name.startswith('or'):
                print(name)
                print('\t',end='')
                print(cls.__doc__)


maple_description = __doc__

arg_parser = MyParser(description=maple_description,
                      fromfile_prefix_chars='@',
                      epilog='Note: to pass in arguments from a file, proceed the filename with the "@" symbol')

arg_parser.add_argument('-rest_admin_user', '-rau', default='rest_admin',
                        metavar='The REST admin user name configured in FMC',
                        help='the username of the REST admin user configured in FMC')

arg_parser.add_argument('-rest_admin_password', '-rap', default='C1sc0123',
                        metavar='The REST admin user password configured in FMC',
                        help='the password of the REST admin user configured in FMC')

arg_parser.add_argument('-operations_config_file', '-ocf', type=validate_file_exists, required=True,
                        metavar='The full path to the operations configuration file',
                        help='the full path to the operations configuration file used to execute maple scripts')

arg_parser.add_argument('-maple_working_dir', '-mwd', type=validate_dir_exists, required=True,
                        metavar='The full path to the working directory for maple',
                        help=('the full path to the working directory for maple used to store logs and other '
                              'operational files')
                        )

# Gather the input arguments
username = arg_parser.parse_args().rest_admin_user
password = arg_parser.parse_args().rest_admin_password
operations_config_file = arg_parser.parse_args().operations_config_file

arg_dict = vars(arg_parser.parse_args())

# Read the operations config
operations_config = configparser.RawConfigParser(strict=False)
operations_config.optionxform = lambda option: option
operations_config.read(operations_config_file, encoding='utf-8')

def get_kwargs(kwargs_definition):
    logger.info('Processing kwargs %s' % str(kwargs_definition))
    kwargs = {}
    kwarg_pairs = kwargs_definition.split(',')
    for kwarg_pair in kwarg_pairs:
        key = kwarg_pair.split('=', 1)[0]
        val = kwarg_pair.split('=', 1)[1]
        if val.startswith('@'):
            logger.info('Processing parameter substitution with key %s and val %s' % (str(key), str(val)))
            try:
                val = arg_dict[val.replace('@', '')]
            except KeyError:
                logger.error('Key error processing key %s with val %s' % (key, val))
                sys.exit()
        elif '{' in val:
            logger.info('Processing key substitution with key %s and val %s' % (str(key), str(val)))
            place_holders = re.findall(r'(\{([^}]+)\})',val)
            for place_holder in place_holders:
                section = place_holder[1].split('$')[0]
                item = place_holder[1].split('$')[1]
                value = working_config[section][item]
                val = value
        else:
            val = str2bool(val)
        kwargs[key] = val
    return kwargs

def process_RUN(config_dict,key,val):
    logger.info('Processing a RUN dict %s with key %s and val %s' % (config_dict, key, val))
    results_var = key.split(' ')[1]
    operation_definition = val
    callable = re.match(r'^([^(]+)\(', operation_definition).group(1)
    method = None
    if '.' in callable:
        class_name, method_name = callable.split('.')
        if '{' in class_name:
            place_holder = re.match(r'\{([^}]+)\}',class_name).group(1)
            section = place_holder.split('$')[0]
            item = place_holder.split('$')[1]
            _class = working_config[section][item]
        else:
            _class = getattr(this_module,class_name)
        method = getattr(_class,method_name)
    else:
        method = getattr(this_module,callable)
    kwargs = {}
    kwargs_definition = re.match(r'^\((.*)\)$',operation_definition.replace(callable,'')).group(1)
    if len(kwargs_definition) >= 1:
        kwargs = get_kwargs(kwargs_definition)
        config_dict[key] = method(**kwargs)
    else:
        config_dict[key] = method()

def process_place_holders(config_dict,key,val):
    logger.info('Processing config_dict %s with key %s and val %s' % (config_dict, key, val))
    place_holders = re.findall(r'(\{([^}]+)\})',val)
    for place_holder in place_holders:
        logger.info('Processing place holder %s' % str(place_holder))
        section = place_holder[1].split('$')[0]
        item = place_holder[1].split('$')[1]
        value = working_config[section][item]
        if type(value) is str:
            val = val.replace(place_holder[0],value)
        config_dict[key] = val
    if key.startswith('RUN '):
        logger.info('RUN detected, sending to process_RUN...')
        process_RUN(config_dict,key,val)

def recurse_config(config_dict):
    for key, val in config_dict.items():
        logger.info('Recursing with key %s and val %s' % (str(key), str(val)))
        if type(val) is collections.OrderedDict:
            recurse_config(val)
        if type(val) is str:
            process_place_holders(config_dict,key,val)

working_config = operations_config._sections.copy()
recurse_config(working_config)
