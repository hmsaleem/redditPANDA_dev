'''
@uthor: HSaleem

Simple slack bot.
'''

import sys
sys.dont_write_bytecode = True

from slacker import Slacker


class Catbot:

    def __init__(self, secret, channel, user):
        self.secret = secret
        self.channel = channel
        self.user = user
        self.slackClient = Slacker(self.secret)

    def postToSlack(self, message):
        try:
            print message
            self.slackClient.chat.post_message(
                self.channel, message, as_user=self.user)
        except Exception as e:
            print e
