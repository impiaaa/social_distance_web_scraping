from urllib.request import urlopen
from urllib.parse import quote
import urllib.error
import json, re
from fieldnames import *

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
    
    result = None
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
    except Exception:
        print("A test request to the local Pelias server did not succeed. "
              "It may not be operating properly.")
        raise

scannedGeocodedLocations = set()

def geocode(row):
    row = {k: v for k, v in row.items() if v}
    addr = row[ADDR1]
    addr2 = row[ADDR2]
    
    i = addr2.rfind(' CA ')
    if i == -1:
        result = {'features': []}
    else:
        # first try strict search
        zipcode = addr2[i+4:]
        city = addr2[:i]
        result = load("search/structured?address="+quote(addr)+"&locality="+quote(city)+"&postalcode="+quote(zipcode))
    
    if len(result['features']) == 0:
        # let libpostal have a try
        result = load("search?text="+quote(addr+", "+addr2))
    
    if len(result['features']) == 0:
        # the most common failure case seems to be misdetected unit prefix,
        # so try changing that out
        for unitType in unitTypes:
            if unitType.search(addr):
                for replacement in "number", "unit", "suite":
                    result = load("search?text="+quote(unitType.sub(r'\1'+replacement+r' \3', addr)+", "+addr2))
                    if len(result['features']) != 0:
                        break
                if len(result['features']) != 0:
                    break

    if len(result['features']) == 0:
        # now just strip the unit
        for unitType in unitTypes:
            if unitType.search(addr):
                result = load("search?text="+quote(unitType.sub(r'\1', addr)+", "+addr2))
                if len(result['features']) != 0:
                    break

    if len(result['features']) == 0:
        # no luck
        open("missed.log", 'a').write(addr+'\t'+addr2+'\n')

    for geocoded in result['features']:
        geoLocTuple = (row[NAME1], row.get(NAME2, None), tuple(geocoded['geometry']['coordinates']))
        if geoLocTuple in scannedGeocodedLocations:
            continue
        scannedGeocodedLocations.add(geoLocTuple)
        
        if 'housenumber'   in geocoded['properties']: row['House number (detected)']  = geocoded['properties']['housenumber']
        if 'street'        in geocoded['properties']: row['Street name (detected)']   = geocoded['properties']['street']
        if 'neighbourhood' in geocoded['properties']: row['Neighbourhood (detected)'] = geocoded['properties']['neighbourhood']
        if 'locality'      in geocoded['properties']: row['City (detected)']          = geocoded['properties']['locality']
        if 'postalcode'    in geocoded['properties']: row['Zip code (detected)']      = geocoded['properties']['postalcode']
        
        if 'addendum' in geocoded['properties'] and 'scc' in geocoded['properties']['addendum']:
            row.update(geocoded['properties']['addendum']['scc'])

        if 'gid' in geocoded['properties']: row['gid'] = geocoded['properties']['gid']
        
        if geocoded['properties']['source'] == "openstreetmap":
            row['osm_id'] = geocoded['properties']['source_id']
        
        geocoded['properties'] = row

        open("socialdistance.geojsonl", 'a').write(json.dumps(geocoded)+'\n')

def geocodeWorker(q):
    while True:
        geocode(q.get())
        q.task_done()

