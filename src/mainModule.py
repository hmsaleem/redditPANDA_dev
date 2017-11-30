'''
redditPANDA
Main Module

@uthor: Haji Mohammad Saleem
Date: November 27, 2017
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

#----------------------------------------------------------------------


