#!/usr/bin/python3
import os
import requests

# debug folder for photos
folder = "photos"
target_url = "http://127.0.0.1:8000/upload/123"

def sendPhoto(photo):
    global target_url
    global folder
    file_path = os.path.join(folder,photo)
    # print(target_file) 
    target_file = open(file_path, "rb")
    res = requests.post(target_url, files = {"photo": target_file})
    print(res)

files = os.listdir(folder)
for photo in files:
    sendPhoto(photo)
