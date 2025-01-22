import requests
import json


###################

# Mimicing a user querying partial matches with HUC "1805000301"
# This "partial" match is anything that BEGINS with the HUC specified.

HUC = "1805000301"
EXACT = False

###################

# Query Feature Translation Service and parse JSON response
r = requests.get("https://g6zl7z2x7j.execute-api.us-west-2.amazonaws.com/prod/huc/{}?exact={}".format(HUC, EXACT))

# Load response from FTS
response = json.loads(r.text)

# Print all elements in HUC database that partially matches with HUC 1805000301
print(json.dumps(response, indent = 4))
