import os
import time
import wx
import MplayerCtrl as mpc
import wx.lib.buttons as buttons
import speech
import threading

dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')

class ThreadSpeech(threading.Thread):
    """Test Worker Thread Class."""
 
    #----------------------------------------------------------------------
    def __init__(self, speech, frame):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.frame = frame
        self.speech = speech
        self.run()
 
    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        self.speech.recognize(self.frame)


class Frame(wx.Frame):
    
    #----------------------------------------------------------------------
    def __init__(self, parent, id, title, mplayer, trackpath):

        wx.Frame.__init__(self, parent, id, title)
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('black')
        
        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()
        self.currentVolume = 100

        self.create_menu()

        self.speech = speech
        self.thread_speech = None
        
        # create sizers
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        controlSizer = self.build_controls()
        sliderSizer = wx.BoxSizer(wx.HORIZONTAL)
        #labelSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.mplayer = mpc.MplayerCtrl(self.panel, -1, mplayer, trackpath)
        self.playbackSlider = wx.Slider(self.panel, size=wx.DefaultSize)
        sliderSizer.Add(self.playbackSlider, 1, wx.ALL|wx.EXPAND, 5)

        self.label=wx.StaticText(self.panel , -1, label='Voice Tube 0.1v', style=wx.ALIGN_CENTRE|wx.EXPAND, name='label')
        self.label.SetBackgroundColour('black')
        self.label.SetForegroundColour((255,255,255))
        font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.label.SetFont(font)
        #labelSizer.Add(self.label, 0, wx.ALL, 5)

        # create volume control
        self.volumeCtrl = wx.Slider(self.panel)
        self.volumeCtrl.SetRange(0, 100)
        self.volumeCtrl.SetValue(self.currentVolume)
        self.volumeCtrl.Bind(wx.EVT_SLIDER, self.on_set_volume)
        controlSizer.Add(self.volumeCtrl, 0, wx.ALL, 5)

        # create track counter
        self.trackCounter = wx.StaticText(self.panel, label="00:00")
        self.trackCounter.SetForegroundColour((255,255,255))
        sliderSizer.Add(self.trackCounter, 0, wx.ALL|wx.CENTER, 5)
        
        # set up playback timer
        self.playbackTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_playback)

        #self.mainSizer.Add(labelSizer, 0, wx.ALL|wx.EXPAND, 5)                  
        self.mainSizer.Add(self.mplayer, 1, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(sliderSizer, 0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(controlSizer, 0, wx.ALL|wx.CENTER, 5)
        self.panel.SetSizer(self.mainSizer)
        
        self.Bind(mpc.EVT_MEDIA_STARTED, self.on_media_started)
        self.Bind(mpc.EVT_MEDIA_FINISHED, self.on_media_finished)
        self.Bind(mpc.EVT_PROCESS_STARTED, self.on_process_started)
        self.Bind(mpc.EVT_PROCESS_STOPPED, self.on_process_stopped)

        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)

        self.trackpath = ""
        self.salva_offset = 0.1
        self.salva_offset_sleep = 5

        self.Maximize()
        self.Show()
        self.panel.Layout()

    #----------------------------------------------------------------------

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        print keycode
        if keycode == wx.WXK_SPACE:
            print "you pressed the spacebar!"
        event.Skip()

    #----------------------------------------------------------------------

    def hide_label(self):
        self.label.Hide()
        
    #----------------------------------------------------------------------

    def set_label(self, text):
        #self.label.show()
        self.label.SetLabel(text)
        timer = wx.Timer(self.panel, -1)
        timer.Start(3000)
        wx.EVT_TIMER(self.panel, -1, self.hide_label)        
        
    #----------------------------------------------------------------------
        
    def build_btn(self, btnDict, sizer):
        """"""
        bmp = btnDict['bitmap']
        handler = btnDict['handler']
                
        img = wx.Bitmap(os.path.join(bitmapDir, bmp))
        btn = buttons.GenBitmapButton(self.panel, bitmap=img,
                                      name=btnDict['name'])
        btn.SetInitialSize()
        btn.SetBackgroundColour('black')        
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.LEFT, 3)
        
    #----------------------------------------------------------------------
    def build_controls(self):
        """
        Builds the audio bar controls
        """
        controlSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btnData = [{'bitmap':'player_listen.png', 
                    'handler':self.on_recognize, 'name':'recognize'},
                    {'bitmap':'player_play.png', 
                    'handler':self.on_play, 'name':'play'},                   
                    {'bitmap':'player_pause.png', 
                    'handler':self.on_pause, 'name':'pause'},
                   {'bitmap':'player_stop.png',
                    'handler':self.on_stop, 'name':'stop'}]
        for btn in btnData:
            self.build_btn(btn, controlSizer)
            
        return controlSizer
    
    #----------------------------------------------------------------------
    def create_menu(self):
        """
        Creates a menu
        """
        #menubar = wx.MenuBar()
        #fileMenu = wx.Menu()
        #add_file_menu_item = fileMenu.Append(wx.NewId(), "&Add File", "Add Media File")
        #menubar.Append(fileMenu, '&File')
        
        #self.SetMenuBar(menubar)
        #self.Bind(wx.EVT_MENU, self.on_add_file, add_file_menu_item)
        
    #----------------------------------------------------------------------
    '''def on_add_file(self, event):
        wildcard = "Media Files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.currentFolder, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.currentFolder = os.path.dirname(path[0])
            trackPath = '"%s"' % path.replace("\\", "/")
            self.mplayer.Loadfile(trackPath)
            
            t_len = self.mplayer.GetTimeLength()
            self.playbackSlider.SetRange(0, t_len)
            self.playbackTimer.Start(100)'''
        
        
    #----------------------------------------------------------------------
    def on_media_started(self, event):
        t_len = self.mplayer.GetTimeLength()
        try:
            self.playbackSlider.SetRange(0, t_len)
        except:
            pass
        self.playbackTimer.Start(100)
        self.mplayer.Pause()
        self.playbackTimer.Start()
        self.timer.Stop()
        #except:
        #    print 'Erro on_media_started(), tentando mais uma vez...'
        #    self.on_media_started
        print 'Media started!'
        
    #----------------------------------------------------------------------
    def on_media_finished(self, event):
        print 'Media finished!'
        self.playbackTimer.Stop()
        
    #----------------------------------------------------------------------

    def on_recognize(self, event):
       
        #try:
        #    thread.start_new_thread( self.speech.recognize(self), ("Thread-1", 2, ) )
        #except:
        #    pass


        self.thread_speech = ThreadSpeech(self.speech, self)
        
        path = self.speech.path_youtube
        
        if path !="":
            trackpath = os.path.dirname(__file__)+"/"+path
            trackPath = '"%s"' % path.replace("\\", "/")
            self.trackpath = trackPath
            self.mplayer.Loadfile(trackPath)
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_media_started, self.timer)
            self.timer.Start(1000)
            
        else:
            time.sleep(1000)
            self.on_recognize(self)
        #self.mplayer.SetProperty('width', 1850)              
        #self.mplayer.SetProperty('height', 1850)              
       
    def on_play(self, event):
        """"""
    
        if self.playbackTimer.IsRunning():
            print "pausing..."
            self.mplayer.Pause()
            self.playbackTimer.Stop()
        else:
            print "unpausing..."
            self.mplayer.Pause()
            self.playbackTimer.Start()
            
    #----------------------------------------------------------------------
    def on_pause(self, event):
        """"""
        if self.playbackTimer.IsRunning():
            print "pausing..."
            self.mplayer.Pause()
            self.playbackTimer.Stop()
        else:
            print "unpausing..."
            self.mplayer.Pause()
            self.playbackTimer.Start()
        
    #----------------------------------------------------------------------
    def on_process_started(self, event):
        print 'Process started!'
        
    #----------------------------------------------------------------------
    def on_process_stopped(self, event):
        print 'Process stopped!'
        
    #----------------------------------------------------------------------
    def on_set_volume(self, event):
        """
        Sets the volume of the music player
        """
        self.currentVolume = self.volumeCtrl.GetValue()
        self.mplayer.SetProperty("volume", self.currentVolume)
        
    #----------------------------------------------------------------------
    def on_stop(self, event):
        """"""
        print "stopping..."
        self.mplayer.Stop()
        self.playbackTimer.Stop()
        self.speech.terminate_youtube()
        self.on_recognize(self)
        
        
    #----------------------------------------------------------------------
    def on_update_playback(self, event):
        """
        Updates playback slider and track counter
        """
        offset = self.mplayer.GetTimePos()
        print 'OFFSET:'+str(offset)+' salva_offset:'+str(self.salva_offset)
       
        if offset is None:

            if self.salva_offset > 5:
                print "Reiniciando..."
                self.mplayer.Stop()
                self.playbackTimer.Stop()
                self.speech.terminate_youtube()
                self.on_recognize(self)

            print "Erro - on_update_playback: "+self.trackpath
            self.speech.say('Aguarde, carregando...')
            time.sleep(self.salva_offset_sleep)
            self.salva_offset_sleep = self.salva_offset_sleep * 2
            self.mplayer.Loadfile(self.trackpath)
            t_len = self.mplayer.GetTimeLength()
            try:
                self.playbackSlider.SetRange(0, t_len)
            except:
                pass
            self.playbackTimer.Start(100)
            self.mplayer
            self.mplayer.Pause()
            self.mplayer.Seek(self.salva_offset)
            self.playbackTimer.Start()
            self.timer.Stop()
        else:
            self.salva_offset = offset                            
            
        mod_off = str(offset)[-1]

        if mod_off == '0':
            print "mod_off"
            offset = int(offset)
            self.playbackSlider.SetValue(offset)
            secsPlayed = time.strftime('%M:%S', time.gmtime(offset))
            self.trackCounter.SetLabel(secsPlayed)

    def play(self):
       self.on_play()


#----------------------------------------------------------------------
#if __name__ == "__main__":
def init(trackpath):
    import os, sys

    paths = [os.path.dirname(__file__)+'\mplayer.exe']
    mplayerPath = None
    for path in paths:
        if os.path.exists(path):
            mplayerPath = path
        
    if not mplayerPath:
        print "Erro - mplayer not found!"
        sys.exit()
            
    app = wx.App(redirect=False)
    frame = Frame(None, -1, 'Voice Tube 1.0v', mplayerPath, trackpath)
    #if trackpath !="":
    #    frame.load_file(trackpath)
    app.MainLoop()

if __name__ == "__main__":
    init("")
