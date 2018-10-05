'''
Created on May 22, 2018

@author: ronhi
'''

import re,sys
from pprint import pprint
from collections import OrderedDict


def recurse_map_dict_OrderedDict(map_dict,tab_string):
    for key, val in map_dict.items():
        print(tab_string+key)
        if type(val) is OrderedDict:
            recurse_map_dict_OrderedDict(val,tab_string+'\t')
        else:
            print(tab_string+'\t'+str(val))
        
def create_outline(_dict,tab_string):

    def process_val(val,tab_string):
        if type(val) is dict:
            process_dict(val,tab_string)
        elif type(val) is list:
            process_list(val,tab_string)
        else:
            print(tab_string+str(val))

    def process_list(_list,tab_string):
        print(tab_string+'list')
        for val in _list:
            process_val(val,tab_string+'\t')

    def process_dict(_dict,tab_string):
        for key, val in _dict.items():
            print(tab_string+key)
            process_val(val,tab_string+'\t')

    process_val(_dict,tab_string)
        
def create_mindmap(_dict,tab_string):

    def process_val(val,tab_string):
        if type(val) is dict:
            process_dict(val,tab_string)
        elif type(val) is list:
            process_list(val,tab_string)
        else:
            print(tab_string+str(val))

    def process_list(_list,tab_string):
        print(tab_string+'list')
        for val in _list:
            process_val(val,tab_string+'\t')

    def process_dict(_dict,tab_string):
        for key, val in _dict.items():
            print(tab_string+key)
            process_val(val,tab_string+'\t')

    process_val(_dict,tab_string)
        
# flatfile = open(sys.argv[1],'rb').read()
flatfile = open(sys.argv[1],'r').read()
model_dict = eval(flatfile)
create_outline(model_dict,'')

sys.exit()

pprint(flatfile)
for line in flatfile:
    print(line,end='')

sys.exit()

flatfile = flatfile.decode('utf-16')
flatfile = flatfile.splitlines()

map_dict = OrderedDict()

flatfile_record = ''
for flatfile_line in flatfile:
    flatfile_record_match = re.match(r"^(\s{1}|\{{1})'",flatfile_line)
    if flatfile_record_match:
        if not flatfile_record == '':
            flatfile_record = re.sub(r',$','',flatfile_record)
            if not flatfile_record.startswith('{'):
                flatfile_record = '{' + flatfile_record
            if not flatfile_record.endswith('}}'):
                flatfile_record = flatfile_record + '}'
            flatfile_dict = eval(flatfile_record)
            for key,val in flatfile_dict.items():
                map_pointer = map_dict
                if 'json_dict' in val:
                    json_dict = val['json_dict']
                    if json_dict is None:
                        break
                    if 'links' in json_dict:
                        if not 'self' in json_dict['links']:
                            break
                        link = json_dict['links']['self']
                        link = link.replace('https://10.1.101.39/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/','')
                        link = link.split('/')
                        link.pop()
                        for link_part in link:
                            if not link_part in map_pointer:
                                map_pointer[link_part] = OrderedDict()
                            map_pointer = map_pointer[link_part]
                        json_dict.pop('links')
                    if not 'name' in map_pointer:
                        map_pointer['name'] = OrderedDict()
                    map_pointer = map_pointer['name']
                    if 'name' in json_dict:
                        map_pointer[json_dict['name']] = OrderedDict()
                        map_pointer = map_pointer[json_dict['name']]
                        json_dict.pop('name')
                    if 'id' in json_dict:
                        map_pointer['id'] = json_dict['id']
                        json_dict.pop('id')
                    if 'type' in json_dict:
                        map_pointer['type'] = json_dict['type']
                        json_dict.pop('type')
                    map_pointer['associated_objects'] = OrderedDict()
                    map_pointer = map_pointer['associated_objects']
                    for jkey, jval in json_dict.items():
                        ao_pointer = map_pointer
                        ao_pointer[jkey] = OrderedDict()
                        ao_pointer = ao_pointer[jkey]
                        def store_aos(ao_dict,ao_pointer):
                            for ao_key, ao_val in ao_dict.items():
                                if ao_key == 'response_url':
                                    ao_val = ao_val.replace('https://10.1.101.39/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/','')
                                ao_pointer['member->'+ao_key] = '=' + str(ao_val)
                            ao_pointer['ao_complete'] = ''
                        if type(jval) is dict:
                            ao_pointer['members'] = OrderedDict()
                            member_pointer = ao_pointer['members']
                            member_pointer['1'] = OrderedDict()
                            store_aos(jval,member_pointer['1'])
                        elif type(jval) is list:
                            ao_pointer['members'] = OrderedDict()
                            member_pointer = ao_pointer['members']
                            member_counter = 1
                            for ao in jval:
                                member_pointer[str(member_counter)] = OrderedDict()
                                ao_dict =  member_pointer[str(member_counter)]
                                store_aos(ao,ao_dict)
                                member_counter += 1
                        else:
                            ao_pointer['members'] = OrderedDict()
                            member_pointer = ao_pointer['members']
                            member_pointer['1'] = OrderedDict()
                            member_pointer['1']['member->value'] = jval
                            member_pointer['1']['ao_complete'] = ''

                                    
            flatfile_record = ''
        flatfile_record = flatfile_line
    else:
        flatfile_record += flatfile_line

#pprint(map_dict)
# sys.exit()
recurse_map_dict_OrderedDict(map_dict,'')

headers = ['object','name','id','type','associated_objects','members','member->value','member->count','member->name','member->id','member->type','member->response_url','member->metadata']

record_template = {}
for header in headers:
    record_template[header] = ''
for header in headers:
    print(header+'~',end='')
print()
    
def recurse_map_dict_csv(map_dict,record,current_header):
    this_record = record.copy()
    save_header = current_header
    for key, val in map_dict.items():
        if key == 'items':
            return
        if key == 'ao_complete':
            for header in headers:
                print(this_record[header].strip()+'~',end='')
            print()
            return
        if key in this_record:
            current_header = key
        else:
            this_record[current_header] = key
        if type(val) is OrderedDict:
            recurse_map_dict_csv(val,this_record,current_header)
            current_header = save_header
        else:
            this_record[current_header] += str(val)
     
    
recurse_map_dict_csv(map_dict,record_template,'')
