'''
Created on Mar 18, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''

from maple.tree import MapleTree
from pprint import pprint
import re, sys
import _pickle

amp_query = sys.argv[1]
tg_query = sys.argv[2]

maple_tree = MapleTree(logging_level='INFO')
TG_leaf = maple_tree.add_leaf_instance('tg',name='Hackathon_TG',
                                          TG_host='panacea.threatgrid.com',TG_API_key='6g2r13gl2t5g6moef3m24ubajq',default_get_item_limit=200)
AMP_leaf = maple_tree.add_leaf_instance('amp',name='Hackathon',
                                          AMP_host='api.amp.cisco.com',AMP_API_client_ID='b73313ad271b882c8118',AMP_API_key='4fd9e8c8-b1bc-4d63-ac8e-300c24f158d0',default_get_item_limit=200)

#AMP_leaf.GET_API_path('v1/computers')
#AMP_leaf.walk_API_path_gets('v1/computers')
#AMP_leaf.walk_API_resource_gets()


TG_leaf.GET_API_path('api/v2/iocs/feeds/ips?api_key=6g2r13gl2t5g6moef3m24ubajq&after=2018-09-18T13:00:00')



amp_response_dict = _pickle.load(open('amp_responses_dict.pickle','rb'))
pprint(amp_response_dict)
sys.exit()
#TG_leaf.GET_API_path('api/v2/samples/search?api_key=6g2r13gl2t5g6moef3m24ubajq&checksum=b447b22d10787bfbe974084562bfd656a81f9243a0311b3215846c6deaaf535d')
TG_leaf.GET_API_path('api/v2/iocs/feeds/ips?api_key=6g2r13gl2t5g6moef3m24ubajq&after=2018-09-18T13:00:00')
#TG_leaf.walk_API_path_gets('v1/computers')
#TG_leaf.walk_API_resource_gets()
pprint(TG_leaf.responses_dict)
pickle_file = open('responses_dict.pickle','wb')
_pickle.dump(TG_leaf.responses_dict,pickle_file)
pickle_file.close()

