#!/usr/bin/env python
'''
@uthor: Saleem

redditPANDA Pipeline,
crwals a subreddit
continually scrapes to get deleted comments.
'''
#----------------------------------------------------------------------
# Suppress pyc files
import sys
sys.dont_write_bytecode = True

#----------------------------------------------------------------------
# Imports
import ConfigParser
import time
from datetime import datetime
import json
import os
import praw
from catbot import Catbot
from sciurus import scheduler
from tastypy import POD
from pprint import pprint

# Setting up proxy settings
os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:9400'
os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:9400'

#----------------------------------------------------------------------
# Helper methods


def removekeys(d, keys):
    for key in d.keys():
        if key not in keys:
	    try:
                del d[key]
            except KeyError:
                pass
    return


def makedir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return


def ConfigSectionMap(section, Config_obj):
    dict1 = {}
    options = Config_obj.options(section)
    for option in options:
        try:
            dict1[option] = Config_obj.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except BaseException:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


def clean(body_text):
    body_text = ' '.join(body_text.split())
    body_text = ''.join([i if ord(i) < 128 else ' ' for i in body_text])
    return body_text


# Removing un-needed fields
comm_dict_keep= [
     'author',
     'body',
     'controversiality',
     'created_utc',
     'edited',
     'gilded',
     'id',
     'link_id',
     'name',
     'parent_id',
     'score',
     'subreddit']

post_dict_keep = [
     'author',
     'created_utc',
     'gilded',
     'id',
     'locked',
     'num_comments',
     'permalink',
     'score',
     'selftext',
     'subreddit',
     'title',
     'upvote_ratio',
     'url']

#----------------------------------------------------------------------
# Class POST Panda


class postpanda:
    def __init__(self, subname):
        self.reddit = None
        self.catbot = None
        self.track_pod = None
        self.subreddit = subname
        self.previous_posts = []
        self.current_posts = []
        self.config = ConfigParser.ConfigParser()
        self.config.read('CONFIG.INI')
        self.basepath = ConfigSectionMap(
            "CommonConfigs", self.config)['datapath']
        self.datapath = os.path.join(self.basepath, self.subreddit)
        self.commpath = os.path.join(self.datapath, 'comments')
        self.userpath = os.path.join(self.datapath, 'users')
        self.trckpath = os.path.join(self.datapath, 'trackers', 'posttracker')
        return

    # Login into Reddit with config details
    def login(self):
        conf = ConfigSectionMap(self.subreddit, self.config)
        comm = ConfigSectionMap("CommonConfigs", self.config)
        self.reddit = praw.Reddit(
            client_id=conf['client_id'],
            client_secret=conf['client_secret'],
            password=conf['password'],
            username=conf['username'],
            user_agent=conf['user_agent'])
        self.catbot = Catbot(
            comm['slack_secret'],
            conf['slack_channel'],
            comm['slack_user'])
        self.catbot.postToSlack(
            'redditPanda initalized for r/%s' %
            self.subreddit)
        return

    # Setup connection
    def setup(self):
        makedir(self.datapath)
        makedir(self.commpath)
        makedir(self.userpath)
        makedir(self.trckpath)
        self.reddit.read_only = True
        self.reddit.config.store_json_result = True
        self.track_pod = POD(self.trckpath)
        return

    # Retrieve a list of post made during the past 24 hours
    def get_posts(self):
        subreddit = self.reddit.subreddit(self.subreddit)

        time_now = datetime.utcnow()
        post_list = []
        for post in subreddit.new(limit=200):
            timediff = time_now - datetime.utcfromtimestamp(post.created_utc)
            if timediff.days == 0:
                post_list.append(post.id)
        return post_list

    # Retrieve a list of all comments made in a post
    def get_comments(self, post_id):
        post = self.reddit.submission(id=post_id)
        post.comments.replace_more(limit=0)
        all_comments = post.comments.list()
        post_dict = post.__dict__
        try:
            post_dict['author'] = post.author.name
        except AttributeError:
            post_dict['author'] = None
        post_dict['subreddit'] = post.subreddit.display_name
        post_dict['retrieved'] = int(time.time())
        removekeys(post_dict, post_dict_keep)
        z = json.dumps(post_dict)
        data_directory = os.path.join(self.commpath, post_id)
        makedir(data_directory)
        data_file = os.path.join(data_directory, "post_%s.txt" % post_id)
        with open(data_file, 'a') as fout:
            fout.write('%s\n' % z)
        return all_comments

    # Write retrieved comments to file
    def write_comments(self, post_id, all_comments):
        f_index = int(time.time())
        data_directory = os.path.join(self.commpath, post_id)
        makedir(data_directory)
        data_file = os.path.join(
            data_directory, "%s_%s.txt" %
            (post_id, f_index))
        with open(data_file, 'w') as fout:
            for comment in all_comments:
                comment_dict = comment.__dict__
                try:
                    comment_dict['author'] = comment.author.name
                except AttributeError:
                    comment_dict['author'] = None

                comment_dict['subreddit'] = comment.subreddit.display_name
                removekeys(comment_dict, comm_dict_keep)
                z = json.dumps(comment_dict)
                fout.write('%s\n' % z)
        return

    # tracker
    def update_tracker(self):
        tracked_posts = self.track_pod.keys()
        done_posts = sorted(
            list(set(self.previous_posts) - set(self.current_posts)))
        for post_id in done_posts:
            self.track_pod[post_id]['collected'] = True
        new_posts = sorted(
            list(set(self.current_posts) - set(self.previous_posts)))
        for post_id in new_posts:
            self.track_pod[post_id] = {
                'collected': False}
        return


    # The main method
    def redditPANDA(self):
        self.catbot.postToSlack('Runing ... %s' % str(datetime.now())[5:-10])
        self.current_posts = self.get_posts()
        self.update_tracker()
        print 'Getting comments for %s posts' % len(self.current_posts)
        for post_id in self.current_posts:
            all_comments = self.get_comments(post_id)
            print post_id, len(all_comments)
            self.write_comments(post_id, all_comments)
        print 'all files written... %s' % str(datetime.now())[5:-10]
        self.previous_posts = self.current_posts
        return


#----------------------------------------------------------------------
if __name__ == "__main__":

    # Login into Reddit
    subreddit = sys.argv[1]

    p = postpanda(subreddit)
    p.login()
    p.setup()
    p.redditPANDA()

    '''
    # Login into Reddit
    p = panda()
    p.login()
    p.setup()

    # Schedule the scraping
    runPanda = scheduler.scheduler(m=20)
    runPanda.runit(p.redditPANDA)
    '''
