from urllib.request import urlopen
from urllib.parse import quote
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
    if bounded: url += "&boundary.gid=whosonfirst:county:102081673"
    #print(url)
    result = json.load(urlopen(url))
    assert result['type'] == "FeatureCollection"
    # Interpolation is fine, "fallback" (i.e., street or city centroid) is not.
    result['features'] = [f for f in result['features'] if f['properties']['match_type'] != 'fallback']
    if len(result['features']) == 0 and bounded: return load(path, False)
    return result

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
                for replacement in "number", "suite", "unit":
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

    for f in result['features']:
        f['properties'].update(row)
    return result['features']

