#!/usr/bin/env python3

from fire import Fire
import datetime as dt
from notifator.version import __version__

import cv2
import requests
import os
import sys
#----------------- text config file --------
from configparser import ConfigParser
# for take_image
import subprocess as sp
from PIL import Image




def load_config( mysection, cfile="~/.notifator.rc" ):
    configur = ConfigParser()
    address = None
    ok  = False
    try:
        #print("D... config path",os.path.expanduser(cfile))
        configur.read(os.path.expanduser(cfile) )
        ok = True
    except:
        print("X... cannot read the config from file ",cfile)
    if not ok:
        sys.exit(1)

    sections=configur.sections()
    if mysection in sections:
        address = configur.get(mysection, "address")
        return address
    else:
        print("X... section not found: ", mysection)
        print("X... possible sections:", sections)
        sys.exit(0)


def take_screenshot( w=320, h=None):
    """
    gnome-screenshot
    """
    # Take the screenshot
    file_size = None
    sp.run(['gnome-screenshot', '-f', '/tmp/screenshot.png'])
    filename = None
    # Open the screenshot, resize, and save as JPG
    with Image.open('/tmp/screenshot.png') as img:
        original_width, original_height = img.size
        aspect_ratio = original_height / original_width
        h = int(w * aspect_ratio)
        img = img.convert('RGB')
        img = img.resize((w, h))
        filename=f'/tmp/screenshot_{w}_{h}.jpg'
        img.save(filename, 'JPEG')
        file_size = os.path.getsize(filename)
        print(f"i... file size = {file_size}")
    return filename



def send_ntf(message, title, section="default", scrshot=False):
    """
    send to ntfy.sh
    """

    url_full = load_config( section )
    #now = take_time()
    #title = f"{now}"
    #message = message
    #filename = None

    data = None
    filename = None
    msg2 = message
    tit2 = title

    if scrshot:
        msg2 = f""#THE message {now}"
        tit2 = message # the message will be in the title
        filename = take_screenshot(w=200)
        data=open(filename, 'rb')
        filename = filename
    else:
        data = message
        tit2 = ""
        # no message here for some reason... and title = "" to make it short
        # "Actions": "http, OpenSeznam, https://www.seznam.cz/, method=PUT, headers.Authorization=Bearer zAzsx1sk.., body={\"action\": \"close\"}"   }
    response = requests.put( url_full,
                             data=data,
                             headers={ "Title": f"{tit2}",
                                       "Filename": filename,
                                       "message": msg2,
                                       # "Actions": "http, OpenSeznam, https://www.seznam.cz/ "
                                      }
                            )

    if response.status_code == 200:
        print("Notification with image sent successfully! ntfy.sh")
    else:
        print("Failed to send notification.  ntfy.sh")
    return #message




def main():
    ad = load_config( "default" )
    print(f"i... sending to {ad}")
    send_ntf(f"test {dt.datetime.now()}", "tItLe", scrshot=False)

if __name__ == "__main__":
    Fire(main)
