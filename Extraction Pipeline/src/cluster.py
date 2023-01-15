import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from matplotlib import pyplot as plt
from tqdm import tqdm

from .Geolocations import GeoLocation

CLUSTER_SIZE = 100


def distance(point1, point2):
    lat1, lon1, lat2, lon2 = point1[0], point1[1], point2[0], point2[1]
    p = np.pi / 180  # pi / 180
    a = (
        0.5 -
        np.cos((lat2 - lat1) * p) / 2 +
        np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    )
    # distance in KM
    return 12742 * np.arcsin(np.sqrt(a))  # 2*R*arcsin...


def find_k(coordinates):
    """
        Look at the plot obtained from this function and find the x for which y is the highest
    """

    sils = []
    low, high, step = 635, 645, 1
    for clusters in tqdm(range(low, high, step)):
        kmeans = KMeans(n_clusters=clusters).fit(coordinates)
        labels = kmeans.labels_
        sils.append(silhouette_score(coordinates, labels, metric='euclidean'))

    plt.plot(range(low, high, step), sils)
    plt.show()


def get_cluster_centers(in_file):
    coordinates = json.load(open(in_file))
    coordinates = [
        [c[0], c[1]]
        for c in coordinates if c
    ]

    # find_k(coordinates)
    # number 643 obtained from find_k by iteratively looking for range
    # 2, 5000, 1000
    # 500, 1500, 100
    # 600, 800, 25
    # 625, 645, 1
    kmeans = KMeans(n_clusters=643).fit(coordinates)
    return kmeans.cluster_centers_.tolist()


def get_bbox(coordinate, distance=100):
    location = GeoLocation.from_degrees(coordinate[0], coordinate[1])
    SW, NE = location.bounding_locations(distance)

    return {
        "type": "Polygon",
        "coordinates": [
            [
                [SW.deg_lat, SW.deg_lon],
                [NE.deg_lat, SW.deg_lon],
                [NE.deg_lat, NE.deg_lon],
                [SW.deg_lat, NE.deg_lon],
                [SW.deg_lat, SW.deg_lon]
            ]
        ]
    }


# TODO: if the data point is isolated, we only want 5-10 sq. km range from the data
def get_bboxes(in_file):
    centers = get_cluster_centers(in_file)
    return [get_bbox(item) for item in centers]


# get_bboxes("coordinates")
