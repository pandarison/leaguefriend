# -*- coding: utf-8 -*-
# @Author: caspar
# @Date:   2018-07-27 14:23:36
# @Last Modified by:   caspar
# @Last Modified time: 2018-08-01 17:09:27

from Quartz import CoreGraphics
import Quartz
from PIL import Image
import pyocr
import pyocr.builders
import tempfile
import LaunchServices
import requests
import io
import json
import math

import monitor
exit(0)

__LEGAL_CHARS_EUW = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzªµºÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿĄąĆćĘęıŁłŃńŒœŚśŠšŸŹźŻżŽžƒˆˇˉμﬁﬂ"


def ocr_space_file(filename, overlay=False, api_key='420c01445b88957', language='eng'):
    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               'scale':True
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()

def getWindowInfo():
    windows = CoreGraphics.CGWindowListCopyWindowInfo(CoreGraphics.kCGWindowListOptionAll, CoreGraphics.kCGNullWindowID)
    window_lol = None

    for x in windows:
        if 'kCGWindowOwnerName' in x:
            if x['kCGWindowOwnerName'] == 'League of Legends'  and x['kCGWindowSharingState'] == 0:
                window_lol = x
                break

    if window_lol is None:
        print("Cannot find League of Legends window.")
    return window_lol

def getImageFromWindowInfo(wInfo):
    
    window_img = CoreGraphics.CGWindowListCreateImageFromArray(CoreGraphics.CGRectNull, (wInfo['kCGWindowNumber'],), CoreGraphics.kCGWindowImageBestResolution)
    # create temp file
    f = tempfile.NamedTemporaryFile(mode='w', delete=True)
    url = CoreGraphics.NSURL.fileURLWithPath_(f.name)
    destination = Quartz.CGImageDestinationCreateWithURL(url, LaunchServices.kUTTypePNG, 1, None)
    Quartz.CGImageDestinationAddImage(destination, window_img, None)
    Quartz.CGImageDestinationFinalize(destination)
    f.flush()
    f.seek(0)
    img = Image.open(f.name)
    
    #img = Image.open('/Users/caspar/Downloads/11.png')
    f.close()
    return img

def getPlayer(img, side, screen):
    screen_width, screen_height = screen

    left_scale = 80/1280.0
    left = screen_width*left_scale

    width_scale = 175/1280.0
    width = screen_width*width_scale

    height_scale = 80/720.0
    height = screen_height*height_scale

    top_scale = 95/720.0
    top = screen_height*top_scale

    if side == 'left':
        return img.crop((left, top, left+width, top+height*(5)))
    else:
        return img.crop((screen_width-left-width, top, screen_width-left, top+height*(5)))

def filterName(name):
    name = list(name)
    name = filter(lambda x: x in __LEGAL_CHARS_EUW, name)
    name = list(name)
    return "".join(name)

def removeTagName(img):
    # 195 167 89
    pixels = img.load()
    distance1 = lambda x,y,z: abs(x-195) + abs(y-167) + abs(z-89)
    distance2 = lambda x,y,z: abs(x-149) + abs(y-127) + abs(z-69)
    distance3 = lambda x,y,z: abs(x-168) + abs(y-145) + abs(z-79)
    distance4 = lambda x,y,z: abs(x-86) + abs(y-79) + abs(z-45)
    distance5 = lambda x,y,z: abs(x-112) + abs(y-97) + abs(z-55)

    for w in range(img.width):
        for h in range(img.height):
            r,g,b,a = img.getpixel((w,h))
            if distance1(r,g,b) < 30 or distance2(r,g,b) < 30 or distance3(r,g,b) < 30 or distance4(r,g,b) < 30 or distance5(r,g,b) < 30:
                pixels[w,h] = (0,0,0,255)
    return img

# get window 
print("Detecting League of Legends.")
window = getWindowInfo()
#if window is None:
#    exit(0)

# get image of window
print("Analysing images.")
img = getImageFromWindowInfo(window)
#img.show()


# crop the image
player = getPlayer(img, "left", (1280,720))
player = removeTagName(player)
#player.show()


#https://porofessor.gg/pregame/euw/Gésucritto,AgustiPlanas,SonamisFortune,Averatus,Naiehered,

# call OCR API
print("Finding player names.")
player_img_file = tempfile.NamedTemporaryFile(mode='w', delete=True, suffix=".png")
player.save(player_img_file.name, format="png", quality=100)
result = json.loads(ocr_space_file(player_img_file.name))
player_img_file.close()

POSITIONS = ['TOP', 'JUNGLE', 'MID', 'BOTTOM', 'SUPPORT']

result = result['ParsedResults'][0]['ParsedText'].split("\r\n")
result = list(filter(lambda x: len(x)>1, result))
result = list(map(lambda x: x.strip() ,result))

print("Opening stats website.")
url = 'https://porofessor.gg/pregame/euw/'
for i in range(len(result)):
    x = result[i]
    if x in POSITIONS:
        url = url + filterName(result[i+1]) + ','

#print(url)
import os
os.system("open \"" + url + "\"")


