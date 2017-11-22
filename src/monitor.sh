#!/bin/bash
until ./redditPanda.py; do
        echo "RedditPANDA crashed with exit code $?. Restarting in 10 minutes..." >&2
        sleep 600
done
