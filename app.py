import asyncio
import sys, os

from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from qasync import QEventLoop, QApplication, asyncSlot

import autoplay
from autoplay import DATA

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll
    windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.myproduct.subproduct.version')
except ImportError:
    pass

class MainWindow(QWidget):
    default_text = "All credits to <a href=\"https://discordapp.com/users/_amphibi_\" style=\"color: cyan\">Amphibi</a>"
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("BeatBangerAuto")
        self.setWindowIcon(QIcon(os.path.join(basedir, "images", "windowIcon.png")))
        self.setFixedSize(260, 64)
        self.setLayout(QHBoxLayout())

        self.label = QLabel(self)
        self.label.setText(MainWindow.default_text)
        self.label.setOpenExternalLinks(True)                   
        self.layout().addWidget(self.label)

        self.button = QPushButton(self)
        self.button.setFixedSize(38, 38)
        self.button.setIcon(QIcon(os.path.join(basedir, "images", "buttonOff.png")))
        self.button.setIconSize(QSize(38, 38))
        self.button.clicked.connect(self.executeScript)
        self.layout().addWidget(self.button)
        
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                color: white;
                
                font-family: Brush Script MT;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        
        autoplay.signal = self

    @asyncSlot()
    async def changeText(self, text):
        if DATA['ENABLE_AUTOPLAY']:
            self.label.setText(text)
        
    @asyncSlot()
    async def disableScript(self, text = ""):
        DATA['ENABLE_AUTOPLAY'] = False
        self.label.setText(text if text != "" else MainWindow.default_text)
        self.button.setIcon(QIcon(os.path.join(basedir, "images", "buttonOff.png")))
    
    @asyncSlot()
    async def executeScript(self):
        DATA['ENABLE_AUTOPLAY'] = not DATA['ENABLE_AUTOPLAY']
        if DATA['ENABLE_AUTOPLAY']:
            asyncio.create_task(autoplay.connect())
        if not DATA['ENABLE_AUTOPLAY']:
            self.label.setText(MainWindow.default_text)
        self.button.setIcon(QIcon(os.path.join(basedir, "images", "{}.png".format('buttonOn' if DATA['ENABLE_AUTOPLAY'] else 'buttonOff'))))

if __name__ == "__main__":
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    main_window = MainWindow()
    main_window.show()

    with loop:
        sys.exit(loop.run_forever())