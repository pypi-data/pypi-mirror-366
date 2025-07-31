#!/usr/bin/python3
#myservice_description: global notificator/in development
#
#   I need to combine with the advanced RPIHAT (running invisibly in screen)
#
#
import notify2
#sudo aptitude install python3-notify2
import time
#from multiprocessing import Queue
from queue import LifoQueue, Queue, Empty, Full
import os
import glob
import subprocess
from fire import Fire
from gtts import gTTS
#from pydub import AudioSegment
#from pydub.playback import play
#########################################from playsound import playsound
#from pydub.utils import make_chunks
import re
from notifator import notihat
from notifator import hodiny
from notifator import ntfy
from unidecode import unidecode

import select
import sys
import requests # ntfy.sh


import datetime as dt
import json
import os

#
# detect pipe mode... taken from cmdai
#


def is_cron():
    return not os.isatty(sys.stdin.fileno())

def pipe_mode():
    """
    detect mode - pipe or not
    """
    if is_cron():
        return None
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        print(f"D... {fg.lightslategray}Pipe mode detected! {fg.default}")
        mstdin = []
        for line in sys.stdin:
            mstdin.append( line.strip() )
        return mstdin
    # UNCLESS IT IS NOT
    else:
        # print(f"D... {fg.lightgray} NO Pipe  {fg.default}")
        return None #print("No pipe")


def take_time():
    return str(dt.datetime.now())[:-7]



class ScreenTool:
    servlist=[]
    def __init__(self):
        res=self.check_myservice()
        print("i... "+str(len(res))+" screens seen for the user")
        print( "i... : {}\n".format(res ) )


    def check_myservice(self):
        #### CMD="screen -ls "+self.screenname
        user_name = os.getenv('USER')
        res=glob.glob( "/var/run/screen/S-"+user_name+"/*" )
        res=[os.path.basename(x) for x in res] # 4321.myservice_
        shortres=["".join(x.split(".")[1:]) for x in res]
        self.servlist=res
        return res


    def run_screen(self, name, cmd):
        self.screenname=name
        print("i... starting screen")
        CMD=cmd
        print("D...  --- ",CMD)
        CMD='/usr/bin/screen -dmS '+self.screenname+' bash -c  "'+CMD+'"'
        print( CMD )
        ok=False
        #try:
        subprocess.check_call( CMD, shell=True )
        ok=True
        print("i...      run ok ")
        print("i...  screen STARTED")
        #except:
        #print("X...      xxx... screen  PROBLEM")


# ********************************************************
# ********************************************************
# ********************************************************
# ********************************************************
#
#
#  This is the main object.... housing   audio,hat,term,dbus....
#
# then later - the message is queued:
#    q.put( NotifyClass('audio',msg) )
#
#
# ********************************************************
# ********************************************************
# ********************************************************

