from social_distance_spider import parseMain, parseLocations
from geocode import geocodeWorker, geocodeTest
import threading, queue

NTHREADS = 8

geocodeTest()
geocodeQueue = queue.Queue(maxsize=NTHREADS)
session, urlFormat, maxPages = parseMain("https://sdp.sccgov.org")
scannedLocations = set()
open("socialdistance.geojsonl", 'w') # clear output file
threads = [threading.Thread(target=geocodeWorker, daemon=True, args=[geocodeQueue]) for i in range(NTHREADS)]
for thread in threads:
    thread.start()

for i in range(maxPages+1):
    print("Scraping page", i+1, "of", maxPages)
    link = urlFormat.format(i)
    for location in parseLocations(session, link):
        if location['address1'] == "No physical address":
            continue
        
        # Site is sorted newest first, so discard any later duplicate entries
        locTuple = (location['name1'], location.get('name2', None), location['address1'], location['address2'])
        if locTuple in scannedLocations:
            continue
        scannedLocations.add(locTuple)
        
        geocodeQueue.put(location)
    
    for thread in threads:
        if not thread.is_alive():
            # these threads never exit normally, so it must have been an exception
            quit(1)

geocodeQueue.join()

