import json
import requests
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm
import os

from .cluster import get_bboxes
from .utils import gen_api_input
from .contants import (
    API_KEY,
    API_HEADERS,
    BANDS_REQUIRED,
    DATE_OF_INTEREST,
    URL,
)


@sleep_and_retry
@limits(calls=3, period=1)  # 4 requests per 1 sec
def _get_next_orders(session, new_url):
    # Planet API - makes a get request to the Data API
    res = session.get(new_url, headers=API_HEADERS)
    text = res.text
    json_text = json.loads(text)
    return json_text


@sleep_and_retry
@limits(calls=3, period=1)  # 4 requests per 1 sec
def _get_orders(session, api_input):
    """
        Mutates the order dict with orders before returning
    """
    res = session.post(URL, data=json.dumps(api_input), json=True, headers=API_HEADERS)
    text = res.text
    json_text = json.loads(text)
    order_dict = {}
    i = 0
    for feature in json_text.get("features", []):
        scene = feature.get("properties", {}).get("item_type", "Not Found")
        order_dict[scene] = order_dict.get(scene, []) + [feature.get("id", "Not Found")]
        i += 1
        print(i)
    while json_text["_links"].get("_next"):
        # print("DOING")
        new_url = json_text["_links"].get("_next") + "&_sort=acquired+desc&_page_size=250"
        json_text = _get_next_orders(session, new_url)
        for feature in json_text.get("features", []):
            if len(order_dict['PSScene4Band']) < 10:
                # print("doing")
                scene = feature.get("properties", {}).get("item_type", "Not Found")
                order_dict[scene] = order_dict.get(scene, []) + [feature.get("id", "Not Found")]
            else:
                return order_dict


def get_bulk_orders(in_file, out_folder="orders"):
    # print(API_KEY)
    session = requests.Session()
    session.auth = (API_KEY, "")
    aois = json.load(open(in_file))  # areas of interest from in file
    start_from = 0
    # print(session)
    for index, aoi in tqdm(enumerate(aois[start_from:])):
        api_input = gen_api_input(aoi["coordinates"], DATE_OF_INTEREST, BANDS_REQUIRED)
        orders = _get_orders(session, api_input)

        file_name = f"{out_folder}/{index}.json"

        # void null caputures
        if os.path.exists(out_folder):
            json.dump(orders, open(file_name, "w"))

        else:
            os.mkdir(out_folder)
            json.dump(orders, open(file_name, "w"))