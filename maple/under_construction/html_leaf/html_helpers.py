'''
Created on Mar 18, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''

import json
import importlib
import maple.tree_helpers as tree_helpers
#global_helpers = importlib.import_module('.tree_helpers', 'maple')
import logging
from collections import OrderedDict
from autologging import logged, traced
from autologging import TRACE
from pprint import pformat,pprint
import time
import sys
import re

# Create a logger for maple.fmc.fmc_helpers...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))


@logged(logger)
@traced(logger)
def process_json_request_wrapper(AMP_instance,recursed=False,**kwargs):
    
    # time_diff = time.time() - AMP_instance._auth_token_time
    # if time_diff > 1500: # 1500 = 25 minutes...
    #     logger.info('Refreshing authentication token...')
    #     if AMP_instance._refresh_token_count < 3:
    #         AMP_instance._refresh_token_count += 1
    #     else:
    #         logger.info('Token has been refreshed the maximum of 3 times, requesting new token...')
    #         AMP_instance._refresh_token_count = 0
    #         AMP_instance._auth_headers.pop('X-auth-access-token')
    #         AMP_instance._auth_headers.pop('X-auth-refresh-token')
    #     FMC_instance._get_token_and_domains()
        
    if not recursed:
        
        for i in range(1,AMP_instance._rpm_retries):
            response_dict, status, include_filtered, exclude_filtered, cache_hit = process_json_request_wrapper(AMP_instance,recursed=True,**kwargs)
            if response_dict['status_code'] == 429 and not exclude_filtered:
                # Pop the url from the responses_dict so we don't trigger a cache hit on the next request...
                AMP_instance.responses_dict.pop(kwargs['url'])
                if i == (AMP_instance._rpm_retries-1):
                    logger.error('Requests per minute code 429 retry count exceeded.  Exiting...')
                    sys.exit()
                logger.info('AMP reports requests per minute exceeding 120.  Sleeping for FMC_instance._backoff_timer seconds...')
                time.sleep(AMP_instance._backoff_timer)
            else:
                return response_dict, status, include_filtered, exclude_filtered, cache_hit
    else:
        return tree_helpers.process_json_request(**kwargs)

@logged(logger)
@traced(logger)
def get_all_reference_dicts(FMC_instance):

    def add_paths_to_dict(path_parts,paths_dict,API_path_keywords_list):
        if path_parts:
            path_part = path_parts.pop(0)
            if not path_part in paths_dict:
                paths_dict[path_part] = {}
                if not path_part in API_path_keywords_list and not path_part.startswith('{'):
                    API_path_keywords_list.append(path_part)
            paths_dict = OrderedDict(sorted(paths_dict.items()))
            add_paths_to_dict(path_parts,paths_dict[path_part],API_path_keywords_list)
        else:
            return

    paths_dict = {}
    resource_path_dict = {}
    operations_dict = {}
    model_path_dict = {}
    path_model_dict = {}
    models_dict = {}
    API_path_keywords_list = []
    all_API_paths_list = []
    # Get the base paths
    resource_tuple_list = tree_helpers.get_jsonpath_full_paths_and_values('$.features.*.[*]',FMC_instance._json_dict)
    for i in range(0,len(resource_tuple_list)):
        resource_key = re.sub(r'features.|\[[0-9]+\]|\.','',resource_tuple_list[i][0])
        resource_dict = resource_tuple_list[i][1]
        base_path = resource_dict['basePath']
        API_version = resource_dict['apiVersion']
        resource_root = FMC_instance._url_host + '/api' + base_path + '/' + API_version + '/domain/' + FMC_instance.FMC_domain_ID + '/'
        resource_path_dict[resource_key] = resource_root
        models_list = tree_helpers.get_jsonpath_full_paths_and_values('$..models.*.id',resource_dict)
        for model in models_list:
            if not model is None:
                model_path = model[0]
                model_ID = model[1]
                if not model_ID in models_dict:
                    properties_path = model_path
                    properties_path_list = properties_path.split('.')
                    properties_path_list.pop()
                    properties_path_list.append('properties')
                    properties_path = '.'.join(properties_path_list)
                    models_dict[model_ID] = tree_helpers.get_jsonpath_values(properties_path,resource_dict)[0]
        operations_list = tree_helpers.get_jsonpath_values('$..operations',resource_dict)
        for operation_list in operations_list:
            for operation in operation_list:
                if not operation is None:
                    path = resource_root + re.sub('^/','',operation['path'])
                    method = tree_helpers.get_jsonpath_values('$..method',operation)[0]
                    model_ID = None
                    for example in operation['examples']:
                        if 'responseData' in example:
                            if 'type' in example['responseData']:
                                model_ID = example['responseData']['type']
                                break
                    if not model_ID:
                        model_ID = operation['type']['modelId']
                    model_path_dict[model_ID] = path
                    path_model_dict[path] = model_ID
                    if not path in operations_dict:
                        operations_dict[path] = {'methods':{},'operation_path':operation['path'],'resource_root':resource_root}
                    operations_dict[path]['methods'][method] = operation
    for path in operations_dict.keys():
        operation_path = operations_dict[path]['operation_path']
        all_API_paths_list.append(path)
        path_parts = operation_path.split('/')
        path_parts.pop(0) # Get rid of the first '/'
        resource_path = path_parts[0]
        if resource_path in resource_path_dict:
            base_path = resource_path_dict[resource_path]
        else:
            continue
        # Prepend the path root back on path_parts
        path_parts = [base_path] + path_parts
        add_paths_to_dict(path_parts,paths_dict,API_path_keywords_list)
    
    all_API_paths_list.sort()
    return OrderedDict(sorted(resource_path_dict.items())), OrderedDict(sorted(operations_dict.items())), \
           OrderedDict(sorted(model_path_dict.items())), OrderedDict(sorted(paths_dict.items())), \
           API_path_keywords_list, all_API_paths_list, path_model_dict, models_dict

@logged(logger)
@traced(logger)
def get_type_and_id_tuple_list(base_path,json_dict):
    type_list = tree_helpers.get_jsonpath_values(base_path+'.type',json_dict)
    id_list = tree_helpers.get_jsonpath_values(base_path+'.id',json_dict)
    return zip(type_list,id_list)

@logged(logger)
@traced(logger)
def validate_FMC_domain(FMC_Domain,FMC_domain_dict):
    
    def fmc_domain_string(FMC_domain_dict):
        return FMC_domain_dict.keys().join('\n')
    
    if FMC_Domain == 'Global':
        return FMC_Domain
    elif not isinstance(FMC_Domain,str):
        logger.error('A string value must be provided for the %s, provided value is of type %s...' % ('FMC Domain',type(FMC_Domain)))
        raise
    elif not FMC_Domain.startswith('Global/'):
        logger.error('The provided value for the %s is not "Global".  \
                                 If a sub domain is the target, it must be prefixed with "Global/".  \
                                 The provided value = %s...' % ('FMC Domain',FMC_Domain))
        raise
    elif FMC_Domain not in FMC_domain_dict:
        logger.error('The provided value for the %s (%s) does not exist in the FMC.  \
                                 Valid domains names as follows:\n%s' % ('FMC Domain',FMC_Domain,fmc_domain_string(FMC_domain_dict)))
        raise
        
@logged(logger)
@traced(logger)
def get_domain_dict(headers):
    
    domains_dict = {}
    domain_list = json.loads(headers['DOMAINS'])
    for domain_dict in domain_list:
        domains_dict[domain_dict['name']] = domain_dict['uuid']
    return domains_dict

@logged(logger)
@traced(logger)
def build_FMC_URL(FMC_host,FMC_API_path_Ordereddict):
    
    FMC_API_full_path = ''
#     for FMC_API_path_part in FMC_API_path_Ordereddict.items():
#         FMC_API_full_path += FMC_

@logged(logger)
@traced(logger)
def get_child_urls(response_dict,_models_path_dict,API_path_keywords_list,get_item_limit=25):

    response_self_link = None
    response_self_id   = None
    url = response_dict['url']
    child_urls = []
    # if 'self' in response_dict['json_dict']['links']:
    #     response_self_link = re.sub('\?.+','',response_dict['json_dict']['links']['self'])
    # else:
    #     logger.warning('self node not found for url %s...' % (url))
    #     return child_urls # return an empty child_urls list to caller since we can't proceed...
    if 'id' in response_dict['json_dict']:
        response_self_id = response_dict['json_dict']['id']
    else:
        logger.warning('id node not found for url %s...' % (url))
    temp_response_dict = response_dict['json_dict'].copy()
    if 'metadata' in temp_response_dict:
        temp_response_dict.pop('metadata')
#    child_types = tree_helpers.get_jsonpath_full_paths_and_values('$.*..type',response_dict['json_dict'])
    child_types = tree_helpers.get_jsonpath_full_paths_and_values('$.*..type',temp_response_dict)
    logger.debug('child_types found for url %s = \n\t%s' % (url,pformat(child_types)))
    for full_path, id_type in child_types:
        if 'literals' in full_path:
            continue
        logger.debug('Processing child type %s with full_path = %s' % (id_type, full_path))
        child_url = ''
        type_dict = {}
        lower_first_func = lambda s: s[:1].lower() + s[1:] if s else ''
        if not id_type in _models_path_dict \
                and not full_path.split('.')[0] in _models_path_dict \
                and not lower_first_func(id_type) in _models_path_dict \
                and not id_type.lower() in _models_path_dict:
            logger.warning('recurse_API_child_gets: no url found for id_type %s...' % (id_type))
        else:
            logger.debug('child_type = %s' % (id_type))
            type_dict = tree_helpers.get_jsonpath_values(re.sub('\.[^.]+$','',full_path),temp_response_dict)[0]
            if 'links' in type_dict:
                if 'self' in type_dict['links']:
                    child_url = type_dict['links']['self']
                else:
                    logger.warning('Child type %s dictionary has a links node but self url is missing...' % (id_type))
            else:
                if id_type in _models_path_dict:
                    child_url = _models_path_dict[id_type]
                elif full_path.split('.')[0] in _models_path_dict:
                    child_url = _models_path_dict[full_path.split('.')[0]]
                elif lower_first_func(id_type) in _models_path_dict:
                    child_url = _models_path_dict[lower_first_func(id_type)]
                else:
                    child_url = _models_path_dict[id_type.lower()]

                logger.debug('child_model_url = %s' % (child_url))
                if '{containerUUID}' in child_url:
                        if not response_self_id:
                            logger.warning('Child type url %s needs a {containerUUID} but no parent id found...' % (child_url))
                        else:
                            child_url = child_url.replace('{containerUUID}',response_self_id)
                if '{objectId}' in child_url:
                    if 'id' in type_dict:
                        object_id = type_dict['id']
                        child_url = child_url.replace('{objectId}',object_id)
                    else:
                        logger.warning('Child type url %s needs an {objectId} but no id found...' % (child_url))
        type_dict['response_url'] = child_url
        child_urls.append(child_url)
    return child_urls

@logged(logger)
@traced(logger)

def build_request_template_from_model(model_struct):
    
    properties_struct = tree_helpers.get_jsonpath_results(model_struct)
    
# {
#   "type": "AccessPolicy",
#   "name": "AccessPolicy1",
#   "description": "policy to test FMC implementation",
#   "defaultAction": {
#     "intrusionPolicy": {
#       "id": "id_of_existing_or_new_intrusion_policy",
#       "type": "IntrusionPolicy"
#     },
#     "variableSet": {
#       "id": "id_of_variableSet_to_be_added",
#       "type": "VariableSet"
#     },
#     "snmpConfig": {
#       "id": "id_of_snmpConfig_object",
#       "type": "SNMPAlert"
#     },
#     "syslogConfig": {
#       "id": "id_of_syslog_object",
#       "type": "SyslogAlert"
#     },
#     "type": "AccessPolicyDefaultAction",
#     "logBegin": "true/false",
#     "logEnd": "true/false",
#     "sendEventsToFMC": "true/false",
#     "action": "any_allowed_action_enum"
#   }
# }

# {'AccessPolicy': {'id': 'AccessPolicy',
#                   'properties': {'defaultAction': {'id': 'urn:jsonschema:com:cisco:api:external:rest:config:model:IAccessPolicyDefaultAction',
#                                                    'properties': {'action': {'enum': ['BLOCK',
#                                                                                       'TRUST',
#                                                                                       'PERMIT',
#                                                                                       'NETWORK_DISCOVERY'],
#                                                                              'type': 'string'},
#                                                                   'description': {'type': 'string'},
#                                                                   'id': {'type': 'string'},
#                                                                   'intrusionPolicy': {'id': 'urn:jsonschema:com:cisco:api:external:rest:config:model:IIntrusionPolicyModel',
#                                                                                       'properties': {'basePolicy': {'$ref': 'urn:jsonschema:com:cisco:api:external:rest:config:model:IIntrusionPolicyModel',
#                                                                                                                     'type': 'object'},
#                                                                                                      'description': {'type': 'string'},
#                                                                                                      'id': {'type': 'string'},
#                                                                                                      'inlineDrop': {'type': 'integer'},
#                                                                                                      'links': {'$ref': 'urn:jsonschema:com:cisco:api:external:rest:common:model:ILinks',
#                                                                                                                'type': 'object'},
#                                                                                                      'metadata': {'$ref': 'urn:jsonschema:com:cisco:api:external:rest:common:model:IMetadata',
#                                                                                                                   'type': 'object'},
#                                                                                                      'name': {'type': 'string'},
#                                                                                                      'type': {'type': 'string'},
#                                                                                                      'version': {'type': 'string'}},
#                                                                                       'type': 'object'},
#                                                                   'isLockedForChild': {'type': 'boolean'},
#                                                                   'isOverridingParent': {'type': 'boolean'},
#                                                                   'links': {'$ref': 'urn:jsonschema:com:cisco:api:external:rest:common:model:ILinks',
#                                                                             'type': 'object'},
#                                                                   'logBegin': {'type': 'boolean'},
#                                                                   'logEnd': {'type': 'boolean'},
#                                                                   'metadata': {'$ref': 'urn:jsonschema:com:cisco:api:external:rest:common:model:IMetadata',
#                                                                                'type': 'object'},
#                                                                   'name': {'type': 'string'},
#                                                                   'sendEventsToFMC': {'type': 'boolean'},
#                                                                   'snmpConfig': {'$ref': 'urn:jsonschema:com:cisco:api:external:rest:common:model:IReference',
#                                                                                  'type': 'object'},
#                                                                   'syslogConfig': {'$ref': 'urn:jsonschema:com:cisco:api:external:rest:common:model:IReference',
#                                                                                    'type': 'object'},
#                                                                   'type': {'type': 'string'},
#                                                                   'variableSet': {'$ref': 'urn:jsonschema:com:cisco:api:external:rest:common:model:IReference',
#                                                                                   'type': 'object'},
#                                                                   'version': {'type': 'string'}},
#                                                    'type': 'object'},
#                                  'defaultActionEntryObject': {'id': 'urn:jsonschema:com:cisco:nm:vms:api:xsd:UnifiedNGFWDefaultActionEntry',
