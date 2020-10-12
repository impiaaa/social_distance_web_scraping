from social_distance_spider import parseMain, parseLocations
from geocode import geocode
import json

session, urlFormat, maxPages = parseMain("https://sdp.sccgov.org")
locations = []
for i in range(maxPages+1):
    print("Scraping page", i)
    link = urlFormat.format(i)
    for location in parseLocations(session, link):
        if location['address1'] != "No physical address":
            locations.extend(geocode(location))
json.dump({"type": "FeatureCollection", "features": locations}, open("socialdistance.geojson", 'w'))

