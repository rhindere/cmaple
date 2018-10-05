'''
Created on May 22, 2018

@author: ronhi
'''

import re,sys
from pprint import pprint
from collections import OrderedDict
from windows_automation.mmap.mmap_main import MindManagerApp
import json
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
import html

def create_mindmap_from_iterable(_dict,topic):

    def process_val(val,topic):
        if type(val) is dict:
            process_dict(val,topic)
        elif type(val) is list:
            process_list(val,topic)
        else:
            topic.add_sub_topic(str(val))

    def process_list(_list,topic):
        list_topic = topic.add_sub_topic('list')
        for val in _list:
            process_val(val,list_topic)
        list_topic.w32_topic.Collapsed = True
        topic.w32_topic.Collapsed = True        

    def process_dict(_dict,topic):
        for key, val in _dict.items():
            dict_topic = topic.add_sub_topic(key)
            process_val(val,dict_topic)
        dict_topic.w32_topic.Collapsed = True
        topic.w32_topic.Collapsed = True        

    process_val(_dict,topic)
    topic.w32_topic.Collapsed = True
        
def create_mindmap_from_iterable_alpha_grouping(_dict,topic):

    def process_val(val,topic):
        if type(val) is dict:
            process_dict(val,topic)
        elif type(val) is list:
            process_list(val,topic)
        else:
            topic.add_sub_topic(str(val))

    def process_list(_list,topic):
        list_topic = topic.add_sub_topic('list')
        for val in _list:
            process_val(val,list_topic)
        list_topic.w32_topic.Collapsed = True
#         topic.w32_topic.Collapsed = True        

    def process_dict(_dict,topic):
        topic_list = []
        if 'type' in _dict:
            _dict.pop('type')
        if 'response_url' in _dict:
            _dict.pop('response_url')
        if 'name' in _dict:
            name = _dict['name']
            _dict.pop('name')
#             first_character = name[0].upper()
#             if not first_character in topic.sub_topic_names:
#                 topic = topic.add_sub_topic(first_character)
#             else:
#                 topic = topic.sub_topic_names[first_character]
#             topic_list.append(topic)
            topic = topic.add_sub_topic(name)
            topic_list.append(topic)
        for key, val in _dict.items():
            dict_topic = topic.add_sub_topic(key)
            topic_list.append(dict_topic)
            process_val(val,dict_topic)
#         for topic in reversed(topic_list):
#             topic.w32_topic.Collapsed = True        

    process_val(_dict,topic)
    topic.w32_topic.Collapsed = True
        
def create_outline(_dict,tab_string):

    def get_list_item_label(_dict):
        if 'name' in _dict:
            if type(_dict['name']) is str:
                return 'name', _dict['name']
        elif 'models' in _dict:
            if type(_dict['models']) is str:
                return 'models', _dict['models']
            elif type(_dict['models']) is dict:
                return 'models', list(_dict['models'].keys())[0]
        elif 'content-type' in _dict:
            if type(_dict['content-type']) is str:
                return 'content-type', _dict['content-type']
            elif type(_dict['models']) is dict:
                return 'content-type', list(_dict['content-type'].keys())[0]
        for key, val in _dict.items():
            if type(val) is str:
                if re.match(r'^[a-zA-Z]+$',val):
                    if re.match(r'^[A-Z]+$',val) or \
                        re.match(r'^[A-Z][a-z]+[A-Z][a-z]+$',val) or \
                        re.match(r'^[a-z]+[A-Z][a-z]+$',val):
                        return key, val
        return None
        
    def process_val(val,tab_string):
        if type(val) is dict:
            process_dict(val,tab_string)
        elif type(val) is list:
            process_list(val,tab_string)
        else:
            if type(val) is str and '-----BEGIN ' in val:
                val = 'Certificate Encoding Omitted...'
            print(tab_string+str(val))

    def process_list(_list,tab_string):
        print(tab_string+'list')
        tab_string += '\t'
        list_counter = 0
        for val in _list:
            if type(val) is dict:
                label = get_list_item_label(val)
                if not label is None:
                    print(tab_string+label[0]+'='+label[1])
                else:
                    list_counter+=1
                    print(tab_string+str(list_counter))
                process_val(val,tab_string + '\t')
            else:
                process_val(val,tab_string)

    def process_dict(_dict,tab_string):
        for key, val in _dict.items():
            print(tab_string+key)
            process_val(val,tab_string+'\t')

    process_val(_dict,tab_string)
        
