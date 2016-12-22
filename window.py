#! python3
#File: window.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: December 2016
"""

import sys
import grav.db as db
from grav.nodeImg import NodeImg
from PyQt4.QtCore import(Qt, QCoreApplication, QRectF, QLineF, QPointF,
QSignalMapper)
from PyQt4.QtGui import(QIcon, QFont, QPainter, QMainWindow, QApplication,
QWidget, QDesktopWidget, QToolTip, QPushButton, QMessageBox, QAction, qApp,
QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QTextEdit, QTableView,
QPen, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
QGraphicsLineItem, QGraphicsSimpleTextItem, QMenu)


class Window(QMainWindow):
    # Implements a window widget displaying nodes in the database

    def __init__(self):
        # Initialization from superclass and call to class constructor
        super(Window, self).__init__()
        # Create the Brain that is shown in window
        self.brain = db.Brain()
        # Define active node
        self.activeNodeID = 30
        # Define pin nodes
        self.pinNodeIDs = []
        # Define history nodes
        self.historyNodeIDs = []
        # Initialize the window user interface
        self.initUI()

    def initUI(self, labelText=None):
        # Sets window geometry and features.
        # Set basic config of window
        self.resize(1000, 800)
        self.center()
        self.setWindowTitle('Grav\'s window')
        self.setWindowIcon(QIcon('web.png'))
        # Set up actions for window
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
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

        # Create the scene and the view
        self.sceneNetwork = QGraphicsScene()
        self.view = QGraphicsView(self.sceneNetwork)

        # Create the pin scene and view
        self.scenePins = QGraphicsScene()
        self.viewPins = QGraphicsView(self.scenePins)
        # Show the pins
        #self.renderNetwork()

        # Create the history scene and view
        self.sceneHistory = QGraphicsScene()
        self.viewHistory = QGraphicsView(self.sceneHistory)

        # Create a central widget of the main window with a stretch
        # factor layout, and include the view from above
        stretchBox = QWidget()

        viewPane = QVBoxLayout()
        viewPane.addWidget(self.viewPins)
        viewPane.addStretch(1)
        viewPane.addWidget(self.view)
        viewPane.addStretch(1)
        viewPane.addWidget(self.viewHistory)

        hbox = QHBoxLayout()
        self.textEdit = QTextEdit()
        hbox.addWidget(self.textEdit)
        hbox.addStretch(1)
        hbox.addLayout(viewPane)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        lineEdit3 = QLineEdit()
        vbox.addWidget(lineEdit3)

        # Next hbox within vbox and make vbox the central
        stretchBox.setLayout(vbox)
        self.setCentralWidget(stretchBox)

        # Display the node tree, the pins and the history
        self.setActiveNode(nodeID=self.activeNodeID)
        self.renderPins()
        self.historyNodeImgs = []
        #self.renderHistory()

        # Display the window
        self.show()

    def setActiveNode(self, nodeID=1):
        self.activeNodeID = nodeID
        self.activeLinks = db.linksDBModel(self.activeNodeID, dirs=[1, 2, 3])
        self.destNodeIDs = self.activeLinks.destNodeIDs()
        # THIS SECTION UNDER DEV - ADDING CODE FOR DIFFERENT DIRECTIONS
        self.activeLinks_dir1 = db.linksDBModel(self.activeNodeID, dirs=[1])
        self.destNodeIDs_dir1 = self.activeLinks_dir1.destNodeIDs()
        self.activeLinks_dir2 = db.linksDBModel(self.activeNodeID, dirs=[2])
        self.destNodeIDs_dir2 = self.activeLinks_dir2.destNodeIDs()
        self.activeLinks_dir3 = db.linksDBModel(self.activeNodeID, dirs=[3])
        self.destNodeIDs_dir3 = self.activeLinks_dir3.destNodeIDs()
        # Create list of elements for future deletion
        self.networkElements = []
        self.removeImgSet(self.networkElements, self.sceneNetwork)
        # NOW CREATE A DIR-SPECIFIC renderNetwork FUNCTION AND IMPLEMENT IT HERE
        self.renderNetwork()
        self.renderNotes()

    # UNDER DEVELOPMENT!
    def renderNetwork(self):
        # Add the active node image into the scene
        self.activeNodeImg = self.addNode(
            name='activeNodeImg',
            nodeID=self.activeNodeID,
            scene=self.sceneNetwork,
            centerX=500,
            centerY=400
        )
        self.networkElements.append(self.activeNodeImg)
        # Add sibling node images into the scene
        relationTop = 275
        self.activeLinkNodeImgs = []
        for i in range(len(self.destNodeIDs)):
            linkNodeImg = self.addNode(
                name='activeLinkNodeImg_'+str(i),
                nodeID=self.destNodeIDs[i],
                scene=self.sceneNetwork,
                centerX=800,
                centerY=relationTop+60*i
            )
            self.activeLinkNodeImgs.append(linkNodeImg)
            self.networkElements.append(linkNodeImg)
        # Add link images into the scene
        self.activeLinkImgs = []
        for i in range(len(self.destNodeIDs)):
            linkImg = self.addLink(
                scene=self.sceneNetwork,
                nodeImg1=self.activeNodeImg,
                anchor1=self.activeNodeImg.sourceAnchor,
                nodeImg2=self.activeLinkNodeImgs[i],
                anchor2=self.activeLinkNodeImgs[i].destAnchor
            )
            self.activeLinkImgs.append(linkImg)
            self.networkElements.append(linkImg)

    def renderNotes(self):
        self.notesDBModel = db.notesDBModel(self.activeNodeID)
        self.textEdit.setText(
            self.notesDBModel.modelNotes.record(0).value('body').toString()
        )

    def renderPins(self):
        # Add the pin node images into the scene
        self.pinNodeImgs = []
        for i in range(len(self.pinNodeIDs)):
            pinNodeImg = self.addNode(
                name='pinNodeImg_'+str(i),
                nodeID=self.pinNodeIDs[i],
                scene=self.scenePins,
                centerX=110*i,
                centerY=0
            )
            self.pinNodeImgs.append(pinNodeImg)

    def renderHistoryNodes(self):
        # Add the pin node images into the scene
        self.historyNodeImgs = []
        for i in range(len(self.historyNodeIDs)):
            historyNodeImg = self.addNode(
                name='historyNodeImg_'+str(i),
                nodeID=self.historyNodeIDs[i],
                scene=self.sceneHistory,
                centerX=-110*i,
                centerY=0
            )
            self.historyNodeImgs.append(historyNodeImg)

    def removeImgSet(self, imgSet, scene):
        for img in imgSet:
            # Remove chldren of active images from scene
            for child in img.childItems():
                scene.removeItem(child)
                del child
            # Remove active images themselves from scene
            scene.removeItem(img)
            del img

    def addPin(self, nodeID):
        self.pinNodeIDs.append(nodeID)
        self.removeImgSet(self.pinNodeImgs, self.scenePins)
        self.renderPins()

    def addHistoryNode(self, nodeID):
        self.historyNodeIDs.append(nodeID)
        self.removeImgSet(self.historyNodeImgs, self.sceneHistory)
        self.renderHistoryNodes()

    def addNode(self, name, nodeID, scene, centerX=0, centerY=0,
                width=100, height=50):
        # Add the node graphic and set properties
        node = NodeImg(self, name, nodeID, centerX, centerY,
        width, height)
        node.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemSendsScenePositionChanges
            )
        scene.addItem(node)
        # Add the text and set it as child of the node graphic
        text = scene.addText(
            node.nodeDBModel.model.record(0).value('ID').toString() + '\n\n' +
            node.nodeDBModel.model.record(0).value('name').toString()
        )
        text.setPos(node.centerX-node.width/2+5,
        node.centerY-node.height/2)
        text.setParentItem(node)
        # Return the pointer for the node
        return node

    def addLink(self, scene, nodeImg1, anchor1, nodeImg2, anchor2):
        # Add the link graphic
        linkImg = scene.addLine(
            nodeImg1.centerX+anchor1.xOffset, nodeImg1.centerY+anchor1.yOffset,
            nodeImg2.centerX+anchor2.xOffset, nodeImg2.centerY+anchor2.yOffset,
            QPen(Qt.black, 1, Qt.SolidLine)
        )
        linkImg.nodeAtWhichEnd = {}
        nodeImg1.addLine(linkImg, nodeImg1.name+"-"+nodeImg2.name, 'p1')
        nodeImg2.addLine(linkImg, nodeImg1.name+"-"+nodeImg2.name, 'p2')
        # Return the pointer for the link
        return linkImg

    def center(self):
        # Centers window in desktop
        frame = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(centerPoint)
        self.move(frame.topLeft())

    def closeEvent(self, event):
        # Redefines superclass close event with a message box to confirm quit
        reply = QMessageBox.question(self, 'Confirm exit',
        'Are you sure you want to quit?', QMessageBox.Yes |
        QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


#Code to make module into script-----------
if __name__ == "__main__":

    app = QApplication(sys.argv)
    newWindow = Window()
    sys.exit(app.exec_())

#------------------------------------------
# Secret message: Genie is great
