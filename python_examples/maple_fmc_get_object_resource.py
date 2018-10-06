"""
Created on Mar 18, 2018

@author: Ron Hinderer - rhindere@cisco.com

maple_fmc_get_object_resource.py - simple example to demonstrate MAPLE getting a resource path by
filter.
"""

from maple.tree import MapleTree
from pprint import pprint

# Create a maple tree instance...
maple_tree = MapleTree(logging_level='INFO', name='amp_test', tree_dir=r'C:\Users\rhindere\Documents\maple_working_dir')

# Attach a maple fmc leaf instance to the tree...
model_json_file=r'C:\Users\rhindere\Documents\PycharmProjects\maple_project\maple\fmc\api-docs-fmcwithll.json'
FMC_leaf = maple_tree.add_leaf_instance('fmc',name='10.1.101.39_Global',
                                        json_file_path=model_json_file, FMC_host='10.1.101.39',
                                        FMC_username='rest_admin', FMC_password='C1sc0123',
                                        default_get_item_limit=200)

# Use the fmc leaf method walk_API_resource_gets to recursively walk the resource paths.
# Use the key parameter "include_filter_regex" with pattern r'/object' to exclude all resource paths except "object"
FMC_leaf.walk_API_resource_gets(include_filter_regex=r'/object')
pprint(FMC_leaf.responses_dict)