# flatfile = open(sys.argv[1],'rb').read()
def mm_from_iterable():
    mm_app = MindManagerApp()
    mm_mmap = mm_app.add_mmap(r'C:\Users\ronhi\Documents\LiClipse Workspace\maple_project', 'model_dict.mmap')
    central_topic = mm_mmap.central_topic
    
    flatfile = open(sys.argv[1],'r').read()
    model_dict = eval(flatfile)
    create_mindmap_from_iterable(model_dict,central_topic)

def mm_from_responses():
    flatfile = open(sys.argv[1],'rb').read()
    flatfile = flatfile.decode('utf-16')
    map_dict = eval(flatfile)
    mm_app = MindManagerApp()
    mm_mmap = mm_app.add_mmap(r'C:\Users\ronhi\Documents\LiClipse Workspace\maple_project', 'response_dict.mmap')
    central_topic = mm_mmap.central_topic
    
    for key,val in map_dict.items():
        print(key)
        if 'json_dict' in val:
            json_dict = val['json_dict']
            if json_dict is None:
                continue
            if 'items' in json_dict:
                continue
            if 'links' in json_dict:
                if not 'self' in json_dict['links']:
                    continue
                link = json_dict['links']['self']
                json_dict.pop('links')
                link = link.replace('https://10.1.101.39/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/','')
                link = link.split('/')
                link.pop()
                def json_dict_to_topics(link,topic):
                    if link:
                        link_part = link.pop(0)
                        if not link_part in topic.sub_topic_names:
                            topic = topic.add_sub_topic(link_part)
                        else:
                            topic = topic.sub_topic_names[link_part]
                        topic = json_dict_to_topics(link, topic)
                    return topic
                topic = json_dict_to_topics(link, central_topic)
                create_mindmap_from_iterable_alpha_grouping(json_dict, topic)
                topic.w32_topic.Collapsed = True

def opml_from_responses():
    flatfile = open(sys.argv[1],'rb').read()
    flatfile = flatfile.decode('utf-16')
    map_dict = eval(flatfile)
    
    opml_struct = OrderedDict()
    for key,val in map_dict.items():
        tab_string = ''
        opml_pointer = opml_struct
        print(key)
        if 'json_dict' in val:
            json_dict = val['json_dict']
            if json_dict is None:
                continue
            if 'items' in json_dict:
                continue
            if 'links' in json_dict:
                if not 'self' in json_dict['links']:
                    continue
                link = json_dict['links']['self']
                json_dict.pop('links')
                link = link.replace('https://10.1.101.39/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/','')
                link = link.split('/')
                link.pop()
                for link_part in link:
                    if not link_part in opml_pointer:
                        opml_pointer[link_part] = {}
                    opml_pointer = opml_pointer[link_part]
                    tab_string += '\t'
                if not 'string' in opml_pointer:
                    opml_pointer['string'] = ''
                opml_pointer['string'] += create_opml(json_dict,tab_string)
    return opml_struct

