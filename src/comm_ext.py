from pprint import pprint
import os
import json

commpath = '/home/ndg/users/hsalee/tools/redditPANDA/data/TwoXChromosomes/'

def clean(body_text):
    body_text = ' '.join(body_text.split())
    body_text = ''.join([i if ord(i) < 128 else ' ' for i in body_text])
    return body_text

#----------------------------------------------------------------------
# Class comment for extracting deleted comments from snapshots


class comment:
    def __init__(self, comment_json, j_obj):
        self.c_id = j_obj['id']
        self.c_obj = comment_json
        self.c_body_snap = []
        self.c_body_snap.append(j_obj['body'])
        return

    def increment(self):
        self.c_body_snap.append('')
        return

    def update(self, j_obj):
        self.c_body_snap[-1] = j_obj['body']
        return

#----------------------------------------------------------------------

def extract_deleted(post_id):
    post_path = os.path.join(commpath, post_id)
    post_files = sorted(os.listdir(post_path))

    post_files = [
	filename for filename in post_files if 'post' not in filename]

    # dict to create snapshots of all the comments in the post
    post_snap = {}

    for filename in post_files:
	for item in post_snap:
	    post_snap[item].increment()
	post_file_path = os.path.join(post_path, filename)
	with open(post_file_path, 'r') as fin:
	    all_lines = fin.readlines()
	for line in all_lines:
	    j_obj = json.loads(line)
	    c_id = j_obj['id']
	    if c_id in post_snap:
		post_snap[c_id].update(j_obj)
	    else:
		post_snap[c_id] = comment(line, j_obj)
        print len(post_snap)

    # extracting deleted comments
    deleted_comments = []
    for c_id in sorted(post_snap.keys()):
	last = clean(post_snap[c_id].c_body_snap[-1])
	if last == '' or last == '[deleted]' or last == '[removed]':
	    # if last == '' or last == '[removed]':
	    first = clean(post_snap[c_id].c_body_snap[0])
	    if first != '' and first != '[deleted]' and first != '[removed]':
		# if first != '' and first != '[removed]':
		deleted_comments.append(post_snap[c_id].c_obj)
    return deleted_comments

p_id = '60prbs'

pprint(extract_deleted(p_id))
