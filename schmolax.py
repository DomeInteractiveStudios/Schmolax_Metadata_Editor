import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
import os
from datetime import datetime
import mutagen

class Shortcut:
    # NAME: NAME OF THE SHORTCUT
    # KEY: KEYBOARD SHORTCUT
    # FUNCTION: FUNCTION TO BE CALLED WHEN THE SHORTCUT IS PRESSED
    # SHORTCUT TYPE: ON WHAT DOES THE SHORTCUT WORK (FILE, EDIT, VIEW, ETC...)
    def __init__(self, name, key, function, shortcutType):
        self.name = name
        self.key = key
        self.function = function
        self.shortcutType = shortcutType

class Album:
    def __init__(self, name):
        self.name = name
        self.songs = []

    def add_song(self, song): #? ADDS A SONG TO THE ALBUM
        self.songs.append(song)

    def __repr__(self): #? RETURNS THE ALBUM NAME AND ALL SONGS IN THE ALBUM
        return f"Album: (name='{self.name}', songs={self.songs})"


class RecentActivity:
    def __init__(self):
        self.albums = {}

    def add_song(self, album_name, song_name): #? ADDS A SONG TO THE ALBUM (ALTERNATIVE METHOD)
        if album_name not in self.albums:
            self.albums[album_name] = Album(album_name)
        self.albums[album_name].add_song(song_name)

    def get_album_by_name(self, album_name): #? RETURNS AN ALBUM BY PROVIDING THE ALBUM NAME
        return self.albums.get(album_name)

    def get_songs_by_album(self, album_name): #? RETURNS ALL SONGS IN AN ALBUM BY PROVIDING THE ALBUM NAME
        return self.albums.get(album_name).songs if album_name in self.albums else None

    def __repr__(self): #? RETURNS ALL ALBUMS IN THE RECENT ACTIVITY
        return f"RecentActivity: (albums={list(self.albums.values())})"

def recentAcitivityFile():
    recent_activity_folder = os.getcwd()
    recent_activity_folder = os.path.join(recent_activity_folder, 'RecentActivity')
    if not os.path.exists(recent_activity_folder):
        os.makedirs(recent_activity_folder)
    txt_file_path = os.path.join(recent_activity_folder, 'recent_activity.txt')
    #print(txt_file_path)

    if not os.path.exists(txt_file_path):
        with open(txt_file_path, 'w') as file:
            file.write('')

    return txt_file_path

def updateRecentActivity(newFilePath, album):
    txt_file_path = recentAcitivityFile()

    with open(txt_file_path, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        found = False
        for line in lines:
            if newFilePath in line:
                found = True
            file.write(line)
        if not found:
            current_date = datetime.now().strftime('%Y-%m-%d')
            file.write(f'{current_date} || {album} || {newFilePath}\n')

library = RecentActivity()
shortcuts = []
actions = []

class MainWindow(QMainWindow):
    def setShortcuts(self):
        global shortcuts, actions

        #? ADDS SHORTCUTS HERE ↓
        shortcuts.append(Shortcut("Open File", 'Ctrl+O', self.openFile, "File"))
        shortcuts.append(Shortcut("Exit", 'Ctrl+Q', self.close, "Misc"))
        #? ADDS SHORTCUTS HERE ↑

        #? ASSOCIATES SHORTCUTS WITH ACTIONS
        for shortcut in shortcuts:
            actions.append(QAction(shortcut.name, self))
            actions[-1].setShortcut(shortcut.key)
            actions[-1].triggered.connect(shortcut.function)
            self.addAction(actions[-1])

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        global shortcuts, actions

        self.setShortcuts() #? SETS SHORTCUTS

        self.setWindowTitle('Schmolax Metadata Editor')

        # Create menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        miscMenu = menubar.addMenu('Misc')

        for shortcut, action in zip(shortcuts, actions):
            match shortcut.shortcutType.lower():
                case "file":
                    fileMenu.addAction(action)
                case "misc":
                    miscMenu.addAction(action)

        # Create central widget and layout
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Use a horizontal layout for the buttons
        self.layout = QHBoxLayout(self.centralWidget)
        self.centralWidget.setLayout(self.layout)

        self.setGeometry(300, 300, 800, 600)

        self.checkForRecentActivity()

    def openFile(self):
        #TODO: 
            ## make this support special characters
            ## make this support multiple files
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Audio Files (*.mp3 *.flac)", options=options)
        if fileName:
            audio = mutagen.File(fileName, easy=True)
        else: return
        if audio:
            if audio.get("album", [""])[0] != "": album = audio.get("album", [""])[0]
            else: album = "Unknown Album"

        updateRecentActivity(fileName, album)
        if not library.get_album_by_name(album): self.layout.addWidget(self.createSongButton(album))
        library.add_song(album, fileName)


    def createSongButton(self, album):
        #TODO: 
            ## make it so that only max 8 buttons are shown per row
            ## make it so on resize the buttons go to the next row
        songButton = QPushButton(album, self)
        songButton.setFixedSize(200, 200)
        songButton.setStyleSheet(
            "background-color: none; border: 1px solid #ccc; margin: 5px;"
        )
        songButton.clicked.connect(lambda: print(library.get_songs_by_album(album)))

        # Add button to horizontal layout
        self.layout.addWidget(songButton)

    def checkForRecentActivity(self):
        txt_file_path = recentAcitivityFile()
        with open(txt_file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                date, album, songPath = line.split(' || ')
                songPath = songPath.replace('\n', '') #? REMOVES THE NEW LINE CHARACTER
                library.add_song(album, songPath)
        for album in library.albums:
            self.createSongButton(album)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    for action in actions:
        mainWin.addAction(action)
    mainWin.show()
    sys.exit(app.exec_())