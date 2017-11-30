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



reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            username=username,
            user_agent=user_agent)

reddit.read_only = True
reddit.config.store_json_result = True

subreddit = 'soccer'
subreddit = reddit.subreddit(subreddit)
for post_id in subreddit.new(limit=10):
    post = reddit.submission(id=post_id.id)
    post.comments.replace_more(limit=0)
    all_comments = post.comments.list()
    #for comment in all_comments:
    #    pprint(comment.__dict__)
    pprint(post.__dict__)
    #pprint(sorted(post.__dict__.keys()))

