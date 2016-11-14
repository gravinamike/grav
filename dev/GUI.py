#! python3
#File: GUI.py

"""
Currently test code to learn GUI programming through PyQt.
Based on code found at http://zetcode.com/gui/pyqt5/menustoolbars/

author: Mike Gravina
last edited: August 2016
"""

import sys
from PyQt5.QtWidgets import(QApplication, QWidget, QDesktopWidget, QToolTip,
QPushButton, QMessageBox, QMainWindow, QAction, qApp, QLabel, QHBoxLayout,
QVBoxLayout, QGridLayout, QLineEdit, QTextEdit)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication

# A QWidget is a less specific form of window - QMainWindow has menubars, etc.
class Window(QMainWindow):
    
    def __init__(self):
        # Initialization from superclass and call to class constructor
        super().__init__()
    
        self.initUI()
    
    
    def initUI(self):
        """ Window class constructor. Sets window geometry, window title,
        window icon, menu bar, tool bar, status bar, tool tip, and quit
        button. Creates the display object."""
        
        # Set basic config of window
        self.resize(300, 300)
        self.center()
        # You can handle the size/position like this too:
        # self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Grav\'s window')
        self.setWindowIcon(QIcon('web.png'))
        
        # Set up window-wide tooltip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This is <b>Grav\'s</b> window.')
        
        # Set up actions for window
        exitAction = QAction(QIcon('exit24.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        
        # Set up menu bar, tool bar, status bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        
        self.statusBar().showMessage('Ready')        
        
        # Create a quit button
        quitButton = QPushButton('Quit', self)
        quitButton.clicked.connect(QCoreApplication.instance().quit)
        quitButton.resize(quitButton.sizeHint())
        quitButton.move(50, 100)
        quitButton.setToolTip('This is a quit button.')
        
        # Create an independently positioned label
        label1 = QLabel('Grav', self)
        label1.move(50, 150)
        
        # Create a grid layout widget
        grid = QGridLayout()
        grid.setSpacing(10)
        
        gridNames = ['11', '', '', '14',
                     '21', '', '23', 'Grav',
                     '?', '', '33', '34']

        positions = [ (i,j) for i in range(3) for j in range (4)]
        
        for position, name in zip(positions, gridNames):
            if name == '':
                continue
            button = QPushButton(name)
            grid.addWidget(button, *position)
            
        lineEdit = QLineEdit()
        textEdit = QTextEdit()
        
        grid.addWidget(lineEdit, 0, 1)
        grid.addWidget(textEdit, 1, 1, 2, 1)
        
        gridBox = QWidget()
        gridBox.setLayout(grid)
        
        # Create a central widget of the main window with a stretch
        # factor layout, and include the grid layout from above
        stretchBox = QWidget()
        
        upButton = QPushButton('Up')
        downButton = QPushButton('Down')
        
        hbox = QHBoxLayout()
        hbox.addWidget(gridBox)
        hbox.addStretch(1)
        hbox.addWidget(upButton)
        hbox.addWidget(downButton)
        
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        
        stretchBox.setLayout(vbox)
        
        self.setCentralWidget(stretchBox)
        
        #Display the window
        self.show()
    
    def closeEvent(self, event):
        
        # Redefines superclass close event with a message box to confirm quit
        reply = QMessageBox.question(self, 'Confirm exit',
        'Are you sure you want to quit?', QMessageBox.Yes |
        QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        
        # Centers window in desktop
        frame = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(centerPoint)
        self.move(frame.topLeft())

        
#Code to make module into script-----------
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    newWindow = Window()
    sys.exit(app.exec_())
#------------------------------------------
