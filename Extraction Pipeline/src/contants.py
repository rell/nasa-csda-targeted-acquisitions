import os
from dotenv import load_dotenv

# TODO transfer all constants to config.ini

API_KEY = "" # set api key to personal api in planet vendor settings
URL = "https://api.planet.com/data/v1/quick-search?_sort=acquired+desc&_page_size=250"
ORDER_URL = "https://api.planet.com/compute/ops/orders/v2"
# URL = "https://api.planet.com/data/v1"


BANDS_REQUIRED = [
    "PSScene4Band",
    "REOrthoTile",
    # "SkySatCollect"
    "REScene",
    "PSScene3Band",
    "PSOrthoTile",
]

DATE_OF_INTEREST = {
    "gte": "2020-01-01T00:00:00.000Z",
    "lte": "2021-08-27T23:59:59.999Z"
}

# AREA_OF_INTEREST = {
#     "type": "Polygon",
#     "coordinates": [
#         [
#             [-86.656967, 34.699937],
#             [-86.518192, 34.699937],
#             [-86.518192, 34.773153],
#             [-86.656967, 34.773153],
#             [-86.656967, 34.699937]
#         ]
#     ]
# }

API_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}
