import requests
import json


###################

# Mimicing a user querying exact matches with HUC "180500030105"

HUC = "180500030105"
EXACT = True

###################

# Query Feature Translation Service and parse JSON response
r = requests.get("https://g6zl7z2x7j.execute-api.us-west-2.amazonaws.com/prod/huc/{}?exact={}".format(HUC, EXACT))

# Load response from FTS
response = json.loads(r.text)

# Print all elements in HUC database that exactly match HUC "180500030105"
print(json.dumps(response, indent = 4))
