'''
Created on Mar 18, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''

from maple.tree import MapleTree
from pprint import pprint

maple_tree = MapleTree(logging_level='INFO', name='amp_test', tree_dir=r'C:\Users\rhindere\Documents\maple_working_dir')
model_json_file=r'C:\Users\rhindere\Documents\PycharmProjects\maple_project\maple\fmc\api-docs-fmcwithll.json'
FMC_leaf = maple_tree.add_leaf_instance('fmc',name='10.1.101.39_Global',
                                        json_file_path=model_json_file,
                                          FMC_host='10.1.101.39',FMC_username='rest_admin',FMC_password='C1sc0123',default_get_item_limit=200)
FMC_leaf.walk_API_resource_gets(include_filter_regex=r'/object')
pprint(FMC_leaf.responses_dict)
