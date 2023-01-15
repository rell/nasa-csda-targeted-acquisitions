from http.client import CONFLICT
import json
import csv

headers = ["filename", "Include?", "Request 2nd Review", "location", "coordinates", "is_isolated_point", "is_episotic (default true)", "default_filter", "Date Range (start;end) [01/01/2015; 09/30/2021]", "url", "EVENT CATEGORY", "NOTES"]

def generate_csv(infile="locations.json", outfile="output.csv"):
    obj = json.load(open(infile))
    writer = csv.writer(open(outfile, "w"))
    writer.writerow(headers)

    for item in obj:
        """
            "file": "Water Watchers",
            "url": "https://earthobservatory.nasa.gov/Features/WaterWatchers/",
            "location": "Mr",
            "coordinates": [
                20.2540382,
                -9.2399263
            ]
        """
        writer.writerow([
            item["file"],
            "",
            "",
            item["location"],
            item["coordinates"],
            "",
            "",
            "",
            "",
            item["url"],
            "",
            ""
        ])
