import logging.config
import inspect
import os

import time
from pathlib import Path
import fnmatch
from tqdm import tqdm
import requests
import json
import functools
from ratelimit import limits, sleep_and_retry

from .write import  write_output
from .contants import (
    API_KEY,
    API_HEADERS,
    ORDER_URL,
)

##################
# Logging Config
#################
filename = inspect.getfile(inspect.currentframe())
filename = Path(filename).stem
source = 'logs/'+filename
logging.config.fileConfig('logging.conf', defaults={'logfilename': source})
logger_default = logging.getLogger('pipeline')
logger_issue = logging.getLogger('root')


ORDERS_LOC = r"orders/"
file_num = len(fnmatch.filter(os.listdir(ORDERS_LOC), '*.json'))

res = ""

# x = len(fnmatch.filter(os.listdir(ORDERS_LOC), '*.json'))
# print(x)


def run_ordering():
    successful_orders = 0
    output_folder = "order_responses/"
    output_file = output_folder + "responses.json"
    responses = {}
    for loop_index in tqdm(range(len(fnmatch.filter(os.listdir(ORDERS_LOC), '*.json')))): # process all orders in /orders
    # for loop_index in tqdm(range(45, 55)): # select for debugging (limit to n mount of orders)
        order_item = json.load(open(f"{ORDERS_LOC}/{loop_index}.json"))
        if order_item is not None:
            print(order_item.keys())
            post_order = {
                "name": "sent_data_request",
                "subscription_id": 394726,
                "products": [
                    # building upto 1000 objects per request for bulk ordering
                    {
                        "item_ids": order_item['PSScene4Band'],
                        "item_type": "PSScene4Band",
                        "product_bundle": "analytic"
                    }
                ]
            }
            # print(post_order)
            session = requests.Session()
            session.auth = (API_KEY, "")
            response = session.post(ORDER_URL, json=post_order, headers=API_HEADERS)
            print(response.status_code)
            if response.status_code == 202:

                responses.update({successful_orders: response.json()})
                successful_orders += 1 # TODO store this information  to be metric data
            else:
                logger_issue.error(f"vendor is currently down or not returning 202 status code so data could not be POST'ed")

    # return(responses) # all orders with current status
    check_order_status(responses)


@sleep_and_retry
@limits(calls=3, period=1)  # 4 requests per 1 sec
def get_status(build, item):
    session = requests.Session()
    session.auth = (API_KEY, "")
    ORDER_URL =f"https://api.planet.com/compute/ops/orders/v2/{item}"
    response = session.get(ORDER_URL, headers=API_HEADERS)
    data = response.json()

    if build:
        return data

    if data['state'] == 'success':
        return item


def check_order_status(input=None, ids=None, still_orders_left=False):
    completed_order_data = {}
    id_list = []
    if still_orders_left == True:
        time.sleep(120) # sleep for 2 minutes for orders not ready (120 sec) = 2 min = Avg order time planet
        id_list = list(map(functools.partial(get_status, False), ids))

    if ids is None:
        ids = []
        json_data={}
        if type(input) is dict:
            json_data = input
        if type(input) is str: # location of order forms generated from
            logger_default.info(f"now processing {input}")
            json_data = json.load(open(input))
        if type(input) is None:
            logger_issue.error("no data was captured in the run_ordering() function")
            return False
        for key, value in json_data.items():
            ids.append(value["id"])

        id_list = list(map(functools.partial(get_status, False), ids))

    for item in id_list:
        if item is not None:
            ids.remove(item)

    if len(ids) >= 1:
        check_order_status(ids=ids, still_orders_left=True)
    else:
        orders = list(map(functools.partial(get_status, True), id_list))
        for item in orders:
            logger_default.info(f"order {item['id']} was successfully completed")
            completed_order_data.update({"completed_orders": {item['id']: item}})

    write_output(output_folder="order_responses/", output_file="order_responses/completed_orders", data=completed_order_data)
