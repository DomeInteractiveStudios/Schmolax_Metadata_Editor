import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog
import os
from datetime import datetime


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

def readRecentActivity(newFilePath):
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
            file.write(f'{current_date} || {newFilePath}\n')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Schmolax Metadata Editor')

        # Create menu bar
        menubar = self.menuBar()

        # Create file menu
        fileMenu = menubar.addMenu('File')

        # Create open action
        openAction = QAction('Open', self)
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)

        self.setGeometry(300, 300, 800, 600)

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Audio Files (*.mp3 *.flac)", options=options)
        if fileName:
            readRecentActivity(fileName) # Add this line

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())