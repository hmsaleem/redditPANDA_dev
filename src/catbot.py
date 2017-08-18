'''
@uthor: HSaleem

Simple slack bot.
'''

import sys
sys.dont_write_bytecode = True

# import config as c
import config_2x as c
from slacker import Slacker

class Catbot:

    def __init__(self, message):
        self.message = message
        self.slackClient = Slacker(c.secret)
        self.postToSlack()

    def postToSlack(self):
        try:
            print self.message
            self.slackClient.chat.post_message(
            	c.channel, self.message, as_user=c.user)
        except Exception as e:
            print e
