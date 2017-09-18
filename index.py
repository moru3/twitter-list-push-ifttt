from twitter import *

import datetime
import urllib.request
import json
import time
import os

def handler(event, context):
    now = datetime.datetime.now(datetime.timezone.utc)
    start_date = now - datetime.timedelta(hours=1)
    send_ifttt_push_notification(get_list_tweets(start_date))

def get_list_tweets(start_date):
    consumer_key = os.environ.get('TW_CONSUMER_KEY')
    consumer_secret = os.environ.get('TW_CONSUMER_SECRET')
    token = os.environ.get('TW_ACCESS_TOKEN')
    token_secret = os.environ.get('TW_ACCESS_TOKEN_SECRET')
    screen_name = os.environ.get('TW_LIST_OWNER_SCREEN_NAME')
    list_name = os.environ.get('TW_LIST_LIST_NAME')

    t = Twitter(auth=OAuth(token, token_secret, consumer_key, consumer_secret))

    # get target list tweets
    max_count = 100
    t_list = t.lists.statuses(
        owner_screen_name=screen_name, slug=list_name, include_rts=False, count=max_count)

    result_dict = {}
    for tweet in t_list:
        print(tweet['text'])
        # Thu Sep 14 02:53:45 +0000 2017
        create_at = datetime.datetime.strptime(
            tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
        if create_at >= start_date:
            user_name = tweet['user']['name']
            print("OK:" + user_name)
            obj = []
            if user_name in result_dict:
                obj = result_dict[user_name]
            obj.append(tweet['text'])
            result_dict[user_name] = obj
        else:
            print("break")
            break
    return result_dict

def send_ifttt_push_notification(result_dict):
     # request ifttt endpoint
    ifttt_url = os.environ.get('IFTTT_ENDPOIMT_URL')
    method = "POST"
    headers = {"Content-Type": "application/json"}
    for k, v in result_dict.items():
        push_str = k + "[" + v[0] + "](" + str(len(v)) + ")"
        push_str = push_str.replace("http", "[URL]")
        print(push_str)
        obj = {"value1": push_str}
        json_data = json.dumps(obj).encode("utf-8")
        request = urllib.request.Request(
            ifttt_url, data=json_data, method=method, headers=headers)
        response = urllib.request.urlopen(request)
        r = response.read()
        print(r)