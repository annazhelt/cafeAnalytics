from utilities import makeRequest
import json
import sys

try:
	f = open('restaurantData.json')
	restaurantData = json.load(f)
	f.close()
except FileNotFoundError:
	print("Run restaurantFethcer first")
	sys.exit(0)

try:
	f = open('placeDetails.json')
	placeDetails = json.load(f)
	f.close()
except FileNotFoundError:
	placeDetails = {}

apiFile = open('googleApiKey')
apiKey = apiFile.read()
apiFile.close()

for placeId in restaurantData:
	if placeId not in placeDetails:
		requestBase = "https://maps.googleapis.com/maps/api/place/details/json?"
		requestQuery = "placeid={}&fields=photo&key={}".format(placeId, apiKey)
		response = makeRequest(requestBase+requestQuery)
		content = json.loads(response.text)
		placeDetails[placeId] = content['result']

f = open('placeDetails.json', 'w')
json.dump(placeDetails, f)
f.close()