from bs4 import BeautifulSoup
import requests
import json

###################

COLLECTION_ID = "C1522341104-NSIDC_ECS" # SMAP/Sentinel-1 L2 Radiometer/Radar 30-Second Scene 3 km EASE-Grid Soil Moisture V002
REGION = "California Creek-Kuskokwim River"
EXACT = True

###################

# Query Feature Translation Service and parse JSON response
r = requests.get("https://g6zl7z2x7j.execute-api.us-west-2.amazonaws.com/prod/region/{}?exact={}".format(REGION, EXACT))

# Load response from FTS
response = json.loads(r.text)

# Obtain convex hull polygon from response
polygon = response['results'][REGION]['Convex Hull Polygon']
#polygon = response['results'][REGION]['Visvalingam Polygon']

# Query CMR
# --------- #

#cmr_response = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json?polygon={}&echo_collection_id=C1522341104-NSIDC_ECS&pretty=True".format(polygon))
cmr_response = requests.get("https://cmr.earthdata.nasa.gov/search/granules?polygon={}&echo_collection_id={}&pretty=True".format(polygon, COLLECTION_ID))

# --------- #

# Make it look nice
soup = BeautifulSoup(cmr_response.text, features = 'lxml')
print(soup.prettify())
