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
import multiprocessing
from pprint import pprint


#Helper functions
raw_path = '/home/ndg/arc/reddit/2017/'
local_data_path = '/home/ndg/users/hsalee/tools/redditPANDA/data'

with open('auths.txt', 'r') as fin:
    all_auths = fin.readlines()

all_auths = [x.strip() for x in all_auths]

all_files = sorted(os.listdir(raw_path))
all_files = [x for x in all_files if 'RC_2017-03' in x or 'RC_2017-04' in x]

#Compile Subreddit info



def sub_sampler(file_name):
    print file_name
    file_path = os.path.join(raw_path, file_name)
    out_path = os.path.join(local_data_path, 'authinfo')
    
    with gzip.open(file_path, 'r') as fin:
        all_lines = fin.readlines()

    auth_comm = []
    for line in all_lines:
        jobj = json.loads(line)
        auth = jobj['author']
        if auth in all_auths:
            auth_comm.append(line)

    out_file_name = file_name[:-3]
    out_file_path = os.path.join(out_path, out_file_name)
    with open(out_file_path, 'w') as fp:
        for line in auth_comm:
            fp.write(line)
    return

#Multiprocessing Pool

def mp_sampler():
    p = multiprocessing.Pool(10)
    p.map(sub_sampler, all_files)

#Run it

if __name__ == '__main__':
    mp_sampler()
