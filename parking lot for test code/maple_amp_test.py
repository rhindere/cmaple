'''
Created on Mar 18, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''

from maple.tree import MapleTree
from pprint import pprint
import re, sys
import _pickle

maple_tree = MapleTree(logging_level='INFO')
AMP_leaf = maple_tree.add_leaf_instance('amp',name='Hackathon',
                                          AMP_host='api.amp.cisco.com',AMP_API_client_ID='b73313ad271b882c8118',AMP_API_key='4fd9e8c8-b1bc-4d63-ac8e-300c24f158d0',default_get_item_limit=200)

#AMP_leaf.GET_API_path('v1/computers')
AMP_leaf.walk_API_path_gets('v1/computers')
# AMP_leaf.walk_API_resource_gets()
pprint(AMP_leaf.responses_dict)
# pickle_file = open('amp_responses_dict.pickle','wb')
# _pickle.dump(AMP_leaf.responses_dict,pickle_file)
# pickle_file.close()

