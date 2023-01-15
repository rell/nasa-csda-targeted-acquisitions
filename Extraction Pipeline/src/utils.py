def get_geojson_from_center(center, offset = 5):
    if isinstance(center, str):
        center = [float(val.strip()) for val in center.split(",")]

    x, y = 0, 0
    if isinstance(center, list) and len(center) == 2:
        x, y = center
    else:
        raise Exception("Not a valid center location ", center)
    
    return {
      "type":"Polygon",
      "coordinates":[
         [
            [
               x - offset,
               y - offset
            ],
            [
               x - offset,
               y + offset
            ],
            [
               x + offset,
               y + offset
            ],
            [
               x + offset,
               y - offset
            ],
            [
               x - offset,
               y - offset
            ]
         ]
      ]
   }

def gen_api_input(AREA_OF_INTEREST, DATE_OF_INTEREST, BANDS_REQUIRED):
    return {
        "filter": {
            "type": "AndFilter",
            "config": [{
                "type": "GeometryFilter",
                "field_name": "geometry",
                "config": get_geojson_from_center(AREA_OF_INTEREST),
            }, {
                "type": "OrFilter",
                "config": [{
                    "type": "AndFilter",
                    "config": [{
                        "type": "StringInFilter",
                        "field_name": "item_type",
                        "config": [band]
                    }]
                } for band in BANDS_REQUIRED]
            }, {
                "type": "OrFilter",
                "config": [{
                    "type": "DateRangeFilter",
                    "field_name": "acquired",
                    "config": DATE_OF_INTEREST
                }]
            }]
        },
        "item_types": ["PSScene4Band", "REOrthoTile", "SkySatCollect"]
    }
