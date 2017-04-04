import argparse
import requests
import time
import smtplib
from datetime import datetime

most_recent_post = ""

parser = argparse.ArgumentParser()
parser.add_argument('-n', required=True, help='10-digit phone number with email gateway (ex. 1234567890@txt.att.net) '
                                              'to receive text alert')
parser.add_argument('-e', required=True, help='email address of GMail bot account to send text from')
parser.add_argument('-p', required=True, help='bot account password')
parser.add_argument('-s', required=True, help='subreddit to search')
parser.add_argument('-t', help='search terms separated by +')
parser.add_argument('-l', action='store_true', help='create log file')
args = parser.parse_args()

phone_number = args.n
email = args.e
password = args.p
subreddit = args.s
terms = args.t
log = args.l


def search(s, t):
    global most_recent_post

    log_out(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\nChecking for new posts...\n")

    if not t:
        t = ""

    base_url = 'https://www.reddit.com/r/' + s + '/search.json?q=' + t
    payload = {'restrict_sr': 'on', 'sort': 'new', 't': 'hour'}
    try:
        r = requests.get(base_url, params=payload, headers={'User-agent': 'reddit post alert'})
    except requests.ConnectionError:
        log_out("Connection error\n\n")
        time.sleep(300)
        return

    if r.status_code == requests.codes.ok:
        data = r.json()
        for post in data['data']['children']:
            # Check if posts have already been seen
            if post['data']['title'] == most_recent_post:
                break
            # Alert user
            message = str(post['data']['title']) + "\n"
            log_out(message)
            alert(message)

        # Update most_recent_post to the most recent post in data
        if data['data']['children']:
            most_recent_post = data['data']['children'][0]['data']['title']

        log_out("\n")
        time.sleep(300)
    else:
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            log_out("Error: status code " + str(r.status_code) + "\n\n")
            time.sleep(20)


def alert(message):
    global email, phone_number, password
    log_out("Sending alert\n")
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(email, password)
        server.sendmail(email, phone_number, message)
        server.quit()
    except:
        log_out("Error sending alert\n")


def log_out(message):
    print(message, end='')
    if log:
        log_file = open(log_file_name, 'a')
        try:
            log_file.write(message)
        except:
            log_file.write("Error writing message to file")
        log_file.close()

if log:
    log_file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".txt"

while True:
    try:
        search(subreddit, terms)
    except KeyboardInterrupt:
        print("Exiting...")
        break
