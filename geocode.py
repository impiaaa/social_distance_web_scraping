from urllib.request import urlopen
from urllib.parse import quote
import json

def geocode(row):
    url = "http://localhost:4000/v1/search?size=1&boundary.gid=whosonfirst:county:102081673&layers=address&text="+quote(row['address1']+', '+row['address2'])
    result = json.load(urlopen(url))
    row = {k: v for k, v in row.items() if v}
    assert result['type'] == "FeatureCollection"
    result['features'] = [f for f in result['features'] if f['properties']['match_type'] != 'fallback']
    for f in result['features']:
        f['properties'].update(row)
    return result['features']