class NotifyClass(object):

    def __init__(self, dest, message, timeshow = 10, color = 1.1):
        print("D... notifator target/message:",dest,"/",message)
        self.dest = dest
        self.message = message
        self.timeshow = timeshow
        self.color = color
        self.mp3 = None

        if self.message is not None:
            if os.path.exists(self.message):
                print(f"D... file exists {self.message}")
                print("D...  checking mp3 extension",os.path.splitext(self.message)[1])
                if os.path.splitext(self.message)[1]==".mp3":
                    self.mp3 = self.message
        else:
            print("D.... maybe clock ??")


    # **********************************************************************
    # **********************************************************************

    def audio(self, lang="cs", CACHE="~/sound_cache/", playme = True):
        """
Use google etxt to speech, not too frequently. Creates an mp3 in /tmp and reads it
        """
        if self.mp3 is not None:
            pass #playsound(self.mp3)
            return

        cache = os.path.expanduser(CACHE)
        #print("@"+self.audio.__name__, end='')
        #t = re.compile("[a-zA-Z0-9.,_-]")

        #CMD = f"iconv -f utf-8 -t ascii//TRANSLIT"
        #sp.check_call( CMD )

        t = re.compile("[a-zA-Z0-9_]+") # safe characters
        #unsafe = "abc∂éåß®∆˚˙©¬ñ√ƒµ©∆∫ø"
        unsafe=self.message

        #unidecode(u"Žluťoučký kůň")
        safe = unidecode(unsafe)
        print("D... ",safe)
        safe = safe.replace(" ","_")
        print("D... ",safe)
        #
        safe = [ch for ch in safe if t.match(ch)]
        print("D... ",safe)
        safe = "".join(safe)
        print("D... ",safe)

        outfile="/tmp/msg_"+safe+".mp3"
        if os.path.exists(cache):
            outfile = f"{cache}/{safe}.mp3"
            outfile = outfile.replace("//","/")

        if not os.path.isfile(outfile):
            print("D... contacting google for tts ...", self.message)
            tts=gTTS( self.message+"." , lang=lang)
            tts.save(outfile)
        else:
            print(f"D... taking sound from {outfile}")

        # read it
        #path_to_file = outfile
        #song = AudioSegment.from_mp3(path_to_file)
        #play(song) # it was  +8 which may be volume up
        if playme:
            pass # playsound(outfile)
        return outfile #self.message


    # **********************************************************************
    # **********************************************************************


    def multicast(self):

        outfile = ""
        if self.mp3 is not None:
            outfile = self.mp3
        else:
            outfile = self.audio( playme = False)
        #CMD = f"ffmpeg -re  -i {outfile}  -acodec libopus -b:a 12k -f rtp rtp://239.0.0.1:8786"
        CMD = f"ffmpeg -re -fflags nobuffer -i {outfile}  -acodec libopus -b:a 72k -f mpegts udp://239.0.0.1:8786"
        # receive with # mpv --cache=no  --framedrop=no --speed=1.01  udp://239.0.0.1:8786
        CMD = f"ffmpeg -re -fflags nobuffer -flags low_delay  -strict experimental -i {outfile} -acodec libopus -b:a 196k -f mpegts 'udp://239.0.0.1:8786?pkt_size=128'"
        # ----this seems to work !!! no flasgc
        CMD = f"ffmpeg -re   -fflags nobuffer  -i {outfile} -acodec libopus -b:a 32k -f mpegts 'udp://239.0.0.1:8786?pkt_size=512'"
        print(CMD)
        print(CMD)
        subprocess.check_call( CMD, shell=True )


    # **********************************************************************
    # **********************************************************************

    def multicast_clock(self):
        """
        New
        """
        print("D....    multicast clock,.....")
        mp3file = hodiny.hodiny()
        print("D....    multicast clockdone,.....")
        self.mp3 = mp3file
        #outfile =
        if self.mp3 is not None:
            outfile = self.mp3
        else:
            outfile = self.audio( playme = False)
        #CMD = f"ffmpeg -re  -i {outfile}  -acodec libopus -b:a 12k -f rtp rtp://239.0.0.1:8786"
        self.multicast()


    # **********************************************************************
    # **********************************************************************

    def dbus(self):
        #print("@"+self.dbus.__name__+' ', end='')
        notify2.init("--Title--")
        #notice = notify2.Notification(self.dest, self.message)
        notice = notify2.Notification( self.message )
        notice.show()
        time.sleep(0.1)
        return self.message

    # **********************************************************************
    # **********************************************************************

    def hat(self):
        #print("@"+self.hat.__name__+'  ', end='')
        print("D... HAT ON")
        notihat.main(message=self.message,
                     timeshow=self.timeshow,
                     color = self.color)
        return self.message


    def web(self):
        """
        I dont remember what this was
        """
        #print("@"+self.web.__name__+'  ', end='')
        return self.message

    # **********************************************************************
    # **********************************************************************

    def ntfy_sh(self, scrshot=False):
        """
        Let all heavy lifting to ntfy.py, just define the message and title
        """
        now = take_time()
        title = f"{now}"
        message = self.message
        filename = None
        ntfy.send_ntf(message, title, scrshot=scrshot)

        # if scrshot:
        #     message = f""#THE message {now}"
        #     title = self.message # the message will be in the title
        #     filename = take_screenshot(w=200)
        #     data=open(filename, 'rb')
        #     filename = "m.jpg"
        # else:
        #     data = self.message
        #     title = ""
        #     # no message here for some reason... and title = "" to make it short

        #     # "Actions": "http, OpenSeznam, https://www.seznam.cz/, method=PUT, headers.Authorization=Bearer zAzsx1sk.., body={\"action\": \"close\"}"   }
        # response = requests.put( url_full,
        #                          data=data,
        #                          headers={ "Title": f"{title}",
        #                                    "Filename": filename,
        #                                    "message": message,
        #                                   # "Actions": "http, OpenSeznam, https://www.seznam.cz/ "
        #                                   }
        #                         )

        # if response.status_code == 200:
        #     print("Notification with image sent successfully! ntfy.sh")
        # else:
        #     print("Failed to send notification.  ntfy.sh")
        # return self.message

    # **********************************************************************
    # **********************************************************************
    def ntfy_sh_scr(self, scrshot=True):
        """
        just call with rue parameter .... ./bin_notifator.py n hoj 1
        """
        self.ntfy_sh(scrshot=True)
        return self.message

    # **********************************************************************
    # **********************************************************************
    def term(self):
        """
        add the user to tty group to be able to listen
        usermod -a -G tty  user
        """

        #print("@"+self.term.__name__+' ', end='')
        msg=self.message
        print(msg)
        msg=msg.replace('"',' ')
        msg=msg.replace('\\',' ')
        msg=msg.replace('|',' ')
        msg=msg.replace('$',' ')
        msg=msg.replace('#',' ')
        msg=msg.replace('`',' ')
        msg=msg.replace("'",' ')
        os.system('echo "'+msg+'" | wall')
        return self.message

#============ this RUNS the message on destination. Call do
#
#
#

    def do( self ):
        return getattr(NotifyClass, self.dest)(self)


