from bs4 import BeautifulSoup
import requests
import json


###################

COLLECTION_ID = "C1522341104-NSIDC_ECS" # SMAP/Sentinel-1 L2 Radiometer/Radar 30-Second Scene 3 km EASE-Grid Soil Moisture V002
REGION = "California Creek-Kuskokwim River" 
EXACT = False

###################

# Query Feature Translation Service and parse JSON response
r = requests.get("https://g6zl7z2x7j.execute-api.us-west-2.amazonaws.com/prod/region/{}?exact={}".format(REGION, EXACT))

# Load response from FTS
response = json.loads(r.text)

# Obtain bounding box from response
bbox = response['results'][REGION]['Bounding Box']

# Query CMR
# --------- #

#cmr_response = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json?bounding_box={}&echo_collection_id=C1522341104-NSIDC_ECS&pretty=True".format(bbox))
cmr_response = requests.get("https://cmr.earthdata.nasa.gov/search/granules?bounding_box={}&echo_collection_id={}&pretty=True".format(bbox, COLLECTION_ID))

# --------- #

# Make it look nice
soup = BeautifulSoup(cmr_response.text, features = 'lxml')
print(soup.prettify())
