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

import sys
import cmaple.tree_helpers as tree_helpers
import logging
from collections import OrderedDict
from autologging import logged, traced
from autologging import TRACE
from pprint import pformat,pprint
import time
import re
from os import urandom
from base64 import b64encode
from copy import deepcopy
from time import time, sleep
# Create a logger for this module...
logger = logging.getLogger(re.sub('\.[^.]+$', '', __name__))


@logged(logger)
@traced(logger)
def get_first_topic_name_path_topic(xml_topic, top_topic, topic_name_path):

    topic_name_path_reverse = reverse_topic_name_path(topic_name_path)

    for path, topic in xml_topic.topic_name_path_index.items():
        if topic_name_path_reverse in path:
            return topic

    if xml_topic.parent_topic.xml_topic_path == top_topic.xml_topic_path:
        return None
    else:
        return get_first_topic_name_path_topic(xml_topic.parent_topic, top_topic, topic_name_path)


@logged(logger)
@traced(logger)
def reverse_topic_name_path(topic_name_path, path_delimiter):

    topic_name_path_split = topic_name_path.split(path_delimiter)

    return path_delimiter.join(topic_name_path_split[::-1])


@logged(logger)
@traced(logger)
def build_mmap_from_xml(xml_topic):

    old_oid = xml_topic['@OId']
    new_oid = b64encode(urandom(16)).decode('utf-8')
    xml_topic['@OId'] = new_oid
    return old_oid, new_oid


@logged(logger)
@traced(logger)
def refresh_oid(xml_topic):

    old_oid = xml_topic['@OId']
    new_oid = b64encode(urandom(16)).decode('utf-8')
    xml_topic['@OId'] = new_oid
    return old_oid, new_oid


@logged(logger)
@traced(logger)
def refresh_all_oids(xml_topic):

    def replace_oid(xml_dict, xml_path):
        old_oid, new_oid = refresh_oid(xml_dict)

    recurse_topics(xml_topic, '', '@OId', replace_oid)

@logged(logger)
@traced(logger)
def clone_xml_dict(topic_to_clone, path_key):

    def check_relationships(old_oid, new_oid):
        if old_oid in mmap.relationship_reference_index:
            for relationship in mmap.relationship_reference_index[old_oid]:
                if relationship.oid not in relationships_to_clone:
                    relationships_to_clone[relationship.oid] = {'relationship': relationship,
                                                                'new_connection_0_oid': None,
                                                                'new_connection_1_oid': None,
                                                                }
                if old_oid == relationship.connection_0_oid:
                    relationships_to_clone[relationship.oid]['new_connection_0_oid'] = new_oid
                elif old_oid == relationship.connection_1_oid:
                    relationships_to_clone[relationship.oid]['new_connection_1_oid'] = new_oid

    relationships_to_clone = {}
    mmap = topic_to_clone.mmap

    topic_to_clone_name = topic_to_clone.name
    topic_to_clone_xml_topic = topic_to_clone.xml_topic
    cloned_topic_xml_topic = deepcopy(topic_to_clone_xml_topic)
    old_oid, new_oid = refresh_oid(cloned_topic_xml_topic)
    check_relationships(old_oid, new_oid)

    cloned_topic_jsonpath_sub_topics = \
        tree_helpers.get_jsonpath_full_paths_and_values('$.."' + path_key + '".[*]', cloned_topic_xml_topic)
    for cloned_topic_jsonpath_sub_topic in cloned_topic_jsonpath_sub_topics:
        old_oid, new_oid = refresh_oid(cloned_topic_jsonpath_sub_topic[1])
        check_relationships(old_oid, new_oid)
    return topic_to_clone_name, cloned_topic_xml_topic, relationships_to_clone


@logged(logger)
@traced(logger)
def recurse_topics(xml_dict, xml_path, callback_key, callback_function, **kwargs):
    # sleep(.01)
    # _time = time()
    # print('entering recurse_topics at time', _time)
    #
    # print(xml_path, file=sys.stderr)
    # print(xml_path)

    for key in list(xml_dict.keys()):
        this_path = xml_path + '.' + key
        # print('this path = ', this_path)
        dict_val = xml_dict[key]
        # print(type(dict_val))
        if type(dict_val) is list:
            # print('dict_val is list', dict_val)
            for i in range(0, len(dict_val)):
                child_dict = dict_val[i]
                child_path = this_path + '.' + '[' + str(i) + ']'
                # print('child_path =', child_path)
                if key == callback_key:
                    callback_function(child_dict, child_path, **kwargs)
                else:
                    recurse_topics(child_dict, child_path, callback_key, callback_function, **kwargs)
                # print('returned from recurse with key', key)
        elif type(dict_val) is str:
            # print('dict_val is str', dict_val)
            if key == callback_key:
                callback_function(xml_dict, this_path, **kwargs)

    # print('exiting recurse_topics at time', _time)


@logged(logger)
@traced(logger)
def build_topic_from_xml(child_dict,
                         child_path,
                         mmap=None,
                         parent_topic=None
                         ):
    # print('entering build_topic_from_xml at time', time(), file=sys.stderr)
    if 'ap:Text' in child_dict:
        topic_name = child_dict['ap:Text'][0]['@PlainText']
    else:
        topic_name = 'null'
    if parent_topic is not None:
        if child_dict['@OId'] in parent_topic.sub_topic_oids:
            return
    new_topic = mmap.add_topic(mmap, parent_topic, child_dict, child_path, topic_name)
    # print('exiting build_topic_from_xml at time', time(), file=sys.stderr)


@logged(logger)
@traced(logger)
def load_topics(xml_topic, mmap):

    recurse_topics(xml_topic.xml_topic,
                   xml_topic.xml_topic_path,
                   'ap:Topic',
                   build_topic_from_xml,
                   mmap=mmap,
                   parent_topic=xml_topic
                   )


@logged(logger)
@traced(logger)
def build_relationship_from_xml(child_dict,
                                child_path,
                                mmap=None,
                                ):

    mmap.relationships_topic.load_relationship(child_dict, child_path)


@logged(logger)
@traced(logger)
def load_relationships(mmap):

    relationship_reference_index = {}
    relationships = {}
    if mmap.relationships_topic.relationships is not None:
        recurse_topics(mmap.relationships_topic.xml_topic,
                       mmap.relationships_topic.xml_topic_path,
                       'ap:Relationship',
                       build_relationship_from_xml,
                       mmap=mmap,
                       )

