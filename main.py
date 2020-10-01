from social_distance_spider import parseCategories
from write_data_to_file import writeToFile

categories = parseCategories("https://sdp.sccgov.org")

writeToFile(categories)

