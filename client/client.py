#!/usr/bin/python3
import json
import os
import requests
from time import sleep



# debug folder for photos
folder = "photos"
uid = '123'

target_url = "http://127.0.0.1:8000/upload/"+ uid


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


res = requests.get( "{}/finish".format(target_url) )
# exit()
while  len(files)  > 0:
    sleep(1)
    res = requests.get( "{}/result".format(target_url) )
    print(res.status_code, res.text, len(files))
    try:
        info = res.json()
        name = '-'
        if len(info):
            files.remove(info["name"]) 
        print(info,  name)
    except:
        print('.')



print('Ok')