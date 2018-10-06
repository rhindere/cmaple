'''
Created on Mar 18, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''

from maple.tree import MapleTree
from pprint import pprint

maple_tree = MapleTree(logging_level='INFO', name='amp_test', tree_dir=r'C:\Users\rhindere\Documents\maple_working_dir')
model_json_file=r'C:\Users\rhindere\Documents\PycharmProjects\maple_project\maple\fmc\api-docs-fmcwithll.json'
FMC_leaf = maple_tree.add_leaf_instance('fmc',name='10.1.101.39_Global', json_file_path=model_json_file,
                                        FMC_host='10.1.101.39', FMC_username='rest_admin',FMC_password='C1sc0123',
                                        default_get_item_limit=200)

smart_ap_url = "policy/accesspolicies/$..items[@.name is 'test_migration_policy_1'].id"
ap_id = FMC_leaf.smart_get_object_id(url=smart_ap_url)
smart_rule_url = "policy/accesspolicies/%s/accessrules/$..items[@.name is 'kitchen_sink'].id" % ap_id
rule_id = FMC_leaf.smart_get_object_id(url=smart_rule_url)
rule_url = "policy/accesspolicies/%s/accessrules/%s" % (ap_id, rule_id)
rule_response = FMC_leaf.get_json_request(url=rule_url)
pprint(rule_response['json_dict'])
rule_json = rule_response['json_dict']
new_json = FMC_leaf.set_json_properties(rule_json, {'logBegin': not rule_json['logBegin']})
print('nj=')
pprint(new_json)
prep_json = FMC_leaf.prep_put_json(json_dict=new_json)
print('pj=')
pprint(prep_json)
put_response = FMC_leaf.put_json_request(url=rule_url, json_dict=prep_json)
pprint(put_response)
