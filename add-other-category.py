import sys, json, tempfile, os
from fieldnames import *
from urllib.request import Request, urlopen
from urllib.error import URLError
from base64 import b64decode
from time import sleep

infile = open(sys.argv[1])
infilepath, infilenameext = os.path.split(sys.argv[1])
infilename, infileext = os.path.splitext(infilenameext)
outfile = tempfile.NamedTemporaryFile(prefix=infilename, suffix=infileext, dir=infilepath, mode='w', delete=False)

for i, line in enumerate(infile):
    j = json.loads(line)
    assert j["type"] == "FeatureCollection"
    
    props = j["features"][0]["properties"]
    if props[CATEGORY] != "Other, please specify":
        continue
    
    print("Feature", i, props[NAME1], end=' ')
    
    for key, val in set(props.items()):
        if val is None:
            del props[key]
    
    for i in range(5):
        try:
            doc = urlopen(Request(props[PDF], method="HEAD"))
        except URLError:
            if i == 4:
                raise
            else:
                sleep(1)
                continue
        break
    props[CATEGORY] = b64decode(doc.getheader("x-ms-meta-typeofbusinessother")).decode('utf-8')
    
    print("is", props[CATEGORY])
    
    outfile.write(json.dumps(j)+'\n')

infile.close()
outfile.close()
os.replace(outfile.name, sys.argv[1])

