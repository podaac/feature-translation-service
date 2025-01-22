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

geo_list = response['results'][SWOT_FEATURE_ID]
#print(geo_list)

# Query CMR
# --------- #

#cmr_response = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json?{}&echo_collection_id=C1522341104-NSIDC_ECS&pretty=True".format(polygon))
cmr_response = requests.get("https://cmr.earthdata.nasa.gov/search/granules?{}&echo_collection_id={}&pretty=True".format(geo_list, COLLECTION_ID))

# --------- #

# Make it look nice
soup = BeautifulSoup(cmr_response.text, features = 'lxml')
print(soup.prettify())
