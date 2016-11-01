import threading, os
from subprocess import Popen, PIPE, STDOUT
import time

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    elif d['status'] == 'error':
        print d['status']
        

class ThreadYouTube(threading.Thread):
    """Test Worker Thread Class."""
 
    #----------------------------------------------------------------------
    def __init__(self, command):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.command = command
        #self.run()
 
    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.

        """command = self.command
        proc_youtube =  Popen(command, stdout = PIPE, stderr = STDOUT, shell = True)

        for line in iter(proc_youtube.stdout.readline, b''):
            print line
            if 'Destination' in line or 'Resuming' in line:
                break;
        """

        import youtube_dl

        ydl_opts = {
            'format': '5',
            'outtmpl': os.path.dirname(__file__)+"/%(id)s.%(ext)s",
            'nopart': True,
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['http://www.youtube.com/watch?v='+self.command, 'nopart'])

        '''ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})

        with ydl:
            result = ydl.extract_info(
                'http://www.youtube.com/watch?v='+self.command,
                download=True # We just want to extract the info
            )

        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result

        print(video)
        video_url = video['url']
        print(video_url)        '''
        
