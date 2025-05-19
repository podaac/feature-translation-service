import requests
import json


###################

# Mimicing a user querying exact matches with region "Woods Creek-Skykomish River"

REGION = "Woods Creek-Skykomish River"
EXACT = True

###################

# Query Feature Translation Service and parse JSON response
# Note the change in endpoint from "/prod/huc" to "/prod/region"
r = requests.get("https://g6zl7z2x7j.execute-api.us-west-2.amazonaws.com/prod/region/{}?exact={}".format(REGION, EXACT))

# Load response from FTS
response = json.loads(r.text)

# Print all elements in HUC database that exact matches with region "Woods Creek-Skykomish River"
print(json.dumps(response, indent = 4))