def create_opml(_dict,tab_string,abbreviated=False):

    escape_table = {
        "™":"&#8482;",
        "€":"&euro;",
        " ":"&#32;",
        "!":"&#33;",
        '"':"&#34;",
        "#":"&#35;",
        "$":"&#36;",
        "%":"&#37;",
        "&":"&#38;",
        "'":"&#39;",
        "(":"&#40;",
        ")":"&#41;",
        "*":"&#42;",
        "+":"&#43;",
        ",":"&#44;",
        "-":"&#45;",
        ".":"&#46;",
        "/":"&#47;",
        ":":"&#58;",
        ";":"&#59;",
        "<":"&#60;",
        "=":"&#61;",
        ">":"&#62;",
        "?":"&#63;",
        "@":"&#64;",
        "[":"&#91;",
        "\\":"&#92;",
        "]":"&#93;",
        "^":"&#94;",
        "_":"&#95;",
        "`":"&#96;",
        "{":"&#123;",
        "|":"&#124;",
        "}":"&#125;",
        "~":"&#126;",
        "Non-breaking space":"&#160;",
        "¡":"&#161;",
        "¢":"&#162;",
        "£":"&#163;",
        "¤":"&#164;",
        "¥":"&#165;",
        "¦":"&#166;",
        "§":"&#167;",
        "¨":"&#168;",
        "©":"&#169;",
        "ª":"&#170;",
        "«":"&#171;",
        "¬":"&#172;",
        "":"&#173;",
        "®":"&#174;",
        "¯":"&#175;",
        "°":"&#176;",
        "±":"&#177;",
        "²":"&#178;",
        "³":"&#179;",
        "´":"&#180;",
        "µ":"&#181;",
        "¶":"&#182;",
        "·":"&#183;",
        "¸":"&#184;",
        "¹":"&#185;",
        "º":"&#186;",
        "»":"&#187;",
        "¼":"&#188;",
        "½":"&#189;",
        "¾":"&#190;",
        "¿":"&#191;",
        "À":"&#192;",
        "Á":"&#193;",
        "Â":"&#194;",
        "Ã":"&#195;",
        "Ä":"&#196;",
        "Å":"&#197",
        "Æ":"&#198;",
        "Ç":"&#199;",
        "È":"&#200;",
        "É":"&#201;",
        "Ê":"&#202;",
        "Ë":"&#203;",
        "Ì":"&#204;",
        "Í":"&#205;",
        "Î":"&#206;",
        "Ï":"&#207;",
        "Ð":"&#208;",
        "Ñ":"&#209;",
        "Ò":"&#210;",
        "Ó":"&#211;",
        "Ô":"&#212;",
        "Õ":"&#213;",
        "Ö":"&#214;",
        "×":"&#215;",
        "Ø":"&#216;",
        "Ù":"&#217;",
        "Ú":"&#218;",
        "Û":"&#219;",
        "Ü":"&#220;",
        "Ý":"&#221;",
        "Þ":"&#222;",
        "ß":"&#223;",
        "à":"&#224;",
        "á":"&#225;",
        "â":"&#226;",
        "ã":"&#227;",
        "ä":"&#228;",
        "å":"&#229;",
        "æ":"&#230;",
        "ç":"&#231;",
        "è":"&#232;",
        "é":"&#233;",
        "ê":"&#234;",
        "ë":"&#235;",
        "ì":"&#236;",
        "í":"&#237",
        "î":"&#238;",
        "ï":"&#239;",
        "ð":"&#240;",
        "ñ":"&#241;",
        "ò":"&#242;",
        "ó":"&#243;",
        "ô":"&#244;",
        "õ":"&#245;",
        "ö":"&#246;",
        "÷":"&#247;",
        "ø":"&#248;",
        "ù":"&#249;",
        "ú":"&#250;",
        "û":"&#251;",
        "ü":"&#252;",
        "ý":"&#253;",
        "þ":"&#254;",
        "ÿ":"&#255;",
        "Ā":"&#256;",
        "ā":"&#257;",
        "Ă":"&#258;",
        "ă":"&#259;",
        "Ą":"&#260;",
        "ą":"&#261;",
        "Ć":"&#262;",
        "ć":"&#263;",
        "Ĉ":"&#264;",
        "ĉ":"&#265;",
        "Ċ":"&#266;",
        "ċ":"&#267;",
        "Č":"&#268;",
        "č":"&#269;",
        "Ď":"&#270;",
        "ď":"&#271;",
        "Đ":"&#272;",
        "đ":"&#273;",
        "Ē":"&#274;",
        "ē":"&#275;",
        "Ĕ":"&#276;",
        "ĕ":"&#277",
        "Ė":"&#278;",
        "ė":"&#279;",
        "Ę":"&#280;",
        "ę":"&#281;",
        "Ě":"&#282;",
        "ě":"&#283;",
        "Ĝ":"&#284;",
        "ĝ":"&#285;",
        "Ğ":"&#286;",
        "ğ":"&#287;",
        "Ġ":"&#288;",
        "ġ":"&#289;",
        "Ģ":"&#290;",
        "ģ":"&#291;",
        "Ĥ":"&#292;",
        "ĥ":"&#293;",
        "Ħ":"&#294;",
        "ħ":"&#295;",
        "Ĩ":"&#296;",
        "ĩ":"&#297;",
        "Ī":"&#298;",
        "ī":"&#299;",
        "Ĭ":"&#300;",
        "ĭ":"&#301;",
        "Į":"&#302;",
        "į":"&#303;",
        "İ":"&#304;",
        "ı":"&#305;",
        "Ĳ":"&#306;",
        "ĳ":"&#307;",
        "Ĵ":"&#308;",
        "ĵ":"&#309;",
        "Ķ":"&#310;",
        "ķ":"&#311;",
        "ĸ":"&#312;",
        "Ĺ":"&#313;",
        "ĺ":"&#314;",
        "Ļ":"&#315;",
        "ļ":"&#316;",
        "Ľ":"&#317",
        "ľ":"&#318;",
        "Ŀ":"&#319;",
        "ŀ":"&#320;",
        "Ł":"&#321;",
        "ł":"&#322;",
        "Ń":"&#323;",
        "ń":"&#324;",
        "Ņ":"&#325;",
        "ņ":"&#326;",
        "Ň":"&#327;",
        "ň":"&#328;",
        "ŉ":"&#329;",
        "Ŋ":"&#330;",
        "ŋ":"&#331;",
        "Ō":"&#332;",
        "ō":"&#333;",
        "Ŏ":"&#334;",
        "ŏ":"&#335;",
        "Ő":"&#336;",
        "ő":"&#337;",
        "Œ":"&#338;",
        "œ":"&#339;",
        "Ŕ":"&#340;",
        "ŕ":"&#341;",
        "Ŗ":"&#342;",
        "ŗ":"&#343;",
        "Ř":"&#344;",
        "ř":"&#345;",
        "Ś":"&#346;",
        "ś":"&#347;",
        "Ŝ":"&#348;",
        "ŝ":"&#349;",
        "Ş":"&#350;",
        "ş":"&#351;",
        "Š":"&#352;",
        "š":"&#353;",
        "Ţ":"&#354;",
        "ţ":"&#355;",
        "Ť":"&#356;",
        "ť":"&#357",
        "Ŧ":"&#358;",
        "ŧ":"&#359;",
        "Ũ":"&#360;",
        "ũ":"&#361;",
        "Ū":"&#362;",
        "ū":"&#363;",
        "Ŭ":"&#364;",
        "ŭ":"&#365;",
        "Ů":"&#366;",
        "ů":"&#367;",
        "Ű":"&#368;",
        "ű":"&#369;",
        "Ų":"&#370;",
        "ų":"&#371;",
        "Ŵ":"&#372;",
        "ŵ":"&#373;",
        "Ŷ":"&#374;",
        "ŷ":"&#375;",
        "Ÿ":"&#376;",
        "Ź":"&#377;",
        "ź":"&#378;",
        "Ż":"&#379;",
        "ż":"&#380;",
        "Ž":"&#381;",
        "ž":"&#382;",
        "ſ":"&#383;",
        "Ŕ":"&#340;",
        "ŕ":"&#341;",
        "Ŗ":"&#342;",
        "ŗ":"&#343;",
        "Ř":"&#344;",
        "ř":"&#345;",
        "Ś":"&#346;",
        "ś":"&#347;",
        "Ŝ":"&#348;",
        "ŝ":"&#349;",
        "Ş":"&#350;",
        "ş":"&#351;",
        "Š":"&#352;",
        "š":"&#353;",
        "Ţ":"&#354;",
        "ţ":"&#355;",
        "Ť":"&#356;",
        "ť":"&#577;",
        "Ŧ":"&#358;",
        "ŧ":"&#359;",
        "Ũ":"&#360;",
        "ũ":"&#361;",
        "Ū":"&#362;",
        "ū":"&#363;",
        "Ŭ":"&#364;",
        "ŭ":"&#365;",
        "Ů":"&#366;",
        "ů":"&#367;",
        "Ű":"&#368;",
        "ű":"&#369;",
        "Ų":"&#370;",
        "ų":"&#371;",
        "Ŵ":"&#372;",
        "ŵ":"&#373;",
        "Ŷ":"&#374;",
        "ŷ":"&#375;",
        "Ÿ":"&#376;",
        "Ź":"&#377",
        "ź":"&#378;",
        "Ż":"&#379;",
        "ż":"&#380;",
        "Ž":"&#381;",
        "ž":"&#382;",
        "ſ":"&#383;",
    }
    
    def html_escape(text):
        """Produce entities within text."""
        text_string = ''
        for c in text:
