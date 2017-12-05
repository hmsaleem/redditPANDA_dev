'''
redditPANDA
Module to collect author data

@uthor: Haji Mohammad Saleem
Date: November 23, 2017
'''

import praw
from pprint import pprint
from datetime import datetime
from tastypy import POD
import json

username = "new_in_montreal"
password = "4evNX4FNQ9&P"
client_id = "e0zhtOtJaykVgA"
client_secret = "EQS8F-7J_kknyroFr_pGQa6TwCA"
user_agent = "reddit scraper by /u/new_in_montreal"


def removekeys(d, keys):
    for key in keys:
        try:
            del d[key]
        except KeyError:
            pass
    return


# Removing un-needed fields
comm_dict_remove = [
    '_fetched',
    '_mod',
    '_reddit',
    '_replies',
    '_post',
    '_info_params',
    '_submission',
    'approved_by',
    'approved_at_utc',
    'banned_at_utc',
    'can_gild',
    'can_mod_post',
    'collapsed',
    'collapsed_reason',
    'archived',
    'author_flair_css_class',
    'author_flair_text',
    'banned_by',
    'body_html',
    'created',
    'distinguished',
    'downs',
    'likes',
    'mod_reports',
    'num_reports',
    'removal_reason',
    'report_reasons',
    'saved',
    'score_hidden',
    'stickied',
    'subreddit_id',
    'subreddit_name_prefixed',
    'subreddit_type',
    'ups',
    'user_reports']


reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    password=password,
    username=username,
    user_agent=user_agent)

reddit.read_only = True
reddit.config.store_json_result = True

user_name = 'beavermakhnoman'
counter = 0
a = datetime.now()

last_collected = ''

comments = []
for comment in reddit.redditor(user_name).comments.new(limit=None):
    if comment.id == last_collected:
        break
    comments.append(comment)

comments = comments[::-1]
with open(user_name + '.txt', 'w') as fout:
    for item in comments:
        comment_dict = item.__dict__
        #comment_dict['author'] = comment.author.name
        #comment_dict['subreddit'] = comment.subreddit.display_name
        #removekeys(comment_dict, comm_dict_remove)
        #z = json.dumps(comment_dict)
        #fout.write('%s\n' % z)
        pprint(sorted(comment_dict.keys()))
        break
