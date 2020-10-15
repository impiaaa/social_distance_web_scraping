from social_distance_spider import parseMain, parseLocations
from geocode import geocode
import json

session, urlFormat, maxPages = parseMain("https://sdp.sccgov.org")
output = open("socialdistance.geojsonl", 'w')
scannedLocations = set()
scannedGeocodedLocations = set()

for i in range(maxPages+1):
    print("Scraping page", i+1, "of", maxPages)
    link = urlFormat.format(i)
    for location in parseLocations(session, link):
        if location['address1'] == "No physical address":
            continue
        
        # Site is sorted newest first, so discard any later duplicate entries
        locTuple = (location['name1'], location.get('name2', None), location['address1'], location['address2'])
        if locTuple in scannedLocations:
            #print("Skipping", locTuple)
            continue
        scannedLocations.add(locTuple)
        
        results = geocode(location)
        if len(results) == 0:
            print("Could not locate", location['address1']+', '+location['address2'])
        
        for geocoded in results:
            geoLocTuple = (geocoded['properties']['name1'], geocoded['properties'].get('name2', None), tuple(geocoded['geometry']['coordinates']))
            if geoLocTuple in scannedGeocodedLocations:
                #print("Skipping", geoLocTuple)
                continue
            scannedGeocodedLocations.add(geoLocTuple)
            
            json.dump(geocoded, output)
            output.write('\n')
        
    output.flush()

output.close()

