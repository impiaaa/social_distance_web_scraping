from social_distance_spider import parseMain, parseLocations
from geocode import geocode
import json

session, urlFormat, maxPages = parseMain("https://sdp.sccgov.org")
output = open("socialdistance.geojsonl", 'w')
for i in range(maxPages+1):
    print("Scraping page", i)
    link = urlFormat.format(i)
    for location in parseLocations(session, link):
        if location['address1'] != "No physical address":
            for geocoded in geocode(location):
                json.dump(geocoded, output)
                output.write('\n')
    output.flush()
output.close()

