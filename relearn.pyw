import os.path
import sys

from PyQt5.QtCore import (Qt, QSize, QRect, QUrl, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow,
        QMessageBox, QTextEdit, QAction, QGridLayout, QFrame, QDockWidget, 
        QSlider, QHBoxLayout, QPushButton, QSplitter, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget


class NoteText(QTextEdit):
    def __init__(self, mainWindow):
        super(NoteText, self).__init__()

        self.mainWindow = mainWindow

        font = self.document().defaultFont()
        font.setFamily("Cambria")
        font.setPointSize(12) 
        self.document().setDefaultFont(font)

        self.document().setPlainText("\n"*20)
        cursor = self.textCursor()
        cursor.setPosition(0)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            mainWindow.next()
        else:
            super(NoteText, self).keyPressEvent(event)

    def sizeHint(self):
        return QSize(200, 360)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Language Learning Machine")
        self.setWindowIcon(QIcon('bitmaps/repeater.png'))
        self.creatMenus()
        self.init()

        self.savedFilePath = None
        self.currentFilePath = None
        self.configFile = "config.txt"

        self.textEdit.setFocus()

    def init(self):

        self.textEdit = NoteText(self)
        #self.textEdit.resize(200, 360)

        self.hSlider = QSlider()
        #self.hSlider.setGeometry(QtCore.QRect(60, 60, 160, 21))
        self.hSlider.setOrientation(Qt.Horizontal)
        #self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
 
        buttonLayout = QHBoxLayout()

        self.playButton = QPushButton("play")
        self.playButton.clicked.connect(self.play)
        buttonLayout.addWidget(self.playButton)

        self.stopButton = QPushButton("stop")
        self.stopButton.clicked.connect(self.stop)
        buttonLayout.addWidget(self.stopButton)

        self.beginButton = QPushButton("begin")
        buttonLayout.addWidget(self.beginButton)
        self.endButton = QPushButton("end")
        buttonLayout.addWidget(self.endButton)

        self.nextButton = QPushButton("next")
        self.nextButton.clicked.connect(self.next)
        buttonLayout.addWidget(self.nextButton)

        self.playState = "Null"
        self.stopButton.setEnabled(False)
        self.playButton.setEnabled(False)
        self.nextButton.setEnabled(False)

        playLayout = QGridLayout()
        playLayout.addWidget(self.textEdit, 0, 0)
        playLayout.addWidget(self.hSlider, 1, 0)
        playLayout.addLayout(buttonLayout, 2, 0)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        # self.videoWidget.resize(500, -1)
        # self.videoWidget.resize(160, 360)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.setNotifyInterval(50)
        # mainLayout.addWidget(self.videoWidget, 1, 0)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.mediaStatusChanged.connect(self.statusChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)

        mainFrame = QFrame()
        self.setCentralWidget(mainFrame)

        mainLayout = QHBoxLayout()
        mainFrame.setLayout(mainLayout)

        firstFrame = QFrame()
        firstFrame.setFixedWidth(400)
        firstFrame.setLayout(playLayout)
        mainLayout.addWidget(firstFrame)

        # secondFrame = QFrame()
        mainLayout.addWidget(self.videoWidget)

        self.endPos = -1

    def open(self):
        if not self.currentFilePath:
            f = open(self.configFile)
            self.savedFilePath = f.read()
            f.close()
            self.currentFilePath = self.savedFilePath

        fn, _ = QFileDialog.getOpenFileName(
                self, 
                "Open File...", 
                self.currentFilePath, 
                "All Files (*)")

        if fn:
            self.currentFilePath = os.path.dirname(fn)
            if self.currentFilePath != self.savedFilePath:
                f = open(self.configFile, "w")
                f.write(self.currentFilePath)
                print("write file")
                f.close()
                self.savedFilePath = self.currentFilePath

            self.load(fn)
            self.setWindowTitle(
                    "Language Learning Machine: " + os.path.basename(fn))

        self.textEdit.setFocus()

    def load(self, fn):
        self.playButton.setText("play")
        self.playButton.setEnabled(True)
        self.playState = "Stop"
        self.stopButton.setEnabled(False)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fn)))

    def exit(self):
        self.close()

    def clear(self):
        pass

    def next(self):
        if self.playToEnd:
            self.endPos = self.mediaPlayer.position()
            self.mediaPlayer.setPosition(self.beginPos)
            self.playToEnd = False
        else:
            self.beginPos = self.endPos
            self.endPos = self.duration
            self.mediaPlayer.setPosition(self.beginPos)
            self.playToEnd = True

        self.textEdit.setFocus()

    def play(self):
        if self.playState == "Stop":
            self.mediaPlayer.play()
            self.playButton.setText("pause")
            self.stopButton.setEnabled(True)
            self.playState = "Play"
            self.nextButton.setEnabled(True)
            print(self.playState)
        elif self.playState == "Play":
            self.mediaPlayer.pause()
            self.playButton.setText("play")
            self.stopButton.setUpdatesEnabled(True)
            self.playState = "Pause"
            print(self.playState)
        elif self.playState == "Pause":
            self.mediaPlayer.play()
            self.playButton.setText("pause")
            self.stopButton.setUpdatesEnabled(True)
            self.playState = "Play"
            self.nextButton.setEnabled(True)
            print(self.playState)

        self.textEdit.setFocus()

    def statusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.playState = "Stop"
            self.stopButton.setEnabled(False)
            self.playButton.setText("play")
            self.nextButton.setEnabled(False)
            self.mediaPlayer.setPosition(self.beginPos)
            self.play()
        elif status == QMediaPlayer.InvalidMedia:
            self.playState = "Null"
            self.stopButton.setEnabled(False)
            self.playButton.setEnabled(False)
            self.nextButton.setEnabled(False)

    def durationChanged(self, duration):
        self.duration = duration
        # self.slider.setMaximum(duration/1000)
        self.hSlider.setRange(0, duration)

        self.playToEnd = True
        self.beginPos = 0
        self.endPos = self.duration

    def positionChanged(self, progress):
        if self.endPos == -1:
            self.playToEnd = True
            self.beginPos = 0
            self.endPos = self.mediaPlayer.duration()
        self.hSlider.setValue(progress)
        if progress > self.endPos:
            self.mediaPlayer.setPosition(self.beginPos)

    def stop(self):
        self.mediaPlayer.stop()
        self.playButton.setText("play")
        self.playState = "Stop"
        self.stopButton.setEnabled(False)
        self.nextButton.setEnabled(False)

        self.playToEnd = True
        self.beginPos = 0
        self.endPos = self.duration

        print(self.playState)
        self.textEdit.setFocus()

    def creatMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.openAct = QAction("O&pen", self, triggered=self.open)
        self.fileMenu.addAction(self.openAct)
        self.exitAct = QAction("Ex&it", self, triggered=self.exit)
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.clearAct = QAction("C&lear", self, triggered=self.clear)
        self.editMenu.addAction(self.clearAct)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.resize(QSize(900, 600))
    mainWindow.show()

    sys.exit(app.exec_())
