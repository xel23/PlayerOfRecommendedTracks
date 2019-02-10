import sys, requests, json, os
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QUrl, QDirIterator, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QAction, QHBoxLayout, \
    QVBoxLayout, QSlider, QFormLayout, QLineEdit, QDialog, QMessageBox
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from mutagen.id3 import ID3
from lxml.html import fromstring

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.login = QLineEdit()
        self.login.setPlaceholderText('Введите логин...')

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText('Введите пароль...')

        layout = QFormLayout()
        layout.addRow('Login:', self.login)
        layout.addRow('Password:', self.password)
        btn1 = QPushButton("OK", self)
        btn2 = QPushButton("Cancel", self)
        layout.addWidget(btn1)
        layout.addWidget(btn2)

        self.setLayout(layout)

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.title = 'Personal audio player v2.3'
        self.left = 300
        self.top = 300
        self.width = 300
        self.height = 150
        self.color = 0  # 0- toggle to dark 1- toggle to light
        self.userAction = -1  # 0- stopped, 1- playing 2-paused
        self.duration = 0
        #self.getRecommendedPlaylist()
        self.initUI()

    def initUI(self):
        # Add file menu
        menubar = self.menuBar()
        filemenu = menubar.addMenu('File')
        windowmenu = menubar.addMenu('Window')
        connectTo = menubar.addMenu('Connect to...')

        fileAct = QAction('Open File', self)
        folderAct = QAction('Open Folder', self)
        themeAct = QAction('Toggle light/dark theme', self)
        yandexMusic = QAction('Yandex Music', self)
        deezer = QAction('Deezer', self)
        spotify = QAction('Spotify', self)
        pandora = QAction('Pandora', self)
        mixcloud = QAction('Pandora', self)

        fileAct.setShortcut('Ctrl+O')
        folderAct.setShortcut('Ctrl+D')
        themeAct.setShortcut('Ctrl+T')


        filemenu.addAction(fileAct)
        filemenu.addAction(folderAct)
        windowmenu.addAction(themeAct)
        connectTo.addAction(yandexMusic)
        connectTo.addAction(deezer)
        connectTo.addAction(pandora)
        connectTo.addAction(mixcloud)
        connectTo.addAction(spotify)

        fileAct.triggered.connect(self.openFile)
        folderAct.triggered.connect(self.addFiles)
        themeAct.triggered.connect(self.toggleColors)
        yandexMusic.triggered.connect(self.connectYandexMusic)
        deezer.triggered.connect(self.connectYandexMusic)
        pandora.triggered.connect(self.connectYandexMusic)
        mixcloud.triggered.connect(self.connectYandexMusic)
        spotify.triggered.connect(self.connectYandexMusic)

        self.addControls()

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.toggleColors()
        self.show()

    def downloadTrack(self, name):
        page = requests.get("http://zaycev.net/search.html?query_search=" + name).text
        parser = fromstring(page)
        fileJSON = parser.xpath('//div/@data-url')
        resp = requests.get("http://zaycev.net" + fileJSON[1])
        data = resp.json()
        with open("track.json", 'w') as outfile:
            json.dump(data, outfile)
        connection_file = open("track.json", 'r')
        conn_string = json.load(connection_file)

        track = requests.get(conn_string['url'].rsplit('?')[0])
        try:
            os.makedirs('./tracks')
        except OSError:
            pass

        out = open("./tracks/" + name.strip() + ".mp3", 'wb')
        out.write(track.content)
        out.close()
        QMessageBox.about(self, "Track added!", name.strip() + " was added")

    def playRecommend(self):
        try:
            similarTracks = open("playlist.txt", 'r')
            i = 0
            for line in similarTracks.readlines():
                if i == 5:
                    break
                else:
                    i = i+1
                print(line)
                self.downloadTrack(line)
                self.openFileRec("./tracks/" + line.strip() + ".mp3")

        except:
            QMessageBox.about(self, "Play error!", "Unknown error!")

    def getRecommendedPlaylist(self, song):
        try:
            audio = ID3(song[0])
            title = ''.join(audio['TIT2'].text[0].rsplit('(')[0])
            if title[-1] == ' ':
                title = title[0:-1]
            artist = audio['TPE1'].text[0]
            if artist[-1] == ' ':
                artist = artist[0:-1]
            print(artist + " " + title)
            resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=track.getsimilar&artist=" + artist + "&track=" + title +
                                "&api_key=API_key&format=json")
            data = resp.json()
            with open("playlist" + artist + "-" + title + ".json", 'w') as outfile:
                json.dump(data, outfile)
            connection_file = open("playlist" + artist + "-" + title + ".json", 'r')
            conn_string = json.load(connection_file)

            with open("playlist.txt", 'a') as playlistFile:
                for track in conn_string['similartracks']['track']:
                    playlistFile.write(track['artist']['name'] + " " + track['name'] + "\n")
            playlistFile.close()
        except:
            QMessageBox.about(self, "Error!", "Some trouble with export title or artist name, try other track")

    def getRecommendedPlaylistFolder(self, song):
        audio = ID3(song)
        title = ''.join(audio['TIT2'].text[0].rsplit('(')[0])
        if title[-1] == ' ':
            title = title[0:-1]
        artist = audio['TPE1'].text[0]
        if artist[-1] == ' ':
            artist = artist[0:-1]
        print(artist + " " + title)
        resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=track.getsimilar&artist=" + artist + "&track=" + title +
                            "&api_key=API_key&format=json")
        data = resp.json()
        with open("playlist" + artist + "-" + title + ".json", 'w') as outfile:
            json.dump(data, outfile)
            connection_file = open("playlist" + artist + "-" + title + ".json", 'r')
        conn_string = json.load(connection_file)
        with open("playlist.txt", 'a') as playlistFile:
            for track in conn_string['similartracks']['track']:
                playlistFile.write(track['artist']['name'] + " " + track['name'] + "\n")
        playlistFile.close()

    def addControls(self):
        wid = QWidget(self)
        self.setCentralWidget(wid)
        # Add song controls
        volumeslider = QSlider(Qt.Horizontal, self)
        volumeslider.setFocusPolicy(Qt.NoFocus)
        volumeslider.valueChanged[int].connect(self.changeVolume)
        volumeslider.setValue(50)

        sldPosition = QSlider(Qt.Horizontal, self)
        sldPosition.setMinimum(0)
        sldPosition.setFocusPolicy(Qt.NoFocus)
        #sldPosition.valueChanged.connect(self.player.setPosition)
        self.player.positionChanged.connect(sldPosition.setValue)
        sldPosition.setMaximum(180000)

        playBtn = QPushButton('Play')  # play button
        pauseBtn = QPushButton('Pause')  # pause button
        stopBtn = QPushButton('Stop')  # stop button
        # Add playlist controls
        prevBtn = QPushButton('Prev')
        shuffleBtn = QPushButton('Shuffle')
        nextBtn = QPushButton('Next')
        playRecommendedBtn = QPushButton('Play Recommended Playlist')
        like = QPushButton('Like')
        dislike = QPushButton('DisLike')

        # Add button layouts
        controlArea = QVBoxLayout()  # centralWidget
        controls = QHBoxLayout()
        playlistCtrlLayout = QHBoxLayout()
        playRec = QHBoxLayout()
        ld = QHBoxLayout()

        # Add buttons to song controls layout
        controls.addWidget(playBtn)
        controls.addWidget(pauseBtn)
        controls.addWidget(stopBtn)
        # Add buttons to playlist controls layout
        playlistCtrlLayout.addWidget(prevBtn)
        playlistCtrlLayout.addWidget(shuffleBtn)
        playlistCtrlLayout.addWidget(nextBtn)
        playRec.addWidget(playRecommendedBtn)
        ld.addWidget(like)
        ld.addWidget(dislike)
        # Add to vertical layout
        controlArea.addWidget(sldPosition)
        controlArea.addWidget(volumeslider)
        controlArea.addLayout(controls)
        controlArea.addLayout(playlistCtrlLayout)
        controlArea.addLayout(playRec)
        controlArea.addLayout(ld)
        wid.setLayout(controlArea)
        # Connect each signal to their appropriate function
        playBtn.clicked.connect(self.playhandler)
        pauseBtn.clicked.connect(self.pausehandler)
        stopBtn.clicked.connect(self.stophandler)

        prevBtn.clicked.connect(self.prevSong)
        shuffleBtn.clicked.connect(self.shufflelist)
        nextBtn.clicked.connect(self.nextSong)

        playRecommendedBtn.clicked.connect(self.playRecommend)

        like.clicked.connect(self.like)
        dislike.clicked.connect(self.dislike)

        self.statusBar()

        self.playlist.currentMediaChanged.connect(self.songChanged)

    def like(self, text):
        QMessageBox.about(self, "Attention!", "You have Liked track!")

    def dislike(self, text):
        QMessageBox.about(self, "Attention!", "You have DisLiked track!")

    def connectYandexMusic(self):
        apple = LoginWindow()
        apple.exec_()

    def openFile(self):
        print("File button clicked!")
        song = QFileDialog.getOpenFileName(self, "Open Song", "~", "Sound Files (*.mp3 *.ogg *.wav *.m4a)")
        print(song[0])

        if song[0] != '':
            url = QUrl.fromLocalFile(song[0])
            if self.playlist.mediaCount() == 0:
                self.playlist.addMedia(QMediaContent(url))
                self.player.setPlaylist(self.playlist)
                self.player.play()
                self.userAction = 1
                print(self.playlist.mediaCount())
            else:
                self.playlist.addMedia(QMediaContent(url))
                print(self.playlist.mediaCount())
            self.getRecommendedPlaylist(song)

    def openFileRec(self, path):
        song = path

        if song != '':
            url = QUrl.fromLocalFile(song)
            if self.playlist.mediaCount() == 0:
                self.playlist.addMedia(QMediaContent(url))
                self.player.setPlaylist(self.playlist)
                self.player.play()
                self.userAction = 1
                print(self.playlist.mediaCount())
            else:
                self.playlist.addMedia(QMediaContent(url))
                print(self.playlist.mediaCount())

    def addFiles(self):
        print("Folder button clicked!")
        if self.playlist.mediaCount() != 0:
            self.folderIterator()
            print(self.playlist.mediaCount())
        else:
            self.folderIterator()
            self.player.setPlaylist(self.playlist)
            self.player.playlist().setCurrentIndex(0)
            self.player.play()
            print(self.playlist.mediaCount())
            self.userAction = 1

    def folderIterator(self):
        folderChosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', '~')
        if folderChosen != None:
            it = QDirIterator(folderChosen)
            it.next()
            while it.hasNext():
                if it.fileInfo().isDir() == False and it.filePath() != '.':
                    fInfo = it.fileInfo()
                    print(it.filePath(), fInfo.suffix())
                    if fInfo.suffix() in ('mp3', 'ogg', 'wav', 'm4a'):
                        print('added file', fInfo.fileName())
                        self.getRecommendedPlaylistFolder(it.filePath())
                        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                it.next()
            if it.fileInfo().isDir() == False and it.filePath() != '.':
                fInfo = it.fileInfo()
                print(it.filePath(), fInfo.suffix())
                if fInfo.suffix() in ('mp3', 'ogg', 'wav', 'm4a'):
                    print('added file', fInfo.fileName())
                    self.getRecommendedPlaylistFolder(it.filePath())
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))

    def playhandler(self):
        if self.playlist.mediaCount() == 0:
            self.openFile()
        elif self.playlist.mediaCount() != 0:
            self.player.play()
            print(self.playlist.mediaCount())
            self.userAction = 1

    def pausehandler(self):
        self.userAction = 2
        self.player.pause()

    def stophandler(self):
        self.userAction = 0
        self.player.stop()
        self.playlist.clear()
        print("Playlist cleared!")
        self.statusBar().showMessage("Stopped and cleared playlist")

    def changeVolume(self, value):
        self.player.setVolume(value)

    def changePosition(self, value):
        self.player.setPosition(value)

    def prevSong(self):
        if self.playlist.mediaCount() == 0:
            self.openFile()
        elif self.playlist.mediaCount() != 0:
            self.player.playlist().previous()

    def shufflelist(self):
        self.playlist.shuffle()
        print("Shuffled playlist!")

    def nextSong(self):
        if self.playlist.mediaCount() == 0:
            self.openFile()
        elif self.playlist.mediaCount() != 0:
            self.player.playlist().next()

    def songChanged(self, media):
        if not media.isNull():
            url = media.canonicalUrl()
            self.statusBar().showMessage(url.fileName())

    def toggleColors(self):

        app.setStyle("Fusion")
        palette = QPalette()
        if self.color == 0:
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(235, 101, 54))
            palette.setColor(QPalette.Highlight, QColor(235, 101, 54))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = 1
        elif self.color == 1:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, QColor(240, 240, 240))
            palette.setColor(QPalette.AlternateBase, Qt.white)
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, Qt.white)
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(66, 155, 248))
            palette.setColor(QPalette.Highlight, QColor(66, 155, 248))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())