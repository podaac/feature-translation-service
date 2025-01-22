from bs4 import BeautifulSoup
import requests
import json


###################

# Mimicing a user querying exact matches with SWOT Feature ID "75411400010000"

COLLECTION_ID = "C1522341104-NSIDC_ECS" # SMAP/Sentinel-1 L2 Radiometer/Radar 30-Second Scene 3 km EASE-Grid Soil Moisture V002
SWOT_FEATURE_ID = "75411400010000"
EXACT = False

###################

# Query Feature Translation Service and parse JSON response
r = requests.get("https://g6zl7z2x7j.execute-api.us-west-2.amazonaws.com/prod/swot/{}?exact={}".format(SWOT_FEATURE_ID, EXACT))

# Load response from FTS
response = json.loads(r.text)
json_response = response['results'][SWOT_FEATURE_ID]
#print(json_response)

# Query CMR
# --------- #

#cmr_response = requests.post("https://cmr.earthdata.nasa.gov/search/granules?echo_collection_id={}&pretty=True".format(COLLECTION_ID), data = json_response)
cmr_response = requests.post("https://cmr.earthdata.nasa.gov/search/granules?echo_collection_id={}&pretty=True".format(COLLECTION_ID), data = json_response)

# --------- #

# Make it look nice
soup = BeautifulSoup(cmr_response.text, features = 'lxml')
print(soup.prettify())
