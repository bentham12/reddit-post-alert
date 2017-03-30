import argparse
import requests
import time
from datetime import datetime

most_recent_post = ""

parser = argparse.ArgumentParser()
parser.add_argument('-s', required=True, help='subreddit to search')
parser.add_argument('-t', help='search terms separated by +')
parser.add_argument('-l', action='store_true', help='create log file')
args = parser.parse_args()

subreddit = args.s
terms = args.t
log = args.l


def search(s, t):
    global most_recent_post

    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), end=' ')

    if not t:
        t = ""

    base_url = 'https://www.reddit.com/r/' + s + '/search.json?q=' + t
    payload = {'restrict_sr': 'on', 'sort': 'new', 't': 'hour'}
    r = requests.get(base_url, params=payload, headers={'User-agent': 'reddit post alert'})

    if r.status_code == requests.codes.ok:
        data = r.json()
        for post in data['data']['children']:
            # Check if posts have already been seen
            if post['data']['title'] == most_recent_post:
                break
            # Alert user
            print(post['data']['title'])

        # Update most_recent_post to the most recent post in data
        if data['data']['children']:
            most_recent_post = data['data']['children'][0]['data']['title']
            print("most_recent_post", most_recent_post)
        else:
            print("most_recent_post not updated")

        time.sleep(60)
    else:
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print("Error: status code", r.status_code)
            time.sleep(5)

if log:
    file = open(datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".txt", 'w')

while True:
    search(subreddit, terms)
