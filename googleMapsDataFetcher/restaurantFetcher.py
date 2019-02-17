from utilities import makeRequest
import json
import numpy as np

def parseResults(results):
	print("Found {} results".format(len(results)))
	for result in results:
		resultPlaceId = result['place_id']
		if resultPlaceId not in restaurantData:
			restaurantData[resultPlaceId] = result

def constructNearbySearchQuery(lat,long):
	searchRadius = 500
	searchType = "cafe"
	requestBase = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
	requestQuery = "location={},{}&radius={}&type={}&key={}".format(lat,long, searchRadius, searchType,apiKey)
	return requestBase+requestQuery

def constructPageTokenQuery(pageToken):
	requestQuery = "pagetoken={}&key={}".format(pageToken, apiKey)
	requestBase = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
	return requestBase+requestQuery

def parseResponse(response):
	content = json.loads(response.text)
	results = content['results']
	parseResults(results)
	if 'next_page_token' not in content:
		return None
	else: 
		return content['next_page_token']

def addNearbyRestaurantsToData(lat, lon):
	print("searching {},{}".format(lat, lon))
	response = makeRequest(constructNearbySearchQuery(lat,lon))
	pageToken = parseResponse(response)

	while pageToken is not None:
		response = requests.get(constructPageTokenQuery(pageToken), headers=headers)
		pageToken = parseResponse(response)

try:
	f = open('restaurantData.json')
	restaurantData = json.load(f)
	f.close()
except FileNotFoundError:
	restaurantData = {}


apiFile = open('googleApiKey')
apiKey = apiFile.read()
apiFile.close()

vancouverLat = 49.2827
vancouverLong = -123.1207

step = 10

latNorthBoundary = 49.3043
latSouthBoundary = 49.2107
lats = np.linspace(latSouthBoundary, latNorthBoundary, step)

longWestBoundary = -123.2460
longEastBoundary = -123.1153
lons = np.linspace(longWestBoundary, longEastBoundary, step)

for lat in lats:
	for lon in lons:
		addNearbyRestaurantsToData(lat, lon)

print("found {} restaurants".format(len(restaurantData)))
f = open('restaurantData.json', 'w')
json.dump(restaurantData, f)
f.close()