#===================================================================
#
#===================================================================
#
#
#
#

def issueall(message):
    """Issues message to all: audio, dbus, hat, term
    """
    q = Queue(6)   # how does this work?

    msg = message
    pmo = pipe_mode()# from pipe
    if pmo is not None:
        msg = '\n'.join(pmo)

    q.put( NotifyClass('audio',msg) )
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    q.put( NotifyClass('dbus' ,   msg  ) )
    q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    q.put( NotifyClass('term' , msg) )

    #================== RPIHAT PART
    #s=ScreenTool()
    #s.run_screen("sleeptest","sleep 10") # this can contain rpihat...

    while not q.empty():
        res=q.get().do()
        #print("   ", res)


#===================================================================
#
#===================================================================
#
#
#
#

def issue_hat(message = None, timeshow = 13, color = 1.1):
    """ Issues a message to RpiHAT (or the emulator)
    """
    print("D... issue_hat")
    q = Queue(6)
    print(q)


    msg = message
    pmo = pipe_mode()# from pipe
    if pmo is not None:
        msg = '\n'.join(pmo)


    q.put( NotifyClass('hat', msg, timeshow , color) )
    print("D... hat in queue")
    while not q.empty():
        res=q.get().do()


#===================================================================
#
#===================================================================
#
#
#
#

def issue_sound(message = None):
    """Issues a message to speech translator and plays locally
    """
    q = Queue(6)   # how does this work?


    msg = message
    pmo = pipe_mode()
    if pmo is not None:
        msg = '\n'.join(pmo)
    q.put( NotifyClass('audio',msg) )
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    #q.put( NotifyClass('dbus' ,   message  ) )
    #q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    #q.put( NotifyClass('term' , message) )

    while not q.empty():
        res=q.get().do()
#===================================================================
#
#===================================================================
#
#
#
#

def issue_term(message = None):
    """Issues a message on term wall /untested/
    """
    q = Queue(6)   # how does this work?

    msg = message
    pmo = pipe_mode() # from pipe
    if pmo is not None:
        msg = '\n'.join(pmo)
    q.put( NotifyClass('term',msg) )
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    #q.put( NotifyClass('dbus' ,   message  ) )
    #q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    #q.put( NotifyClass('term' , message) )

    while not q.empty():
        res=q.get().do()


#===================================================================
#
#===================================================================
#
#
#
#

def issue_multicast(message = None):
    """Issues a message to speech translator and multicasts on port 8786
    """
    q = Queue(6)   # how does this work?

    msg = message
    pmo = pipe_mode()# from pipe
    if pmo is not None:
        msg = '\n'.join(pmo)


    q.put( NotifyClass('multicast',msg) )
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    #q.put( NotifyClass('dbus' ,   message  ) )
    #q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    #q.put( NotifyClass('term' , message) )

    while not q.empty():
        res=q.get().do()


#===================================================================
#
#===================================================================
#
#
#
#

def issue_multicast_clock(message = None):
    """Issues a message to speech translator and multicasts on port 8786
    """
    q = Queue(6)   # how does this work?

    msg = message
    pmo = pipe_mode()# from pipe
    if pmo is not None:
        msg = '\n'.join(pmo)

    print("D... qput")
    q.put( NotifyClass('multicast_clock', message) )
    print("D... *DONE*")
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    #q.put( NotifyClass('dbus' ,   message  ) )
    #q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    #q.put( NotifyClass('term' , message) )

    while not q.empty():
        res=q.get().do()

#===================================================================
#
#===================================================================
#

def issue_dbus(message = None):
    """Issues a message to DBUS system (crash on RPi)
    """
    q = Queue(6)   # how does this work?

    msg = message
    pmo = pipe_mode()# from pipe
    if pmo is not None:
        msg = '\n'.join(pmo)

    #q.put( NotifyClass('audio',message) )
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    q.put( NotifyClass('dbus' ,   msg  ) )
    #q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    #q.put( NotifyClass('term' , message) )

    while not q.empty():
        res=q.get().do()

#===================================================================
#
#===================================================================
#

def issue_ntfy_sh(message , scrshot=False):
    """Issues a message ntfy.sh
    """
    if scrshot:
        print("D... screenshot required... ntfy.sh")
    q = Queue(6)   # how does this work?

    msg = message
    pmo = pipe_mode()# from pipe
    if pmo is not None:
        msg = '\n'.join(pmo)

    if scrshot:
        q.put( NotifyClass('ntfy_sh_scr' ,   msg    ) )
    else:
        q.put( NotifyClass('ntfy_sh' ,   msg    ) )

    while not q.empty():
        res=q.get().do()


#============================================================
#============================================================
#============================================================
#============================================================
#============================================================

if __name__=="__main__":
    Fire( {"a":issueall,
           "s":issue_sound,
           "m":issue_multicast,
           "c":issue_multicast_clock,
           "n":issue_ntfy_sh,
           "t":issue_term,
           "h":issue_hat,
           "b":issue_dbus}
         )
