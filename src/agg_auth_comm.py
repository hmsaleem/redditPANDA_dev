'''
@uthor: Saleem
Date: November 4, 2017
Parse a month of data and create a subreddit profile
'''

#Imports

import os
import sys
sys.dont_write_bytecode = True
import time
import json
import gzip
from pprint import pprint


#Helper functions
local_data_path = '/home/ndg/users/hsalee/tools/redditPANDA/data'

with open('auths.txt', 'r') as fin:
    all_auths = fin.readlines()

all_auths = sorted([x.strip() for x in all_auths])

auth_dict = {}

for auth in all_auths:
    auth_dict[auth] = []


all_files = sorted(os.listdir(os.path.join(local_data_path, 'authinfo')))
all_files = [x for x in all_files if '.txt' in x]

#Compile Subreddit info



for filename in all_files:
    print filename
    file_path = os.path.join(local_data_path, 'authinfo', filename)
    
    with open(file_path, 'r') as fin:
        all_lines = fin.readlines()

    for line in all_lines:
        jobj = json.loads(line)
        auth = jobj['author']
        auth_dict[auth].append(line)


for auth in all_auths:
    print auth
    auth_list = auth_dict[auth]
    out_file_name = auth+'.txt'
    out_file_path = os.path.join(local_data_path, 'authinfo', out_file_name)
    with open(out_file_path, 'w') as fp:
        for line in auth_list:
            fp.write(line)
    

