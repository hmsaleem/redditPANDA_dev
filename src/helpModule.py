'''
@uthor: Saleem

redditPANDA Pipeline, continually scrape a subreddit to get deleted comments.
'''
#----------------------------------------------------------------------
# Suppress pyc files
import sys
sys.dont_write_bytecode = True

#----------------------------------------------------------------------
# Imports
import os

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

post_dict_remove = [
    '_info_params',
    'approved_at_utc',
    'banned_at_utc',
    'can_gild',
    'can_mod_post',
    'is_crosspostable',
    'is_self',
    'is_video',
    'num_crossposts',
    'parent_whitelist_status',
    '_comments',
    '_comments_by_id',
    '_fetched',
    '_flair',
    '_mod',
    '_reddit',
    'approved_by',
    'archived',
    'author_flair_css_class',
    'author_flair_text',
    'banned_by',
    'brand_safe',
    'clicked',
    'pinned',
    'thumbnail_height',
    'thumbnail_width',
    'view_count',
    'whitelist_status',
    'comment_limit',
    'comment_sort',
    'contest_mode',
    'created',
    'distinguished',
    'downs',
    'gilded',
    'hidden',
    'hide_score',
    'likes',
    'link_flair_css_class',
    'link_flair_text',
    'media',
    'media_embed',
    'mod_reports',
    'name',
    'num_reports',
    'over_18',
    'post_hint',
    'preview',
    'quarantine',
    'removal_reason',
    'report_reasons',
    'saved',
    'secure_media',
    'secure_media_embed',
    'selftext_html',
    'spoiler',
    'stickied',
    'subreddit',
    'subreddit_id',
    'subreddit_name_prefixed',
    'subreddit_type',
    'suggested_sort',
    'thumbnail',
    'ups',
    'user_reports',
    'visited']
