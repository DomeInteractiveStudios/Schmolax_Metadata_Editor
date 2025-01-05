import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QPushButton, QWidget, QHBoxLayout, QGridLayout, QVBoxLayout, QLabel, QLayout
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, QRect, QPoint, QSize

import os
from datetime import datetime
import mutagen
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC

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

def updateDateForAlbum(album): 
    songFile = recentAcitivityFile()
    with open(songFile, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            date, albumName, songPath = line.split(' || ')
            if albumName == album:
                current_date = datetime.now().strftime('%Y-%m-%d')
                file.write(f'{current_date} || {album} || {songPath}')
            else:
                file.write(line)

library = RecentActivity()
shortcuts = []
actions = []
maxNumberOfSongsPerRow = 8
marginBetweenButtons = 5


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=10):
        super().__init__(parent)
        self.itemList = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Horizontal)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        y = 0
        line_height = 0
        x = 0
        for item in self.itemList:
            widget = item.widget()
            widget_size = item.sizeHint()
            if x + widget_size.width() > width:
                y += line_height + self.spacing()
                x = 0
                line_height = 0
            line_height = max(line_height, widget_size.height())
            x += widget_size.width() + self.spacing()
        return y + line_height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        x, y, line_height = rect.x(), rect.y(), 0
        for item in self.itemList:
            widget = item.widget()
            widget_size = item.sizeHint()
            if x + widget_size.width() > rect.width():
                x = rect.x()
                y += line_height + self.spacing()
                line_height = 0
            item.setGeometry(QRect(QPoint(x, y), widget_size))
            x += widget_size.width() + self.spacing()
            line_height = max(line_height, widget_size.height())

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().left())
        return size


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
        self.setWindowIcon(QIcon('Icons/Schmolax_Icon.png'))
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        self.setStyleSheet(f"background-color: none; max-width: {screen_size.width()}px; overflow: hidden; white-space: normal;")
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
        self.layout = FlowLayout(self.centralWidget, spacing=20)
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
        updateDateForAlbum(album)
        newAlbum = False
        if not library.get_album_by_name(album): 
            newAlbum = True
        library.add_song(album, fileName)
        if newAlbum: 
            #create a new button only if the album is new, this need to be created after adding the album to the library
            #however I need to check if it was already present before adding it, for obvious reasons
            self.layout.addWidget(self.createSongButton(album))

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

    def createSongButton(self, album):
        #TODO: 
            ## make sections divided by last modified date (SECTIONS: TODAY, YESTERDAY, THIS WEEK, THIS MONTH, THIS YEAR, ONE FOR EACH YEAR AFTER THAT)
            ## make it so on resize the buttons will "shrink" until they become 150x150 after which they will go to the next row
        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(marginBetweenButtons)  # Space between button and label
        container_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra 

        # Create the song button
        songButton = QPushButton('', self)
        songButton.setFixedSize(200, 200)
        songButton.setStyleSheet(
            "background-color: none; border: 1px solid #ccc; margin: 25px; text-align: center;"
        )
        if self.getFirstSongImage(album):
            songButton.setIcon(QIcon(QPixmap.fromImage(QImage.fromData(self.getFirstSongImage(album)))))
            songButton.setIconSize(songButton.size())
        else:
            songButton.setIcon(QIcon(QPixmap("Icons/Default_Album_Image.jpg")))
            songButton.setIconSize(songButton.size())

        # Connect the button click to display songs of the album
        # TODO: If a song is opened the date will be updated to today's date
        songButton.clicked.connect(lambda: print(library.get_songs_by_album(album)))

        # Create a label for the album name
        albumLabel = QLabel(album, self)
        albumLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        albumLabel.setFixedWidth(songButton.width())
        albumLabel.setWordWrap(True)
        albumLabel.setStyleSheet("font-size: 18px; color: #000; font-family: Cooper Black; font-weight: 400;")

        # Add the button and label to the container's layout
        container_layout.addWidget(songButton)
        container_layout.addWidget(albumLabel)

        # Add the container to the main layout
        self.layout.addWidget(container)

    def getFirstSongImage(self, album):
        if album not in library.albums: return None
        image = None
        for song_path in library.get_songs_by_album(album):
                if song_path.endswith(".mp3"):
                    audio = ID3(song_path)
                    for tag in audio.values():
                        if isinstance(tag, APIC):
                            image = tag.data
                            break
                elif song_path.endswith(".flac"):
                    audio = FLAC(song_path)
                    if audio.pictures:
                        image = audio.pictures[0].data
                        break
                if image:
                    break

        return image

if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), 'Icons', 'Schmolax.ico')
    app.setWindowIcon(QIcon(icon_path))
    # if not os.path.exists(icon_path):
    #     print(f"Icon file not found at: {icon_path}")
    # else:
    #     print(f"Icon file found at: {icon_path}")

    mainWin = MainWindow()
    mainWin.setWindowIcon(QIcon(icon_path))  #! Explicitly set the window's icon
    for action in actions:
        mainWin.addAction(action)
    mainWin.show()
    sys.exit(app.exec_())