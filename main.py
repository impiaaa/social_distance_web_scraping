from social_distance_spider import parseMain, parseLocations
from geocode import geocodeWorker, geocodeTest
import threading, queue, json
from fieldnames import *

NTHREADS = 1

geocodeTest()
geocodeQueue = queue.Queue(maxsize=NTHREADS*2)
session, urlFormat, maxPages = parseMain("https://sdp.sccgov.org")
scannedLocations = set()

try:
    previouslyScannedIds = {json.loads(line)['properties']['id'] for line in open("socialdistance.geojsonl")}
except FileNotFoundError:
    previouslyScannedIds = set()

threads = [threading.Thread(target=geocodeWorker, daemon=True, args=[geocodeQueue]) for i in range(NTHREADS)]
for thread in threads:
    thread.start()

for i in range(maxPages+1):
    print("Scraping page", i+1, "of", maxPages)
    link = urlFormat.format(i)
    for location in parseLocations(session, link):
        if location[ADDR1] == "No physical address":
            continue
        if location['id'] in previouslyScannedIds:
            break
        
        # Site is sorted newest first, so discard any later duplicate entries
        locTuple = (location[NAME1], location.get(NAME2, None), location[ADDR1], location[ADDR2])
        if locTuple in scannedLocations:
            continue
        scannedLocations.add(locTuple)
        
        geocodeQueue.put(location)
    
    if location['id'] in previouslyScannedIds:
        break
    
geocodeQueue.join()

