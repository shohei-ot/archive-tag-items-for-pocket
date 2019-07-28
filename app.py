# coding: UTF-8

import sys
import time
import urllib
import json
from dotenv import load_dotenv
from loguru import logger
import requests
from os import environ
from os.path import join, dirname
import fire
import math

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CONSUMER_KEY = environ.get("POCKET_CONSUMER_KEY")
ACCESS_TOKEN = environ.get("POCKET_ACCESS_TOKEN")

def get_common_params():
    if CONSUMER_KEY is None or ACCESS_TOKEN is None:
        logger.error('Requrie POCKET_CONSUMER_KEY, POCKET_ACCESS_TOKEN, KEY_NAME')
        sys.exit(1)
    params = {
        'consumer_key': CONSUMER_KEY,
        'access_token': ACCESS_TOKEN
    }
    return params

def req(method, url, params):
    reqParams = {
        **get_common_params(),
        **params
    }

    # logger.warning(json.dumps(reqParams))
    # sys.exit(1)

    resp = requests.request(method, url, params=reqParams)
    if resp.status_code != 200:
        logger.error('status code ' + str(resp.status_code))
        logger.error(resp.headers)
        sys.exit(1)
    # return json.loads(resp.content)
    return resp.json()

def req_tag_items(tag = None):
    if tag is None:
        logger.error('require tag')

    respJson = req('GET', 'https://getpocket.com/v3/get', {
        'tag': tag
    })

    # if respJson['status'] != 1:
    #     logger.error('unexpected status: ' + str(respJson['status']) + ', ' + str(respJson['error']))
    #     sys.exit(1)
    return respJson['list']

def req_archive(items):
    itemIds = items.keys()
    actions = list()
    for itemId in itemIds:
        q = {
            'action': 'archive',
            'item_id': itemId,
            'time': str(math.floor(time.time()))
        }
        actions.append(q)

    # acts = urllib.parse.quote(json.dumps(actions))
    acts = json.dumps(actions)
    logger.info(acts)

    respJson = req('GET', 'https://getpocket.com/v3/send', {
        'actions': acts
    })

    if respJson['status'] != 1 or respJson['action_results'][0] != True:
        logger.error('faild')
        sys.exit(1)

    dmp = json.dumps(respJson)
    logger.success(dmp)
    return True

def run(tag = None):
    if tag is None:
        logger.error('Usage: python app.py "my tag name"')
        sys.exit(1)

    logger.info('tag: ' + tag)

    items = req_tag_items(tag)
    # logger.info(json.dumps(items))
    if len(items) > 0:
        req_archive(items)
    else:
        logger.info('no items')
    sys.exit(0)

if __name__ == '__main__':
    fire.Fire(run)