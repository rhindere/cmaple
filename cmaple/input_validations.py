#!/usr/bin/env python
"""
Created on May 20, 2018

@author: rhindere@cisco.com

input_validations.py implements various helper functions for input
validation.

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

import ipaddress
import argparse
import os
import re
import socket
import logging
from autologging import logged, traced
from autologging import TRACE

logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))

@logged(logger)
@traced(logger)
def validate_ip_host(ip_host):
    """Validates the value for ip_host.

    """

    try:
        ipaddress.ip_address(ip_host)
    except:
        try:
            socket.gethostbyname(ip_host)
        except:
            raise ValueError('The value provided for the api host "%s" does not appear to be a valid IP address or does not DNS resolve...' % (ip_host))
    return ip_host


@logged(logger)
@traced(logger)
def validate_file_open_for_read(file):
    """Validates the value for file.

    """

    try:
        file = open(file, 'r')
    except IOError:
        msg = "%r is not a valid file path or the file is open in another application" % file
        raise argparse.ArgumentTypeError(msg)
    return file


@logged(logger)
@traced(logger)
def validate_file_exists(file):
    """Validates the file 'file' exists.

    """

    if not os.path.isfile(file):
        raise argparse.ArgumentTypeError(file,'does not reference an existing file...')
    else:
        return file


@logged(logger)
@traced(logger)
def validate_dir_exists(dir):
    """Validates the directory 'dir' exists.

    """

    if not os.path.isdir(dir):
        raise argparse.ArgumentTypeError(dir, 'does not reference an existing directory...')
    else:
        return dir


@logged(logger)
@traced(logger)
def validate_file_open_for_overwrite(file):
    """Validates the file 'file' can be opened for write operations.

    """

    try:
        file = open(file, 'w')
    except IOError:
        msg = "%r is not a valid file path or the file is open in another application" % file
        raise argparse.ArgumentTypeError(msg)
    return file


@logged(logger)
@traced(logger)
def validate_logging_level(level):
    """Validates the logging level 'level' is supported.

    """

    levels = [
                'CRITICAL',
                'ERROR',
                'WARNING',
                'INFO',
                'DEBUG',
                'NOTSET'
             ]
    if not level in levels:
        raise argparse.ArgumentTypeError('Logging level must be one of: CRITICAl, ERROR, WARNING, INFO or DEBUG.')
    else:
        return level


@logged(logger)
@traced(logger)
def str2bool(v):
    """Converts a text value 'v' to a Python boolean value.

    """

    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


@logged(logger)
@traced(logger)
def isIP_v4(address):

    """Validates 'address' is a valid IPv4 address.

    """

    if address == '': return address
    try:
        socket.inet_aton(address)
    except socket.error:
        msg = "%r is not a valid IP address" % address
        raise argparse.ArgumentTypeError(msg)
    return address


@logged(logger)
@traced(logger)
def validate_string_value(string_value,description):
    """Validates 'string_value' is a string type.

    """

    if string_value is None:
        logger.error('A value must be provided for the %s' % (description))
        raise ValueError()
    elif not isinstance(string_value,str):
        logger.error('A string value must be provided for the %s, provided value is of type %s...' % (description,type(string_value)))
        raise ValueError()
    return string_value
