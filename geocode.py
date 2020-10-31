from urllib.request import urlopen
from urllib.parse import quote
import urllib.error
import json, re

unitTypes = [re.compile(r'(\W)('+part+r')(\W+.*)', flags=re.IGNORECASE) 
             for line in open("unit_types_numbered.txt")
             for part in line.rstrip().split('|')]
unitTypes.extend([re.compile(r'(\W)('+part+r')((\W|\d).*)', flags=re.IGNORECASE) 
                  for line in open("number.txt")
                  for part in line.rstrip().split('|')])
unitTypes.sort(key=lambda part: len(part.pattern), reverse=True)

def load(path, bounded=True):
    url = "http://localhost:4000/v1/"+path+"&size=1"
    # First try within the county
    if bounded:
        url += "&boundary.gid=whosonfirst:county:102081673"
    
    for i in range(5):
        try:
            result = json.load(urlopen(url))
        except urllib.error.URLError as e:
            print(e)
            continue
        break
    assert result['type'] == "FeatureCollection"
    
    # Interpolation is fine, "fallback" (i.e., street or city centroid) is not.
    result['features'] = [f for f in result['features'] if f['properties']['match_type'] != 'fallback']
    
    if len(result['features']) == 0 and bounded:
        # If it wasn't found in the county, try outside
        return load(path, False)
    else:
        return result

def geocodeTest():
    try:
        load("search?text=Santa%20Clara%20County")
    except urllib.error.URLError:
        print("A test request to the local Pelias server did not succeed. "
              "It may not be operating properly.")
        raise

scannedGeocodedLocations = set()

def geocode(row):
    row = {k: v for k, v in row.items() if v}
    i = row['address2'].rfind(' ')
    zipcode = row['address2'][i+1:]
    i = row['address2'].rfind(' ', 0, i-1)
    city = row['address2'][:i]
    addr = row['address1']
    
    # first try strict search
    result = load("search/structured?address="+quote(addr)+"&locality="+quote(city)+"&postalcode="+quote(zipcode))
    
    if len(result['features']) == 0:
        # let libpostal have a try
        result = load("search?text="+quote(addr+", "+row['address2']))
    
    if len(result['features']) == 0:
        # the most common failure case seems to be misdetected unit prefix,
        # so try changing that out
        for unitType in unitTypes:
            if unitType.search(addr):
                for replacement in "number", "unit", "suite":
                    result = load("search?text="+quote(unitType.sub(r'\1'+replacement+r' \3', addr)+", "+row['address2']))
                    if len(result['features']) != 0:
                        break
                if len(result['features']) != 0:
                    break

    if len(result['features']) == 0:
        # now just strip the unit
        for unitType in unitTypes:
            if unitType.search(addr):
                result = load("search?text="+quote(unitType.sub(r'\1', addr)+", "+row['address2']))
                if len(result['features']) != 0:
                    break

    if len(result['features']) == 0:
        open("missed.log", 'a').write(row['address1']+'\t'+row['address2']+'\n')

    for geocoded in result['features']:
        geoLocTuple = (row['name1'], row.get('name2', None), tuple(geocoded['geometry']['coordinates']))
        if geoLocTuple in scannedGeocodedLocations:
            continue
        scannedGeocodedLocations.add(geoLocTuple)

        # Remove confusing/unnecessary fields
        if 'id' in geocoded['properties']: del geocoded['properties']['id']
        if 'name' in geocoded['properties']: del geocoded['properties']['name']
        if 'country_gid' in geocoded['properties']: del geocoded['properties']['country_gid']
        if 'region_gid' in geocoded['properties']: del geocoded['properties']['region_gid']
        if 'county_gid' in geocoded['properties']: del geocoded['properties']['county_gid']
        if 'locality_gid' in geocoded['properties']: del geocoded['properties']['locality_gid']
        if 'neighbourhood_gid' in geocoded['properties']: del geocoded['properties']['neighbourhood_gid']
        if 'postalcode_gid' in geocoded['properties']: del geocoded['properties']['postalcode_gid']
        
        geocoded['properties'].update(row)
        
        if geocoded['properties']['source'] == "openstreetmap":
            geocoded['properties']['osm_id'] = geocoded['properties']['source_id']
        
        open("socialdistance.geojsonl", 'a').write(json.dumps(geocoded)+'\n')

def geocodeWorker(q):
    while True:
        geocode(q.get())
        q.task_done()

