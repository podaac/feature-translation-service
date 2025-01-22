import requests
import json


###################

# Mimicing a user querying partial matches with California

REGION = "California"

###################

# Query Feature Translation Service and parse JSON response
r = requests.get("https://g6zl7z2x7j.execute-api.us-west-2.amazonaws.com/prod/region/{}".format(REGION))

# Example query from above is:
# https://g6zl7z2x7j.execute-api.us-west-2.amazonaws.com/prod/region/California

# Load response from FTS
response = json.loads(r.text)

# Print all elements in HUC database that partially match California
print(response['results'].keys())
