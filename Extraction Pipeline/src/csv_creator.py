import csv
import os
import json

headers = [
    "event_id",
    "org_id",
    "org_name",
    "suborg_id",
    "suborg_name",
    "timestamp",
    "user_id",
    "api_key_name",
    "download_item_id",
    "download_item_type",
    "subscription_id",
    "order_reference",
    "plan_name",
    "quota_used_km2",
    "total_download_km2",
    "download_asset_type",
    "geojson_geometry"
]


def create_csv(in_folder="orders", out_csv="orders.csv"):
    with open(out_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for order in os.listdir(in_folder):
            if "aoi" in order or ".json" not in order:
                continue

            with open(os.path.join(in_folder, order)) as json_file:
                json_val = json.load(json_file)
                for key in json_val:
                    for val in json_val[key]:
                        default_dict = {key: '' for key in headers}
                        default_dict["download_item_id"] = val
                        default_dict["download_item_type"] = key
                        writer.writerow(default_dict)
