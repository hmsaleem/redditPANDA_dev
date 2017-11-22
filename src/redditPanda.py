#!/usr/bin/env python
'''
@uthor: Saleem
Date: Jan 27, 2017
Updated: March 1, 2017
Updated: March 9, 2017
Completed: April 17, 2017

redditPANDA Pipeline, continually scrape a subreddit to get deleted comments.
'''
#----------------------------------------------------------------------
# Suppress pyc files
import sys
sys.dont_write_bytecode = True

#----------------------------------------------------------------------
# Imports
import time
from datetime import datetime
import json
import os 
import praw
#import config as c
import config_2x as c
from catbot import Catbot
from sciurus import scheduler

#----------------------------------------------------------------------
# Helper methods
def removekeys(d, keys):
    for key in keys:
        try: 
            del d[key]
        except KeyError:
            pass
    return 

def makedir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return


# Removing un-needed fields
to_remove = ['_fetched', '_mod', '_reddit', '_replies', '_submission', 'approved_by', 'archived', 'author_flair_css_class', 'author_flair_text', 'banned_by', 'body_html', 'created', 'distinguished', 'downs', 'likes', 'mod_reports', 'num_reports', 'removal_reason', 'report_reasons', 'saved', 'score_hidden', 'stickied', 'subreddit_id', 'subreddit_name_prefixed', 'subreddit_type', 'ups', 'user_reports']

to_remove_too = ['_comments', '_comments_by_id', '_fetched', '_flair', '_mod', '_reddit', 'approved_by', 'archived', 'author_flair_css_class', 'author_flair_text', 'banned_by', 'brand_safe', 'clicked', 'comment_limit', 'comment_sort', 'contest_mode', 'created', 'distinguished', 'downs', 'gilded', 'hidden', 'hide_score', 'likes', 'link_flair_css_class', 'link_flair_text', 'media', 'media_embed', 'mod_reports', 'name', 'num_reports', 'over_18', 'post_hint', 'preview', 'quarantine', 'removal_reason', 'report_reasons', 'saved', 'secure_media', 'secure_media_embed', 'selftext_html', 'spoiler', 'stickied', 'subreddit', 'subreddit_id', 'subreddit_name_prefixed', 'subreddit_type', 'suggested_sort', 'thumbnail', 'ups', 'user_reports', 'visited']

#----------------------------------------------------------------------
# Class Panda
class panda:
    def __init__(self):
        self.reddit = None
        self.submissions_past = []
        self.submissions_present = []
        self.datapath = os.path.join(c.datapath, c.subname)
        return

    # Login into Reddit with config details
    def login(self):
        self.reddit = praw.Reddit(client_id=c.client_id, client_secret=c.client_secret, password=c.password, username=c.username, user_agent=c.user_agent)
        return

    # Setup connection
    def setup(self):
        makedir(self.datapath)
        self.reddit.read_only = True
        self.reddit.config.store_json_result = True
        return

    # Retrieve a list of submission made during the past 24 hours
    def update_submissions(self):
        subreddit = self.reddit.subreddit(c.subname)

        time_now = datetime.utcnow()
        submission_list = []
        for submission in subreddit.new(limit=200):
            timediff = str(time_now -datetime.utcfromtimestamp(submission.created_utc))
            if 'day' not in timediff:
                submission_list.append(submission.id)
        return submission_list
    
    # Retrieve a list of all comments made in a submission
    def get_comments(self, submission_id):
        submission = self.reddit.submission(id=submission_id)
        submission.comments.replace_more(limit=0)
        all_comments = submission.comments.list()
        submission_dict = submission.__dict__
        try:
            submission_dict['author'] = submission.author.name
        except AttributeError:
            submission_dict['author'] = None
        submission_dict['retrieved'] = int(time.time())
        removekeys(submission_dict, to_remove_too)
        z = json.dumps(submission_dict)
        data_directory = os.path.join(self.datapath, submission_id)
        makedir(data_directory)
        data_file = os.path.join(data_directory, "post_%s.txt" %submission_id)
        with open(data_file, 'a') as fout:
            fout.write('%s\n' % z)
        return all_comments

    # Write retrieved comments to file
    def write_comments(self, submission_id, all_comments):
        f_index = int(time.time())
        data_directory = os.path.join(self.datapath, submission_id)
        makedir(data_directory)
        data_file = os.path.join(data_directory, "%s_%s.txt" % (submission_id, f_index))
        with open(data_file, 'w') as fout:
            for comment in all_comments:
                comment_dict = comment.__dict__
                try:
                    comment_dict['author'] = comment.author.name
                except AttributeError:
                    comment_dict['author'] = None
                    
                comment_dict['subreddit'] = comment.subreddit.display_name                  
                removekeys(comment_dict, to_remove)
                z = json.dumps(comment_dict)
                fout.write('%s\n' % z)
        return
    
    # The main method
    def redditPANDA(self):
        Catbot('Runing ... %s'%str(datetime.now())[5:-10])
        self.submissions_present = self.update_submissions()
        print 'get comms for %s posts'%len(self.submissions_present)
        for submission_id in self.submissions_present:
            all_comments = self.get_comments(submission_id)
            print submission_id, len(all_comments)
            self.write_comments(submission_id, all_comments)
        print 'all files written... %s'%str(datetime.now())[5:-10]
        done = sorted(list(set(self.submissions_past) - set(self.submissions_present)))
        done_file = os.path.join(self.datapath, 'done.txt')
        with open(done_file, 'a') as fin:
            for s_id in done:
                fin.write('%s\n'%s_id)
        self.submissions_past = self.submissions_present
        return

#----------------------------------------------------------------------
if __name__ == "__main__":
    # Login into Reddit
    p = panda()
    p.login()
    p.setup()

    # Schedule the scraping
    runPanda = scheduler.scheduler(m=20)
    runPanda.runit(p.redditPANDA)
