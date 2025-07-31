#!/usr/bin/python3

from fire import Fire
from gtts import gTTS
import datetime as dt
from pydub import AudioSegment
import glob
import os

ONAME = "tmp.mp3"


def gspeak3( s ):
    """
    ... should also  put mp3  into cache in future
    """
    print(f"i... {s}  ... {ONAME}")
    #tts = gTTS('14:31', lang='cs')
    tts = gTTS( s, lang='cs')
    tts.save( ONAME )
    # Load the saved file with pydub
    sound = AudioSegment.from_file( ONAME )
    print("# Increase the volume")
    louder_sound = sound + 10  # Increase volume by 10 dB
    # Save the result
    louder_sound.export( ONAME, format='mp3')
    return ONAME



def get_mp3(h,m,dirname="~/sound_cache/"):
    """
    preferably get from cache
    """
    DD =  os.path.expanduser(dirname)
    li=sorted( glob.glob( DD+"/*mp3" ) )
    nam = f"{h:02d}_{m:02d}.mp3"
    nam = f"{DD}/{nam}"
    nam = nam.replace("//","/")
    print("i...  searching",nam)
    if nam in li:
        print("i... FOUND")
        return nam
    else:
        #print(li)
        return None


def hodiny( h=None,m=None):
    """

    """
    print("D... really hodiny")
    if h is None or m is None:
        i = int( dt.datetime.now().strftime("%H") )
        j = int( dt.datetime.now().strftime("%M") )
    else:
        i= int(h)
        j= int(m)

    FNAME = get_mp3(i,j)
    print("D... really hodiny FNAME:", FNAME)

    if FNAME is not None:
        print(f"i... file exists: {FNAME}  . saving {ONAME}")
        sound = AudioSegment.from_file( FNAME )
        sound.export( ONAME, format='mp3')
        print("D... returning (old) filename : ", ONAME)
        return ONAME

    print(f"{i} : {j}")

    H1="hodina"
    H2="hodiny"
    H3="hodin"
    M1="minuta"
    M2="minuty"
    M3="minut"

    #for i in range(24):
    ho=""
    if i == 0:  ho = ho + f"{i} {H3}"
    if i == 1:  ho = ho + f"{i} {H1}"
    if i == 2:  ho = ho + f"{i} {H2}"
    if i == 3:  ho = ho + f"{i} {H2}"
    if i == 4:  ho = ho + f"{i} {H2}"
    if i > 4:   ho = ho + f"{i} {H3}"

    #for i in range(60):
    if j == 0: ho = ho +  f" {j} {M3}"
    if j == 1: ho = ho +  f" {j} {M1}"
    if j == 2: ho = ho +  f" {j} {M2}"
    if j == 3: ho = ho +  f" {j} {M2}"
    if j == 4: ho = ho +  f" {j} {M2}"
    if j > 4:  ho = ho +  f" {j} {M3}"

    mp3file = gspeak3( ho ) # just save mp3
    print("D... returning (new) filename : ", mp3file)
    return mp3file

#       mv masnun.wav  ${i}_hod.wav
#       lame  ${i}_hod.wav
#       sleep 10

if __name__=="__main__":
    Fire(main)
