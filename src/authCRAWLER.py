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
import prawcore
from catbot import Catbot
from sciurus import scheduler
from tastypy import POD
from pprint import pprint


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
comm_dict_keep = [
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

subs = ['loseit', 'relationships', 'TwoXChromosomes']

#----------------------------------------------------------------------
# Main methods


def get_collected(subreddit):
    collected_posts = []
    datapath = os.path.join(basepath, subreddit)
    trckpath = os.path.join(datapath, 'trackers', 'posttracker')
    track_pod = POD(trckpath)
    for key in track_pod._keys:
        if track_pod[key]:
            collected_posts.append(key)
    return collected_posts


def process_posts(subreddit, post_id):
    datapath = os.path.join(basepath, subreddit)
    commpath = os.path.join(datapath, 'comments')
    post_path = os.path.join(commpath, post_id)
    post_files = sorted(os.listdir(post_path))
    post_files = [
        filename for filename in post_files if 'post' not in filename]

    comms_dict = {}
    miss_comms = set()

    for filename in post_files:
        post_file_path = os.path.join(post_path, filename)
        with open(post_file_path, 'r') as fin:
            all_lines = fin.readlines()
        for line in all_lines:
            j_obj = json.loads(line)
            c_id = j_obj['id']
            c_body = j_obj['body']
            if clean(c_body) == "[removed]":
                miss_comms.add(c_id)
            if c_id not in comms_dict:
                comms_dict[c_id] = []
            comms_dict[c_id].append(j_obj)

    auth_list = []
    for item in miss_comms:
        body = clean(comms_dict[item][0]['body'])
        if body != "[removed]":
            author = comms_dict[item][0]['author']
            if author != "[removed]" and author != "[deleted]":
                auth_list.append(author)

    return auth_list


def get_users(usertrack_pod, subreddit):
    datapath = os.path.join(basepath, subreddit)
    userpath = os.path.join(datapath, 'users')
    for user in usertrack_pod._keys:
        print user
        last_comment_id = usertrack_pod[user]
        if last_comment_id != 'deleted':
            comments = []
            try:
                for comment in reddit.redditor(user).comments.new(limit=None):
                    if comment.id == last_comment_id:
                        break
                    comments.append(comment)
                comments = comments[::-1]
            except prawcore.exceptions.NotFound:
                usertrack_pod[user] = 'deleted'
                usertrack_pod.sync()
            if comments:
                user_file = os.path.join(userpath, user + '.txt')
                with open(user_file, 'a') as fout:
                    for item in comments:
                        comment_dict = item.__dict__
                        comment_dict['author'] = item.author.name
                        comment_dict['subreddit'] = item.subreddit.display_name
                        removekeys(comment_dict, comm_dict_keep)
                        z = json.dumps(comment_dict)
                        fout.write('%s\n' % z)
                last_comment_id = comments[-1].id
                usertrack_pod[user] = last_comment_id
                usertrack_pod.sync()
    catbot.postToSlack('Complete ... %s, %s' %
                       (subreddit, str(datetime.now())[5:-10]))
    return


def userPANDA(subreddit):
    # Setup
    datapath = os.path.join(basepath, subreddit)
    posttrpath = os.path.join(datapath, 'trackers', 'processtracker')
    usertrpath = os.path.join(datapath, 'trackers', 'usertracker')
    makedir(posttrpath)
    makedir(usertrpath)
    processtrack_pod = POD(posttrpath)
    usertrack_pod = POD(usertrpath)

    collected_posts = get_collected(subreddit)

    processed_posts = processtrack_pod._keys
    processed_users = usertrack_pod._keys

    collected_posts = list(set(collected_posts) - set(processed_posts))

    collected_users = []

    for post_id in collected_posts:
        collected_users.extend(process_posts(subreddit, post_id))
        processtrack_pod[post_id] = True
    processtrack_pod.sync()

    collected_users = list(set(collected_users) - set(processed_users))
    for user in collected_users:
        usertrack_pod[user] = None
    usertrack_pod.sync()

    get_users(usertrack_pod, subreddit)

    return


#----------------------------------------------------------------------
if __name__ == "__main__":

    config = ConfigParser.ConfigParser()
    config.read('CONFIG.INI')
    basepath = ConfigSectionMap("CommonConfigs", config)['datapath']

    # Login into Reddit with config details
    conf = ConfigSectionMap('users', config)
    proxyport = str(conf['proxpyport'])
    os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:{}'.format(proxyport)
    os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:{}'.format(proxyport)
    comm = ConfigSectionMap("CommonConfigs", config)
    reddit = praw.Reddit(
        client_id=conf['client_id'],
        client_secret=conf['client_secret'],
        password=conf['password'],
        username=conf['username'],
        user_agent=conf['user_agent'])
    catbot = Catbot(
        comm['slack_secret'],
        conf['slack_channel'],
        comm['slack_user'])
    catbot.postToSlack(
        'redditPanda initalized for users')

    # Setup connection
    reddit.read_only = True
    reddit.config.store_json_result = True

    # Get comments
    for subreddit in subs:
        userPANDA(subreddit)
