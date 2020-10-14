from social_distance_spider import parseMain, parseLocations
from geocode import geocode
import json

session, urlFormat, maxPages = parseMain("https://sdp.sccgov.org")
output = open("socialdistance.geojsonl", 'w')
for i in range(maxPages+1):
    print("Scraping page", i+1)
    link = urlFormat.format(i)
    for location in parseLocations(session, link):
        if location['address1'] != "No physical address":
            results = geocode(location)
            if len(results) == 0:
                print("Could not locate", location['address1']+', '+location['address2'])
            for geocoded in results:
                json.dump(geocoded, output)
                output.write('\n')
    output.flush()
output.close()