#             if not c in escape_table and not re.match(r'[0-9a-zA-Z]',c):
#                 continue
            text_string += escape_table.get(c,c)
        return text_string
#         return "".join(escape_table.get(c,c) for c in text)

    def process_val(val,opml_string,tab_string):
        if type(val) is dict:
            opml_string = process_dict(val,opml_string,tab_string)
        elif type(val) is list:
            opml_string = process_list(val,opml_string,tab_string)
        else:
            if type(val) is str and '-----BEGIN ' in val:
                val = 'Certificate Encoding Omitted...'
            opml_string += tab_string+'<outline text="'+html_escape(str(val))+'">\n'
            opml_string += tab_string+'</outline>\n'
        return opml_string

    def process_list(_list,opml_string,tab_string):
        opml_string += tab_string+'<outline text="list">\n'
        for val in _list:
            opml_string = process_val(val,opml_string,tab_string+'\t')
#             opml_string += tab_string+'\t</outline>\n'
        opml_string += tab_string+'</outline>\n'
        return opml_string

    def process_dict(_dict,opml_string,tab_string):
        closers = []
        if abbreviated:
            if 'response_url' in _dict:
                _dict.pop('response_url')
            if 'type' in _dict:
                _dict.pop('type')
            if 'id' in _dict:
                _dict.pop('id')
            if 'metadata' in _dict:
                _dict.pop('metadata')
            if 'name' in _dict:
                name = _dict['name']
                _dict.pop('name')
                name_string = tab_string+'<outline text="'+html_escape(name)+'">\n'
                closers.append(tab_string+'</outline>\n')
                opml_string += name_string
                tab_string += '\t'
        for key, val in _dict.items():
            opml_string += tab_string+'<outline text="'+html_escape(key)+'">\n'
            opml_string = process_val(val,opml_string,tab_string+'\t')
            opml_string += tab_string+'</outline>\n'
        for closer in closers:
            opml_string += closer
        return opml_string

    return process_val(_dict,'',tab_string)

def dump_opml(opml_struct,tab_string,opml_file):
    for key,val in opml_struct.items():
        closers = []
        if not key == 'string':
            print(tab_string+'<outline text="'+key+'">',file=opml_file)
            closers.append(tab_string+'</outline>')
        if type(val) is dict:
            dump_opml(val,tab_string+'\t',opml_file)
        elif type(val) is str:
            print(val,file=opml_file,end='')
        for closer in closers:
            print(closer,file=opml_file)


opml_file = open('api-docs-fmcwithll.json','r').read()
opml_struct = json.loads(opml_file)
create_outline(opml_struct,'')
# opml_string = create_opml(opml_struct,'')
# print(opml_string)


# opml_file = open('responses.opml','w')
# opml_struct = opml_from_responses(abbreviated=True)
# print('<opml version="1.0">\n<head><title></title><dateCreated>2018-05-27T12:27:17</dateCreated><dateModified>2018-05-27T12:27:17</dateModified><ownerName>Windows User</ownerName></head><body>',file=opml_file)
# tab_string = ''
# dump_opml(opml_struct,tab_string,opml_file)
# print('</body></opml>',file=opml_file)
