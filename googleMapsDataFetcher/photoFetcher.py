from utilities import makeRequest
import os
import pathlib
import json
import sys

try:
	f = open('placeDetails.json')
	placeDetails = json.load(f)
	f.close()
except FileNotFoundError:
	print("Run placeDetailsFetcher first")
	sys.exit(0)

apiFile = open('googleApiKey')
apiKey = apiFile.read()
apiFile.close()

def getPhoto(photoRef, photoPath):
	requestBase = "https://maps.googleapis.com/maps/api/place/photo?"
	requestQuery = "maxwidth=1600&photoreference={}&key={}".format(photoRef, apiKey)
	response = makeRequest(requestBase+requestQuery)
	print(response)
	if response.status_code == 200:
		with open(photoPath, 'wb') as f:
			f.write(response.content)
			f.close()

for placeId, place in placeDetails.items():
	placePath = os.path.join(os.getcwd(), "photos", placeId)
	pathlib.Path(placePath).mkdir(parents=True, exist_ok=True)
	if 'photos' not in place:
		continue
	for photo in place['photos']:
		photoRef = photo['photo_reference']
		# if photo not in folder
		photoPath = os.path.join(placePath, photoRef+".jpeg")
		if not os.path.exists(photoPath):
			getPhoto(photoRef, photoPath)
