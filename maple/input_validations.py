'''
Created on Jun 3, 2018

@author: ronhi
'''

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
    
    try:
        ipaddress.ip_address(ip_host)
    except:
        try:
            socket.gethostbyname(ip_host)
        except:
            raise ValueError('The value provided for the api host "%s" does not appear to be a valid IP address or does not DNS resolve...' % (ip_host))
    return ip_host

def validate_file_open_for_read(file):
    try:
        file = open(file, 'r')
    except IOError:
        msg = "%r is not a valid file path or the file is open in another application" % file
        raise argparse.ArgumentTypeError(msg)
    return file

def validate_file_exists(file):
    
    if not os.path.isfile(file):
        raise argparse.ArgumentTypeError(file,'does not reference an existing file...')
    else:
        return file


def validate_dir_exists(dir):
    if not os.path.isdir(dir):
        raise argparse.ArgumentTypeError(dir, 'does not reference an existing directory...')
    else:
        return dir

def validate_file_open_for_overwrite(file):
    try:
        file = open(file, 'w')
    except IOError:
        msg = "%r is not a valid file path or the file is open in another application" % file
        raise argparse.ArgumentTypeError(msg)
    return file

def validate_logging_level(level):
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

def validate_leaf_type(leaf):
    leafs = [
                'fmc',
#                 'asa',
#                 'ise',
#                 'pxGrid',
#                 'tetration',
            ]
    if not leaf in leafs:
        raise argparse.ArgumentTypeError('Leaf type must be one of: fmc, asa, ise, pxGrid or tetration (only "fmc" is currently implemented).')
    else:
        return leaf

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def isIP_v4(address):
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
    
    if string_value is None:
        logger.error('A value must be provided for the %s' % (description))
        raise ValueError()
    elif not isinstance(string_value,str):
        logger.error('A string value must be provided for the %s, provided value is of type %s...' % (description,type(string_value)))
        raise ValueError()
    return string_value
        
