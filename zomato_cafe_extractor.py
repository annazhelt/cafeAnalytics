#from requests import Session, Request
import os
import json
import requests
import urllib
from bs4 import BeautifulSoup

DB_PATH = './data/data_{}.json'

def save_image(photo_path, photo_id, photo_uri):
    """
    retrieve a photo from the uri and save it to the path
    """
    if not os.path.isfile(photo_path):
        print("Writing image: " + photo_id)
        try:
            urllib.request.urlretrieve(photo_uri, photo_path)
        except:
            print("Error accessing image: " + photo_id)

def save_images_from_dict(photo_db):
    """
    given a photos list, create directories for the cafes,
    and retrieve and save all the listed photos
    """
    for cafe in photo_db:
        cafe_path = "./data/" + cafe['cafe_name']
        if not os.path.isdir(cafe_path):
            os.mkdir(cafe_path)
        print("Images for: " + cafe['cafe_name'])
        for photo in cafe['photos']:
            photo_path = cafe_path + '/' + photo['photo_id'] + '.jpeg'
            save_image(photo_path, photo['photo_id'], photo['uri'])

def create_image_dict(page_num):
    """
    Creates a list in the form of for one specific page:
        [
             {
                cafe_name: <string>,
                main_ref: <url>,
                photos: [
                    {
                        photo_id: <string>
                        photo_ref: <url>
                        uri: <uri>
                    }
                ]
             }
        ]
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    response = requests.get("https://www.zomato.com/vancouver/caf%C3%A9?page={}".format(page_num), headers=headers)
    html = response.text

    num_requests = 0
    num_photos = 0
    photo_db = []
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and link.get('data-result-type') == 'ResCard_Name':
            cafe_name = link.get('title')
            photo_db.append({ 'cafe_name': cafe_name, 'main_ref': href, 'photos': []})
    print(photo_db)
    num_requests += len(photo_db)

    for cafe in photo_db:
        #request only photos that have ambience tag
        response = requests.get(cafe['main_ref'] + "/photos?category=ambience", headers=headers)
        html = response.text

        photo_links = {}
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            photo_id = link.get('data-photo_id')
            if href and photo_id:
                cafe['photos'].append({'photo_id': photo_id, 'photo_ref': href})
        print(cafe)
        num_requests += len(cafe['photos'])
        num_photos += len(cafe['photos'])

    for cafe in photo_db:
        for photo in cafe['photos']:
            response = requests.get(photo['photo_ref'], headers=headers)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('meta'):
                property = link.get('property')
                if property:
                    if property == "og:image":
                        num_photos -= 1
                        num_requests +=1
                        print("Retrieving images: " + str(num_photos) + " images left...")
                        uri = link.get('content').split('?')[0]
                        photo['uri'] = uri

    print("Total number of requests made: " + str(num_requests))
    return photo_db

def image_fetcher(page_num):
    """
    fetches data for a single page with page_num
    """
    if not os.path.isfile(DB_PATH.format(str(page_num))):
        photo_db = create_image_dict(page_num)
        with open(DB_PATH.format(str(page_num)), 'w') as outfile:
            json.dump(photo_db, outfile)
    else:
        with open(DB_PATH.format(str(page_num))) as f:
            photo_db = json.load(f)

    save_images_from_dict(photo_db)

data_path = "./data"
if not os.path.isdir(data_path):
    os.mkdir(data_path)
for index in range(1,49):
    image_fetcher(index)
