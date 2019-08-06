'''
Created on Apr 30, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''
from pprint import pprint
from collections import OrderedDict
from os.path import isfile, join
from copy import deepcopy
from cmaple.winapps.win_xml_base import WinXMLBase
import cmaple.tree_helpers as tree_helpers
import cmaple.winapps.xml_mmap.xml_mmap_helpers as xml_mmap_helpers
import re
import sys
from os import urandom
from base64 import b64encode
import logging
from autologging import logged, traced
from autologging import TRACE
from inspect import isclass

# Define global variables...
path_delimiter = '->'

# Create a logger tree.fmc...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))


@logged(logger)
@traced(logger)
class MindManagerXMLApp(object):

    def __init__(self, **kwargs):
        kwarg_defaults = {'verify': False, 'cmd_retries': 5, 'backoff_timer': 30,
                          'persist_responses': True, 'restore_responses': False, 'leaf_dir': None}

        for key, val in kwargs.items():
            kwarg_defaults[key] = val

        self.__dict__.update(kwarg_defaults)

        self.mmaps = {}

    def add_mmap(self, mmap_file_path, mmap_name):
        mmap = MindManagerXMLMap(self, mmap_file_path, mmap_name)
        self.mmaps[mmap_name] = mmap
        return mmap


@logged(logger)
@traced(logger)
class MindManagerXMLMap(WinXMLBase):
    
    def __init__(self, app, mmap_file_path, mmap_name, path_delimiter='->'):
        super(MindManagerXMLMap, self).__init__()
        self.app = app
        self.mmap_file_path = mmap_file_path
        self.name = mmap_name
        self.topic_name_path = self.name
        self.path_delimiter = path_delimiter
        self.get_mmap()
        self.topic_name_index = {}
        self.topic_path_index = {}
        self.topic_name_path_index = {}
        self.reversed_topic_name_path_index = {}
        self.sub_topics = []
        self.sub_topic_oids = {}
        self.central_topic = MindManagerCentralTopic(self)
        xml_mmap_helpers.load_topics(self.central_topic, self)
        self.relationships_topic = MindManagerRelationships(self)
        self.relationship_reference_index = {}
        self.relationship_oid_index = {}
        xml_mmap_helpers.load_relationships(self)
        # self.load_topics()
        self.jsonpath_topics = \
            tree_helpers.get_jsonpath_full_paths_and_values('"ap:Map".[0]."ap:OneTopic".."ap:Topic"',
                                                            self.xml_dict)

    def get_mmap(self):
        if not self.app:
            return None
        mmap_path = join(self.mmap_file_path, self.name)
        if isfile(mmap_path):
            self.load_xml_from_file(mmap_path)
        else:
            return None
    
    def write_mmap(self, mmap_file_path=None, mmap_name=None):
        if mmap_file_path is None:
            mmap_file_path = self.mmap_file_path
        if mmap_name is None:
            mmap_name = self.mmap_name
        mmap_path = join(mmap_file_path, mmap_name)
        self.write_xml_to_file(mmap_path)

    def add_topic(self, mmap, parent_topic, xml_topic, xml_topic_path, topic_name):

        new_topic = MindManagerTopic(mmap, parent_topic, xml_topic, xml_topic_path, topic_name)

        return new_topic


@logged(logger)
@traced(logger)
class MindManagerRelationship(object):

    def __init__(self, mmap, xml_topic, xml_topic_path):
        self.mmap = mmap
        self.xml_topic = xml_topic
        self.xml_topic_path = xml_topic_path
        self.oid = xml_topic['@OId']
        self.connection_0_oid = \
            xml_topic['ap:ConnectionGroup'][0]['ap:Connection'][0]['ap:ObjectReference'][0]['@OIdRef']
        self.connection_1_oid = \
            xml_topic['ap:ConnectionGroup'][1]['ap:Connection'][0]['ap:ObjectReference'][0]['@OIdRef']
        if self.connection_0_oid not in self.mmap.relationship_reference_index:
            self.mmap.relationship_reference_index[self.connection_0_oid] = []
        self.mmap.relationship_reference_index[self.connection_0_oid].append(self)
        if self.connection_1_oid not in self.mmap.relationship_reference_index:
            self.mmap.relationship_reference_index[self.connection_1_oid] = []
        self.mmap.relationship_reference_index[self.connection_1_oid].append(self)

    def clone_self(self, new_connection_0_oid, new_connection_1_oid):

        new_xml_topic = deepcopy(self.xml_topic)
        xml_mmap_helpers.refresh_all_oids(new_xml_topic)
        if new_connection_0_oid is not None:
            new_xml_topic['ap:ConnectionGroup'][0]['ap:Connection'][0]['ap:ObjectReference'][0]['@OIdRef'] = \
                new_connection_0_oid
        if new_connection_1_oid is not None:
            new_xml_topic['ap:ConnectionGroup'][1]['ap:Connection'][0]['ap:ObjectReference'][0]['@OIdRef'] = \
                new_connection_1_oid
        new_relationship_position = len(self.mmap.relationships_topic.xml_topic['ap:Relationship'])
        new_relationship_xml_path = re.sub(r'\[[0-9]+\]$',
                                           '[' + str(new_relationship_position) + ']',
                                           self.xml_topic_path
                                           )

        self.mmap.relationships_topic.xml_topic['ap:Relationship'].append(new_xml_topic)
        new_relationship = \
            MindManagerRelationship(self.mmap,
                                    self.mmap.relationships_topic.xml_topic['ap:Relationship'][-1],
                                    new_relationship_xml_path
                                    )
        self.mmap.relationships_topic.relationships.append(new_relationship)


@logged(logger)
@traced(logger)
class MindManagerRelationships(object):

    def __init__(self, mmap):
        self.mmap = mmap
        self.jsonpath_xml_relationships = \
            tree_helpers.get_jsonpath_full_paths_and_values('"ap:Map".[0]."ap:Relationships".[0]',
                                                            self.mmap.xml_dict
                                                            )
        if not self.jsonpath_xml_relationships:
            self.relationships = None
        else:
            self.xml_topic = self.jsonpath_xml_relationships[0][1]
            self.xml_topic_path = self.jsonpath_xml_relationships[0][0]
            self.relationships = []

    def load_relationship(self, child_dict, child_path):

        new_relationship = MindManagerRelationship(self.mmap, child_dict, child_path)
        self.relationships.append(new_relationship)


@logged(logger)
@traced(logger)
class MindManagerTopic:
    
    def __init__(self, mmap, parent_topic, xml_topic, xml_topic_path, topic_name):
        self.mmap = mmap
        self.xml_topic = xml_topic
        self.xml_topic_path = xml_topic_path
        self.name = topic_name
        self.oid = self.xml_topic['@OId']
        self.notes_text = None
        self.sub_topics = []
        self.sub_topic_oids = {}
        self.topic_name_index = {}
        self.topic_path_index = {}
        self.topic_name_path_index = {}
        self.reversed_topic_name_path_index = {}
        if parent_topic is None:
            parent_path_parts = self.xml_topic_path.split('.ap:Topic')[:-2]
            parent_path = ('.ap:Topic').join(parent_path_parts) + '.ap:Topic.[0]'
            self.parent_topic = mmap.topic_path_index[parent_path]
        else:
            self.parent_topic = parent_topic
        self.parent_topic.sub_topics.append(self)
        self.parent_topic.sub_topic_oids[self.oid] = len(self.parent_topic.sub_topics) - 1
        self.topic_name_path = self.parent_topic.topic_name_path + self.mmap.path_delimiter + self.name
        self.reversed_topic_name_path = xml_mmap_helpers.reverse_topic_name_path(self.topic_name_path,
                                                                                 self.mmap.path_delimiter)

        self.update_parent_indexes(self, self.name, self.topic_name_path, self.reversed_topic_name_path)
        if self.name not in self.mmap.topic_name_index:
            self.mmap.topic_name_index[self.name] = []
        self.mmap.topic_name_index[self.name].append(self)
        self.mmap.topic_path_index[self.xml_topic_path] = self
        self.mmap.topic_name_path_index[self.topic_name_path] = self
        self.mmap.reversed_topic_name_path_index[self.reversed_topic_name_path] = self

        # load topics
        xml_mmap_helpers.load_topics(self, self.mmap)

    def update_parent_indexes(self, topic, name, path, reverse_path):

        # add to parent indexes
        if topic.name not in self.parent_topic.topic_name_index:
            self.parent_topic.topic_name_index[topic.name] = []
        self.parent_topic.topic_name_index[topic.name].append(topic)
        self.parent_topic.topic_path_index[topic.xml_topic_path] = topic
        self.parent_topic.topic_name_path_index[topic.topic_name_path] = topic
        self.parent_topic.reversed_topic_name_path_index[topic.reversed_topic_name_path] = topic

        if not type(self.parent_topic) is MindManagerXMLMap:
            self.parent_topic.update_parent_indexes(topic, name, path, reverse_path)
            
    def clone_sub_topic_by_position(self, position):
        topic_to_clone = self.sub_topics[position]
        self.clone_to_sub_topic(topic_to_clone)

    def remove_sub_topic_by_position(self, position):
        topic_to_remove = self.sub_topics[position]
        topic_to_remove.remove_self()

    def remove_self(self):
        position = self.parent_topic.sub_topic_oids[self.oid]
        self.parent_topic.sub_topic_oids.pop(self.oid)
        self.parent_topic.sub_topics.pop(position)
        self.parent_topic.xml_topic['ap:SubTopics'][0]['ap:Topic'].pop(position)
        self.parent_topic.reset_sub_topics()

    def reset_sub_topics(self):

        self.sub_topic_oids = {}
        for i in range(0, len(self.sub_topics)):
            sub_topic_oid = self.sub_topics[i].xml_topic['@OId']
            self.sub_topic_oids[sub_topic_oid] = i

    def clone_relationships(self, relationships_to_clone):

        for key, val in relationships_to_clone.items():
            relationship = val['relationship']
            new_connection_0_oid = val['new_connection_0_oid']
            new_connection_1_oid = val['new_connection_1_oid']
            relationship.clone_self(new_connection_0_oid, new_connection_1_oid)

    def clone_to_sub_topic(self, topic_to_clone):
        topic_to_clone_name, cloned_topic_xml_topic, relationships_to_clone = \
            xml_mmap_helpers.clone_xml_dict(topic_to_clone, 'ap:Topic')
        cloned_topic_position = len(self.sub_topics)
        cloned_topic_xml_path = re.sub(r'\[[0-9]+\]$',
                                       '[' + str(cloned_topic_position) + ']',
                                       topic_to_clone.xml_topic_path)
        cloned_topic = MindManagerTopic(self.mmap,
                                        self,
                                        cloned_topic_xml_topic,
                                        cloned_topic_xml_path,
                                        topic_to_clone_name)

        self.xml_topic['ap:SubTopics'][0]['ap:Topic'].append(cloned_topic_xml_topic)

        # Check to see if cloned topic is in this map, if not, don't try to clone relationships
        if topic_to_clone.mmap == self.mmap:
            self.clone_relationships(relationships_to_clone)

        # xml_mmap_helpers.load_topics(self, self.mmap)

        return cloned_topic

    def clone_map_topic_by_name(self, topic_name, mmap=None):

        if mmap is None:
            mmap = self.mmap

        if topic_name in mmap.topic_name_index:
            topic_to_clone = mmap.topic_name_index[topic_name][0]
            new_topic = self.clone_to_sub_topic(topic_to_clone)
            return new_topic
        else:
            return None

    def change_topic_name(self, topic_name):
        self.name = topic_name
        self.xml_topic['ap:Text'][0]['@PlainText'] = topic_name

    def get_sub_topic(self, sub_topic_name):
        for sub_topic in self.sub_topics:
            if sub_topic.name == sub_topic_name:
                return sub_topic
        return None

    def recurse_child_topics_with_callback_to_dict(self, callback=None, names_dict=None):

        print(self.name, file=sys.stderr)
        callback_dict = callback(self)
        callback = callback_dict['callback']
        processed_name = callback_dict['processed_name']
        if not callable(callback):
            if callback is None:  # Abort the recursion
                return False
            if type(callback) is bool:
                if callback:
                    return True
                else:
                    return False
        else:
            names_dict[processed_name] = {}
            names_dict = names_dict[processed_name]

        for sub_topic in self.sub_topics:
            if not sub_topic.recurse_child_topics_with_callback_to_dict(callback, names_dict):
                return False

        return True

    def recurse_child_topics_with_callback(self, callback=None, callback_results=None):

        callback = callback(self)
        if not callable(callback):
            if callback is None:  # Abort the recursion
                return False
            if type(callback) is bool:
                if callback:
                    return True
                else:
                    return False

        for sub_topic in self.sub_topics:
            if not sub_topic.recurse_child_topics_with_callback(callback, callback_results):
                return False

        return True

    def get_reverse_path_topic(self, topic_name_path, top_topic):

        reversed_topic_name_path = xml_mmap_helpers.reverse_topic_name_path(topic_name_path, self.mmap.path_delimiter)
        for key, topic in self.reversed_topic_name_path_index.items():
            if reversed_topic_name_path in key:
                return topic
        if self.name != top_topic.name:
            return self.parent_topic.get_reverse_path_topic(topic_name_path, top_topic)
        else:
            return None

    def get_nearest_ancestor_by_path(self, topic_path):

        reversed_topic_path = xml_mmap_helpers.reverse_topic_name_path(topic_path, self.mmap.path_delimiter)
        qualified_topics = []
        for key, value in self.mmap.reversed_topic_name_path_index.items():
            if key.startswith(reversed_topic_path):
                qualified_topics.append(value)
        return self.get_nearest_ancestor_by_list(qualified_topics)

    def get_nearest_ancestor_by_name(self, topic_name):

        ancestor_topics = self.mmap.topic_name_index.get(topic_name)
        if ancestor_topics is None:
            return None

        return self.get_nearest_ancestor_by_list(ancestor_topics)

    def get_nearest_ancestor_by_list(self, ancestor_topics):

        longest_match = 0
        longest_ancestor = None
        match_found = False
        this_name_path_names = self.topic_name_path.split(self.mmap.path_delimiter)
        logger.debug('this path = %s' % self.topic_name_path)
        for ancestor_topic in ancestor_topics:
            logger.debug('ancestor path %s' % ancestor_topic.topic_name_path)
            logger.debug('ancestor topic name %s' % ancestor_topic.name)
            ancestor_match = 0
            ancestor_name_path_names = ancestor_topic.topic_name_path.split(self.mmap.path_delimiter)
            for i in range(0, len(this_name_path_names)):
                logger.debug('ancestor name path name %s this path %s' % (ancestor_name_path_names[i], this_name_path_names[i]))
                if ancestor_name_path_names[i] == this_name_path_names[i]:
                    logger.debug('match found, ancestor match index = %s' % ancestor_match)
                    ancestor_match += 1
                    match_found = True
                else:
                    logger.debug('names do not match...')
                    break
            if match_found and ancestor_match > longest_match:
                longest_match = ancestor_match
                longest_ancestor = ancestor_topic
                logger.debug('longest match index = %s' % str(longest_match))
        if match_found:
            logger.debug('longest ancestor name %s' % longest_ancestor.name)
            return longest_ancestor
        else:
            return None

    def get_nearest_descendent_by_name(self, topic_name):

        descendent_topics = self.topic_name_index.get(topic_name)
        if descendent_topics is None:
            return None
        else:
            shortest_descendent_path_len = 0
            shortest_descendent = None
            for descendent_topic in descendent_topics:
                logger.debug('descendent path %s' % descendent_topic.topic_name_path)
                logger.debug('descendent topic name %s' % descendent_topic.name)
                this_descendent_path_len = len(descendent_topic.topic_name_path.split(self.mmap.path_delimiter))
                if shortest_descendent_path_len == 0:
                    shortest_descendent_path_len = this_descendent_path_len
                    shortest_descendent = descendent_topic
                else:
                    if this_descendent_path_len < shortest_descendent_path_len:
                        shortest_descendent_path_len = this_descendent_path_len
                        shortest_descendent = descendent_topic
            return shortest_descendent

@logged(logger)
@traced(logger)
class MindManagerCentralTopic(MindManagerTopic):

    def __init__(self, mmap):
        self.mmap = mmap
        self.jsonpath_xml_central_topic = \
            tree_helpers.get_jsonpath_full_paths_and_values('"ap:Map".[0]."ap:OneTopic".[0]."ap:Topic".[0]',
                                                            self.mmap.xml_dict
                                                            )
        self.xml_central_topic = self.jsonpath_xml_central_topic[0][1]
        super().__init__(self.mmap,
                         self.mmap,
                         self.xml_central_topic,
                         self.jsonpath_xml_central_topic[0][0],
                         self.xml_central_topic['ap:Text'][0]['@PlainText']
                         )

    def add_balanced_sub_topic(self, topic_name):
        w32_topic = self.w32_central_topic.AddBalancedSubTopic(topic_name)
        self.sub_topics.append(MindManagerTopic(self, w32_topic, topic_name))
        return self.sub_topics[-1]

