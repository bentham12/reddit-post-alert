import argparse
import requests
import time

parser = argparse.ArgumentParser()
parser.add_argument('-s', required=True, help='subreddit to search')
parser.add_argument('-t', help='search terms')
args = parser.parse_args()

subreddit = args.s
terms = args.t


def search(s, t):
    if not t:
        t = ""

    base_url = 'https://www.reddit.com/r/' + s + '/search.json?q=' + t
    payload = {'restrict_sr': 'on', 'sort': 'new', 't': 'hour'}
    r = requests.get(base_url, params=payload, headers={'User-agent': 'reddit post alert'})

    if r.status_code == requests.codes.ok:
        data = r.json()
        for post in data['data']['children']:
            print(post['data']['title'])

        time.sleep(60)
    else:
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print("Error: status code", r.status_code)
            time.sleep(5)

while True:
    search(subreddit, terms)
