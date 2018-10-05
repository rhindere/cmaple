'''
Created on May 22, 2018

@author: ronhi
'''

import re,sys

flatfile = open(sys.argv[1],'r')

flatfile_string = ''

split_pattern = ''
type_line = ''
for line in flatfile:
    if '~type' in line:
        type_line = line
        continue
    if not type_line == '':
        while '~type' in type_line:
            #print(line)
            #print(type_line)
            type_pattern = re.match(r'^(.+?~type,*)',type_line).group(1)
            print(type_pattern)
            comma_count = type_pattern.count(',')
            if type_pattern.endswith(','):
                comma_count -= 1
            split_pattern = '((?:{},){}[^,]+,*)'.format('.+?','{'+str(comma_count)+'}')
            #print(split_pattern)
            record_match = re.match(split_pattern,line)
            if record_match:
                print(record_match.group(1))
                line = line.replace(record_match.group(1),'')
                type_line = type_line.replace(type_pattern,'')
            else:
                break
#     flatfile_string += line

# flatfile_split = re.split(r'https://10\.1\.101\.39/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/',flatfile_string)
