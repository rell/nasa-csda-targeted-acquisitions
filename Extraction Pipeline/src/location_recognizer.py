import folium
import geopy
import json
import spacy
import pandas as pd

from folium.plugins import FastMarkerCluster
from geopy.extra.rate_limiter import RateLimiter
from tqdm import tqdm

from .sheets_csv_generation import generate_csv


class LocationExtractor:
    def __init__(
            self,
            spacy_model="",   # absolute dir location of spacy model
            in_file="output/output.json",
            out_locations="locations.json",
            out_coordinates="coordinates.json",
            html_output_file="visualizations.html",
            out_csv_file="output.csv"
    ):
        self.nlp_wk = spacy.load(spacy_model)
        self.in_file = in_file
        self.out_locations = out_locations
        self.out_coordinates = out_coordinates
        self.loc_maps = {}
        self.html_output_file = html_output_file
        self.out_csv_file = out_csv_file

    def extract_locations(self):
        try:
            with open(self.out_locations) as loc_file:
                return json.load(loc_file)
        except FileNotFoundError:
            pass

        locator = geopy.geocoders.Nominatim(user_agent="mygeocoder")
        geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

        locations = []
        loaded_json = json.load(open(self.in_file))
        for key in loaded_json:
            # print(loaded_json[key].keys())
            for article in tqdm(loaded_json[key]):
            # doc = self.nlp_wk(loaded_json[key][article]['text'])
            # TODO fix this line to extract locations
                for sentence in loaded_json[key][article]['text']:
                    doc = self.nlp_wk(sentence)
                    for ent in doc.ents:
                        # TODO only grab location if an EVENT is also found in the text
                        if ent.label_ in ["LOC"] and not self.loc_maps.get(ent.text):
                            self.loc_maps[ent.text] = True
                            #TOBE remove
                            print("Label: ", ent.label_, "Text: ", ent.text)
                            location = geocode(ent.text)
                            if location:
                                locations.append({
                                    "file": key,
                                    "url": loaded_json[key][article]['url_path'],
                                    "location": ent.text,
                                    "coordinates": list(location.point)[:2],
                                })
        #
        self.save_data(self.out_locations, locations)
        return locations

    def save_data(self, file_name, data):
        with open(file_name, "w") as loc_file:
            loc_file.write(json.dumps([item for item in data if item], indent=4))

    def save_map(self, coordinates):
        df = pd.DataFrame(coordinates, columns=["latitude", "longitude"])
        df.latitude.isnull().sum()
        df = df[pd.notnull(df["latitude"])]

        folium_map = folium.Map(
            location=[59.338315, 18.089960],
            zoom_start=2,
            tiles="CartoDB dark_matter"
        )
        FastMarkerCluster(data=list(zip(df["latitude"].values, df["longitude"].values))).add_to(folium_map)
        folium.LayerControl().add_to(folium_map)
        folium_map.save(self.html_output_file)

    def extract(self):
        locations = self.extract_locations()
        try:
            generate_csv(self.out_locations, self.out_csv_file)
        except UnicodeEncodeError:
            pass
        coordinates = [loc["coordinates"] for loc in locations]
        self.save_map(coordinates)
