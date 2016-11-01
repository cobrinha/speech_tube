# -*- coding: utf-8 -*-
import re
import os
import urllib
import urllib2
import speech_recognition as sr
import mp3play
import time
import youtube_dl
import thread_youtube
import threading
import unicodedata


proc_youtube = 0
path_youtube = ""

def robot_voice(text):
    text=text.split()
    text='+'.join(text)
    #url = "http://translate.google.com/translate_tts?tl=pt-BR&q="+text
    url = "http://text2speech.us/mp3.php?lf=pt&gender=female&t="+text
    request = urllib2.Request(url)
    request.add_header('User-agent', 'Mozilla/5.0') 
    opener = urllib2.build_opener()
    return opener.open(request).read()

def say(text):
    f = open("data.mp3", "wb")
    f.write(robot_voice(text))
    f.close()
    play()

def play():
    time.sleep(0.5)    
    mp3=mp3play.load('data.mp3')
    mp3.play()
    time.sleep(mp3.seconds())
    mp3.stop()
    mp3 = ""         

def recognize(Frame):
    #r = sr.Recognizer(language = "pt-BR")
    r = sr.Recognizer()
    global proc_youtube
    global path_youtube
    disse = ""

    with sr.Microphone() as source:
        print('Diga alguma coisa')
        Frame.set_label('Diga alguma coisa')        
        say('Diga alguma coisa')         
        audio = r.listen(source)                   

    try:
        disse = r.recognize(audio)
        #disse = "oldfield your love"
        print(disse.encode('utf-8').strip())
        Frame.set_label(disse.encode('utf-8').strip())        
        say(disse.encode('utf-8').strip())
        disse = unicodedata.normalize('NFKD',disse).encode('ascii','ignore')        
       
    except LookupError:                            
        print("Desculpe, não entendi.")
        say("Desculpe, não entendi.")
        path_youtube = ""
        recognize(Frame)
        
    try:
        os.remove(os.path.dirname(__file__)+'/temp.mp3')
        os.remove(os.path.dirname(__file__)+'/temp.mp4')
    except:
        pass

    if disse !="":
        quoted_query = urllib.quote(disse.encode('utf-8').strip())
    else:
        print "Erro!"
        recognize(Frame)
        
    host = 'https://www.youtube.com/results?search_query=%s' % (quoted_query)
    req = urllib2.Request(host)
    req.add_header('User-Agent', 'Mozilla/5.0')
    conn = urllib2.urlopen(req)
    data = conn.read()
    conn.close()

    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', data) 
    url = "http://www.youtube.com/watch?v=" + search_results[0]

    path_youtube = search_results[0]+'.flv'

    print 'Aguarde'
    say('Aguarde'.encode('utf-8').strip())

    subprocess_str = search_results[0]
    
    #subprocess_str = os.path.dirname(__file__)+'/youtube-dl.exe -f 5 --no-part -o "'+os.path.dirname(__file__)+'/'+search_results[0]+'.mp4" '+url
    th_youtube = thread_youtube.ThreadYouTube(subprocess_str)
    t = threading.Thread(target=th_youtube.run)
    t.daemon = True
    t.start()
    

    #proc_youtube =  Popen(subprocess_str   shell = True)

    #for line in iter(proc_youtube.stdout.readline, b''):
    #    print line
    #    if 'Destination' in line or 'Resuming' in line:
    #        break;


    print 'Sleeping'
    time.sleep(5)

    
    Frame.hide_label()
    return

    #TODO

    #os.system(os.path.dirname(__file__)+'/ffmpeg.exe -i '+os.path.dirname(__file__)+'/temp.mp4 '+os.path.dirname(__file__)+'/temp.mp3')

    #filename = os.path.dirname(__file__)+'/temp.mp3'
    #clip = mp3play.load(filename)

    #print 'Tocando '+disse.encode('utf-8').strip()
    #say('Tocando '+disse.encode('utf-8').strip())

    #clip.play()
    #print clip.seconds()
    #time.sleep(clip.seconds())
    #clip.stop()

    #selection = raw_input('Y to continue')
    
    #if selection.capitalize() == 'Y':
    #    recognize()


def terminate_youtube():
    global proc_youtube
    try:
        proc_youtube.terminate()
    except:
        pass

def download_video(arquivo, url):
    os.system(os.path.dirname(__file__)+'/youtube-dl.exe -f mp4 -o "'+os.path.dirname(__file__)+'/'+arquivo+'.mp4" '+url)
    return

def open_video(arquivo):
    os.system(os.path.dirname(__file__)+'/mplayer.exe "'+os.path.dirname(__file__)+'/'+arquivo+'.mp4" -x 1800 -y 950')

   
#recognize()
