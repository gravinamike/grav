#! python3
#File: window.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: December 2016
"""

import sys
import math
import grav.db as db
from grav.nodeImg import NodeImg
from grav.htmlParse import htmlParse
from PyQt4.QtCore import(Qt, QSignalMapper)
from PyQt4.QtGui import(QIcon, QMainWindow, QApplication, QWidget, QPushButton,
QDesktopWidget, QMessageBox, QAction, qApp, QHBoxLayout, QVBoxLayout, QLineEdit,
QTextEdit, QPen, QFont, QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu)


class Window(QMainWindow):
    # Implements a window widget displaying nodes in the database

    def __init__(self):
        # Initialization from superclass and call to class constructor
        super(Window, self).__init__()
        # Initialize Brain that is shown in window
        self.brain = db.Brain(self)
        # Define active node of network, pin nodes, history nodes
        self.activeNodeID = 30
        self.pinNodeIDs = []
        self.historyNodeIDs = []
        # Initialize the window user interface
        self.initUI()

    def initUI(self, labelText=None):
        # Sets window geometry and features.

        # Set basic config of window
        self.resize(2000, 1500)
        self.center()
        self.setWindowTitle('The Bridge')
        self.setWindowIcon(QIcon('web.png'))
        # Set up actions associated with window
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        # Set up window bars (menu, tool, status)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.statusBar().showMessage('Ready')
        # Set size of node images
        self.nodeImgWidth = 100
        self.nodeImgHeight = 50
        self.nodeImgTextSize = 12

        # Create the network scene, view and element list for later deletion
        self.sceneNetwork = QGraphicsScene()
        self.view = QGraphicsView(self.sceneNetwork)
        self.networkElements = []
        #self.sceneNetwork.setSceneRect(0, 0, 1000, 1000)

        # Create the pin scene/view
        self.scenePins = QGraphicsScene()
        self.viewPins = QGraphicsView(self.scenePins)

        # Create the history scene/view
        self.sceneHistory = QGraphicsScene()
        self.viewHistory = QGraphicsView(self.sceneHistory)

        # Create the notes pane
        notesBox = QVBoxLayout()
        self.textEdit = QTextEdit()
        self.saveNotesButton = QPushButton('Save notes')
        self.saveNotesButton.clicked.connect(self.saveNotes)
        notesBox.addWidget(self.saveNotesButton)
        notesBox.addWidget(self.textEdit)

        # Create the node attribute pane
        attribBox = QHBoxLayout()
        lineEdit3 = QLineEdit()

        self.biggerButton = QPushButton('Bigger')
        self.biggerButtonMapper = QSignalMapper()
        self.biggerButton.clicked.connect(self.biggerButtonMapper.map)
        self.biggerButtonMapper.setMapping(self.biggerButton, 1)
        self.biggerButtonMapper.mapped.connect(self.updateNodeImgSize)

        self.smallerButton = QPushButton('Smaller')
        self.smallerButtonMapper = QSignalMapper()
        self.smallerButton.clicked.connect(self.smallerButtonMapper.map)
        self.smallerButtonMapper.setMapping(self.smallerButton, -1)
        self.smallerButtonMapper.mapped.connect(self.updateNodeImgSize)

        attribBox.addWidget(lineEdit3)
        attribBox.addWidget(self.biggerButton)
        attribBox.addWidget(self.smallerButton)

        # Set main-widget box/stretch layout using the above views
        # Network pane
        viewPane = QVBoxLayout()
        viewPane.addWidget(self.viewPins)
        viewPane.addWidget(self.view)
        viewPane.addWidget(self.viewHistory)
        # Network/notes pane
        hbox = QHBoxLayout()
        hbox.addLayout(notesBox)
        hbox.addLayout(viewPane)
        # Network/notes/attribute pane
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(attribBox)
        # Encapsulating widget
        stretchBox = QWidget()
        stretchBox.setLayout(vbox)
        self.setCentralWidget(stretchBox)

        # Display the network, pins, and history
        self.setActiveNode(nodeID=self.activeNodeID)
        self.renderPins()
        self.historyNodeImgs = []
        #self.renderHistoryNodes()

        # Display the window
        self.show()

    def setActiveNode(self, nodeID=1):
        # Set the active node and re-display the network accordingly

        # Reassign active node ID
        self.activeNodeID = nodeID

        # Create destNodeID lists for each direction from the active node
        self.activeLinks_dir1 = db.LinksDBModel(self.activeNodeID, dirs=[1])
        self.destNodeIDs_dir1 = self.activeLinks_dir1.destNodeIDs()
        self.activeLinks_dir2 = db.LinksDBModel(self.activeNodeID, dirs=[2])
        self.destNodeIDs_dir2 = self.activeLinks_dir2.destNodeIDs()
        self.activeLinks_dir3 = db.LinksDBModel(self.activeNodeID, dirs=[3])
        self.destNodeIDs_dir3 = self.activeLinks_dir3.destNodeIDs()

        # Remove the old network, refresh element list, and render everything
        self.removeImgSet(self.networkElements, self.sceneNetwork)
        self.networkElements = []
        self.renderNetwork(dirs=[1, 2, 3])
        self.renderNotes()

    def renderNetwork(self, dirs=[1, 2, 3]):
        # Render the node network on the main view

        # Set network geometry
        self.networkCenterX = 500
        self.networkCenterY = 400
        self.relationOrbit = 300

        # Add active node image into the scene
        self.activeNodeImg = self.addNode(
            name='activeNodeImg',
            nodeID=self.activeNodeID,
            scene=self.sceneNetwork,
            centerX=self.networkCenterX,
            centerY=self.networkCenterY,
            width=self.nodeImgWidth,
            height=self.nodeImgHeight,
            textSize=self.nodeImgTextSize
        )
        self.networkElements.append(self.activeNodeImg)

        # Add relation node/link images into the scene for each direction
        self.activeLinkNodeImgs = {}
        for dir in dirs:
            # Add node images into the scene for this direction
            linkNodeImgs_thisDir = []
            destNodeIDs = eval('self.destNodeIDs_dir'+str(dir))
            for i in range(len(destNodeIDs)):
                if dir == 1:
                    relationStartLimit = self.networkCenterX - \
                    self.nodeImgWidth*0.55*(len(destNodeIDs)-1)
                    centerX = relationStartLimit+self.nodeImgWidth*1.1*i
                    centerY = self.networkCenterY+self.relationOrbit
                elif dir == 2:
                    relationStartLimit = self.networkCenterX - \
                    self.nodeImgWidth*0.55*(len(destNodeIDs)-1)
                    centerX = relationStartLimit+self.nodeImgWidth*1.1*i
                    centerY = self.networkCenterY-self.relationOrbit
                elif dir == 3:
                    relationStartLimit = self.networkCenterY - \
                    self.nodeImgHeight*0.55*(len(destNodeIDs)-1)
                    centerX = self.networkCenterX+self.relationOrbit
                    centerY = relationStartLimit+self.nodeImgHeight*1.1*i
                linkNodeImg = self.addNode(
                    name='activeLinkNodeImg_dir'+str(dir)+'_'+str(i),
                    nodeID=destNodeIDs[i],
                    scene=self.sceneNetwork,
                    dir=dir,
                    centerX=centerX,
                    centerY=centerY,
                    width=self.nodeImgWidth,
                    height=self.nodeImgHeight,
                    textSize=self.nodeImgTextSize
                )
                linkNodeImgs_thisDir.append(linkNodeImg)
                self.activeLinkNodeImgs.update({str(dir): linkNodeImgs_thisDir})
                self.networkElements.append(linkNodeImg)

            # Add link images into the scene for this direction
            self.activeLinkImgs = []
            for i in range(len(destNodeIDs)):
                if dir == 1:
                    anchor1=self.activeNodeImg.bottomAnchor
                    anchor2=self.activeLinkNodeImgs[str(dir)][i].topAnchor
                elif dir == 2:
                    anchor1=self.activeNodeImg.topAnchor
                    anchor2=self.activeLinkNodeImgs[str(dir)][i].bottomAnchor
                elif dir == 3:
                    anchor1=self.activeNodeImg.rightAnchor
                    anchor2=self.activeLinkNodeImgs[str(dir)][i].leftAnchor
                linkImg = self.addLink(
                    scene=self.sceneNetwork,
                    nodeImg1=self.activeNodeImg,
                    anchor1=anchor1,
                    nodeImg2=self.activeLinkNodeImgs[str(dir)][i],
                    anchor2=anchor2
                )
                self.activeLinkImgs.append(linkImg)
                self.networkElements.append(linkImg)

    def renderNotes(self):
        # Render the notes for the active node
        self.notesDBModel = db.NotesDBModel(self, self.activeNodeID)
        self.textEdit.setText(
            self.notesDBModel.modelNotes.record(0).value('body').toString()
        )

    def saveNotes(self):
        # Save the notes for the active node
        notesText = htmlParse(self.textEdit.toHtml())
        #notesText = self.textEdit.toHtml()
        self.brain.saveNotes(notesText)
        self.renderNotes()

    def renderPins(self):
        # Add the pin node images into the scene
        self.pinNodeImgs = []
        for i in range(len(self.pinNodeIDs)):
            pinNodeImg = self.addNode(
                name='pinNodeImg_'+str(i),
                nodeID=self.pinNodeIDs[i],
                scene=self.scenePins,
                centerX=self.nodeImgWidth*i*1.1,
                centerY=0,
                width=self.nodeImgWidth,
                height=self.nodeImgHeight,
                textSize=self.nodeImgTextSize
            )
            self.pinNodeImgs.append(pinNodeImg)

    def renderHistoryNodes(self):
        # Add the history node images into the scene
        self.historyNodeImgs = []
        for i in range(len(self.historyNodeIDs)):
            historyNodeImg = self.addNode(
                name='historyNodeImg_'+str(i),
                nodeID=self.historyNodeIDs[i],
                scene=self.sceneHistory,
                centerX=-self.nodeImgWidth*i*1.1,
                centerY=0,
                width=self.nodeImgWidth,
                height=self.nodeImgHeight,
                textSize=self.nodeImgTextSize
            )
            self.historyNodeImgs.append(historyNodeImg)

    def removeImgSet(self, imgSet, scene):
        # Remove active images and their children from the specified scene
        for img in imgSet:
            for child in img.childItems():
                scene.removeItem(child)
                del child
            scene.removeItem(img)
            del img

    def addPin(self, nodeID):
        # Add a pin to the pin view
        self.pinNodeIDs.append(nodeID)
        self.removeImgSet(self.pinNodeImgs, self.scenePins)
        self.renderPins()

    def addHistoryNode(self, nodeID):
        # Add a history node to the history view
        self.historyNodeIDs.append(nodeID)
        self.removeImgSet(self.historyNodeImgs, self.sceneHistory)
        self.renderHistoryNodes()

    def addNode(self, name, nodeID, scene, dir=0, centerX=0, centerY=0,
                width=100, height=50, textSize=12):
        # Add a node image into the specified scene

        # Initialize the node graphic and properties
        node = NodeImg(self, name, nodeID, dir, centerX, centerY,
        width, height)
        node.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemSendsScenePositionChanges
            )
        scene.addItem(node)

        # Initialize the anchor graphics and set as children of node graphics
        for anchor in node.anchors:
            scene.addItem(anchor)
            anchor.setFlags(QGraphicsItem.ItemIsSelectable)
            anchor.setParentItem(node)

        # Add text and set it as child of the node graphic
        node.text = scene.addText(
            node.nodeDBModel.model.record(0).value('name').toString() + '\n' +
            node.nodeDBModel.model.record(0).value('ID').toString()
        )
        node.text.setTextWidth(width*0.9)
        font = QFont('Arial')
        font.setPixelSize(textSize)
        node.text.setFont(font)
        node.text.setPos(   node.centerX-node.width/2+5,
                            node.centerY-node.height/2)
        node.text.setParentItem(node)

        # Return the node's pointer
        return node

    def addLink(self, scene, nodeImg1, anchor1, nodeImg2, anchor2):
        # Add a link image into the network scene

        # Add link graphic to scene and set attributes
        linkImg = scene.addLine(
            nodeImg1.centerX+anchor1.xOffset, nodeImg1.centerY+anchor1.yOffset,
            nodeImg2.centerX+anchor2.xOffset, nodeImg2.centerY+anchor2.yOffset,
            QPen(Qt.black, 1, Qt.SolidLine)
        )
        linkImg.nodeAtWhichEnd = {}

        # Add lines to the node image's list of lines
        nodeImg1.addLine(linkImg, nodeImg1.name+"-"+nodeImg2.name, 'p1',
            nodeImg1.dir)
        nodeImg2.addLine(linkImg, nodeImg1.name+"-"+nodeImg2.name, 'p2',
            nodeImg2.dir)

        # Return pointer for the link
        return linkImg

    def updateNodeImgSize(self, scaleFactorExp):
        # Change the size of node images and text

        # Set size of window-level node image size parameters
        scaleFactor = 1.2**scaleFactorExp
        self.nodeImgWidth = self.nodeImgWidth*scaleFactor
        self.nodeImgHeight = self.nodeImgHeight*scaleFactor
        self.nodeImgTextSize = self.nodeImgTextSize*scaleFactor

        # Set size of node images
        self.removeImgSet(self.networkElements, self.sceneNetwork)
        self.networkElements = []
        self.renderNetwork(dirs=[1, 2, 3])
        self.removeImgSet(self.pinNodeImgs, self.scenePins)
        self.renderPins()
        self.removeImgSet(self.historyNodeImgs, self.sceneHistory)
        self.renderHistoryNodes()

    def center(self):
        # Center window in desktop
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

    def exitCleanup(self):
        # Final cleanup if window is closed, including shutting down the db
        self.brain.h2.kill()
        print "Database killed!"


#Code to make module into script-----------
if __name__ == "__main__":

    app = QApplication(sys.argv)
    newWindow = Window()
    app.aboutToQuit.connect(newWindow.exitCleanup)
    sys.exit(app.exec_())

#------------------------------------------
# Secret message: Genie is great
