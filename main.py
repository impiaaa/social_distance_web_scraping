from social_distance_spider import parseMain, parseLocations
from write_data_to_file import writeToFile

session, urlFormat, maxPages = parseMain("https://sdp.sccgov.org")
locations = []
for i in range(maxPages+1):
    print("Scraping page", i)
    link = urlFormat.format(i)
    locations.extend(parseLocations(session, link))
writeToFile(locations)

