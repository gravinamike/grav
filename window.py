#! python3
#File: window.py

"""
This is the main script for Seahorse which instantiates a window allowing you
to display and edit a multidimensional network of nodes.

author: Mike Gravina
last edited: April 2017
"""

import sys
import math
import grav.db as db
import grav.nodeImg # Absolute import to avoid circularities with nodeImg
from grav import axes, htmlParse, networkPortal, textEdit
from PyQt4 import QtCore, QtGui


class Window(QtGui.QMainWindow):
    # Seahorse main window

    def __init__(self):
        super(Window, self).__init__()

        # Initialize the window user interface
        self.initUI()

        # Initialize Brain database
        self.h2 = db.openH2()
        self.openDatabase(
        '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

    def initUI(self, labelText=None):
        # Set window geometry and features

        # Set basic config of window
        self.resize(2000, 1500)
        self.center()
        self.setWindowTitle('Seahorse')
        self.setWindowIcon(QtGui.QIcon('seahorse.png'))

        # Set up actions associated with window
        openAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open database')
        openAction.triggered.connect(self.openDialog)

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        # Set up window bars (menu, tool, status)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.statusBar().showMessage('Ready')

        # Create network scene, view and element lists for later deletion
        self.viewNetwork = networkPortal.NetworkPortal(self)
        self.viewNetwork.setMinimumWidth(800)
        self.viewNetwork.setMinimumHeight(600)
        self.directionElements = []

        # Create pin scene/view
        self.scenePins = QtGui.QGraphicsScene()
        self.viewPins = QtGui.QGraphicsView(self.scenePins)

        # Create history scene/view
        self.sceneHistory = QtGui.QGraphicsScene()
        self.viewHistory = QtGui.QGraphicsView(self.sceneHistory)

        """# Create direction table portal and direction-add/remove buttons
        self.tableDirections = QtGui.QTableView()
        self.tableDirections.setColumnWidth(1, 170)
        self.tableDirections.setColumnWidth(2, 170)
        self.tableDirections.setColumnWidth(3, 170)"""
        self.tableDirections = QtGui.QLineEdit()

        self.buttonAddDir = QtGui.QPushButton('Add direction')
        self.buttonDelDir = QtGui.QPushButton('Delete direction')
        # Signal-slot connnections handled in openDatabase method

        self.directionsBox = QtGui.QVBoxLayout()
        self.directionsBox.addWidget(self.tableDirections)
        self.directionsBox.addWidget(self.buttonAddDir)
        self.directionsBox.addWidget(self.buttonDelDir)

        # Create axis-direction-setting view
        self.sceneDirections = QtGui.QGraphicsScene()
        self.sceneDirections.setSceneRect(-200, -200, 400, 400)
        self.viewDirections = QtGui.QGraphicsView(self.sceneDirections)
        self.viewDirections.setFixedSize(400, 400)
        self.viewDirections.setHorizontalScrollBarPolicy(
        QtCore.Qt.ScrollBarAlwaysOff)
        self.viewDirections.setVerticalScrollBarPolicy(
        QtCore.Qt.ScrollBarAlwaysOff)

        # Create node attribute pane
        attribBox = QtGui.QHBoxLayout()
        lineEdit3 = QtGui.QLineEdit()

        self.biggerButton = QtGui.QPushButton('Bigger')
        self.biggerButtonMapper = QtCore.QSignalMapper()
        self.biggerButton.clicked.connect(self.biggerButtonMapper.map)
        self.biggerButtonMapper.setMapping(self.biggerButton, 1)
        self.biggerButtonMapper.mapped.connect(self.updateNodeImgSize)

        self.smallerButton = QtGui.QPushButton('Smaller')
        self.smallerButtonMapper = QtCore.QSignalMapper()
        self.smallerButton.clicked.connect(self.smallerButtonMapper.map)
        self.smallerButtonMapper.setMapping(self.smallerButton, -1)
        self.smallerButtonMapper.mapped.connect(self.updateNodeImgSize)

        attribBox.addWidget(lineEdit3)
        attribBox.addWidget(self.biggerButton)
        attribBox.addWidget(self.smallerButton)
        attribBox.addLayout(self.directionsBox)
        attribBox.addWidget(self.viewDirections)

        # Set main-widget box/stretch layout using the above views
        # Network pane
        viewPane = QtGui.QVBoxLayout()
        viewPane.addWidget(self.viewPins)
        viewPane.addWidget(self.viewNetwork)
        viewPane.addWidget(self.viewHistory)
        # Notes pane
        notesPane = QtGui.QVBoxLayout()
        self.editButton = QtGui.QPushButton('Edit/read-only')
        self.editButton.setCheckable(True)
        self.notesEditor = textEdit.TextEdit(self)
        self.notesEditor.text.textChanged.connect(self.markNotesChanges)
        self.editButton.clicked.connect(self.notesEditor.setReadOnly)
        notesPane.addWidget(self.notesEditor)
        notesPane.addWidget(self.editButton)
        # Network/notes pane
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(notesPane)
        hbox.addLayout(viewPane)
        # Network/notes/attribute pane
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(attribBox)
        # Encapsulating widget
        stretchBox = QtGui.QWidget()
        stretchBox.setLayout(vbox)
        self.setCentralWidget(stretchBox)

        # Display the window
        self.show()

    def openDatabase(self, filename):

        # Set active node of network, pin nodes, history nodes
        self.startingNodeID = 30
        self.pinNodeIDs = []
        self.historyNodeIDs = []
        # Set null link portal
        self.linkPortal = None
        # Set size of node images
        self.nodeImgWidth = 100
        self.nodeImgHeight = 50
        self.nodeImgTextSize = 12

        # Open the database
        #self.brain = db.Brain(self, filename) #TODO Get rid of this!

        # Set relationship directions to each view axis, and their opposites
        self.axisDirectionsIDs, self.axisDirectionsOpposites, self.axisDirectionsTexts = db.axisDirectionsInfo(self, 1, 2, 3, 4)
        self.axisAssignments = {1: 1, 2: 2, 3: 3, 4: 4}
        self.axisAssignmentOpposites = {}
        self.getAxisAssignmentOpposites()
        # Set dictionary of linkIDs and their opposite linkIDs
        self.oppositeLinkIDs = {}

        """self.tableDirections.setModel(self.brain.modelDirections)"""

        self.buttonAddDir.clicked.connect(db.createDirection)
        self.buttonDelDir.clicked.connect(db.deleteDirection)

        # Display the network, pins, history and direction-selector
        self.viewNetwork.setActiveNode(nodeID=self.startingNodeID)
        self.renderPins()
        self.historyNodeImgs = []
        self.renderDirections(self.sceneDirections)

    def openDialog(self):

        # Get filename and show only .db files
        self.filename = QtGui.QFileDialog.getOpenFileName(self,
        'Open File',".","(*.db)")

        print self.filename

        if self.filename:
            self.brain.close()
            self.openDatabase(self.filename)

    def assignAxis(self, axisDir, assignedDir):
        # Assigns a unidirectional axis of the view to a database direction
        self.axisAssignments[axisDir] = assignedDir
        self.getAxisAssignmentOpposites()
        self.renderDirections(self.sceneDirections)
        self.viewNetwork.setActiveNode()

    def assignAxisAndOpposite(self, axisDir, assignedDir, oppositeDir):
        # Assigns a bidirectional axis of the view to a database direction and
        # its opposite
        self.axisAssignments[axisDir] = assignedDir
        axisOppositeDirs = {1: 2, 2: 1, 3: 4, 4: 3}
        self.axisAssignments[axisOppositeDirs[axisDir]] = oppositeDir
        self.getAxisAssignmentOpposites()
        self.renderDirections(self.sceneDirections)
        self.viewNetwork.setActiveNode()

    def getAxisAssignmentOpposites(self):
        # Sets dictionary of direction-axis assignments
        self.axisAssignmentOpposites = {}
        for i in range(len(self.axisDirectionsIDs)):
            for direction in list(set(self.axisAssignments.values())):
                if self.axisDirectionsIDs[i] == direction:
                    opposite = self.axisDirectionsOpposites[i]
                    self.axisAssignmentOpposites.update({direction: opposite})

    def renderDirections(self, scene):
        # Render the directions-selection dummy axes

        # Clear out the old directions scene
        self.removeImgSet(self.directionElements, self.sceneDirections)
        self.directionElements = []

        # Specify and render the polar axis handles
        handleInfo = [['1', 1, 0, 150], ['2', 2, 0, -150], ['3', 3, 150, 0],
        ['4', 4, -150, 0]]

        for name, axisDir, centerX, centerY in handleInfo:
            axisHandlePole = axes.AxisHandlePole(self, name, axisDir, centerX,
            centerY, 50, 50)
            scene.addItem(axisHandlePole)
            self.directionElements.append(axisHandlePole)

        # Specify and render the long axis handles
        handleInfo = [['1-2', 1, 0, 75, 10, 100], ['2-1', 2, 0, -75, 10, 100],
        ['3-4', 3, 75, 0, 100, 10], ['4-3', 4, -75, 0, 100, 10]]

        for name, axisDir, centerX, centerY, width, height in handleInfo:
            axisHandleLong = axes.AxisHandleLong(self, name, axisDir, centerX,
            centerY, width, height)
            scene.addItem(axisHandleLong)
            self.directionElements.append(axisHandleLong)

        # Render the central square
        centerSquare = QtGui.QGraphicsRectItem(-25, -25, 50, 50)
        scene.addItem(centerSquare)
        self.directionElements.append(centerSquare)

        # Render the text
        pixelSize = 12
        axisTexts = {
        'Down': [None, 20+pixelSize/2, 30, 90],
        'Up': [None, -20-pixelSize/2, -30, -90],
        'Right': [None, 30, -20-pixelSize/2, 0],
        'Left': [None, -30, 35-pixelSize/2, 180]
        }
        axisDirToRelationDir = {'Down': 1, 'Up': 2, 'Right': 3, 'Left': 4}
        for key in axisTexts.keys():
            for i in range(len(self.axisDirectionsIDs)):
                if self.axisDirectionsIDs[i] == self.axisAssignments[
                axisDirToRelationDir[key]]:
                    axisTexts[key][0] = self.axisDirectionsTexts[i]

        font = QtGui.QFont('Arial', weight=75)
        font.setPixelSize(pixelSize)
        for key in axisTexts.keys():
            text = self.sceneDirections.addText(axisTexts[key][0])
            self.directionElements.append(text)
            text.setTextWidth(100)
            text.setFont(font)
            text.setPos(axisTexts[key][1], axisTexts[key][2])
            text.rotate(axisTexts[key][3])

    def renderNotes(self):
        # Render the notes for the active node
        self.notesID, notesText = db.notesInfo(self,
        self.viewNetwork.activeNodeID)
        self.notesEditor.text.setText(notesText)
        # Set up the auto-save timer
        self.notesTimer = QtCore.QTimer()
        self.notesTimer.timeout.connect(self.saveNotes)
        self.notesChangedFlag = False
        self.notesTimer.start(10000)

    def markNotesChanges(self):
        # Make a note that the current notes have been edited
        self.notesChangedFlag = True

    def saveNotes(self):
        # Save the notes for the active node
        if self.notesChangedFlag == True:
            notesText = htmlParse.htmlParse(self.notesEditor.text.toHtml())
            db.saveNotes(self.brain, notesText)
            # Set up the auto-save timer
            self.notesTimer = QtCore.QTimer()
            self.notesTimer.timeout.connect(self.saveNotes)
            self.notesChangedFlag = False
            self.notesTimer.start(10000)

    def renderPins(self):
        # Add the pin node images into the scene

        databaseConn = db.Brain2(self,
        '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

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

        databaseConn.close()

    def renderHistoryNodes(self):

        databaseConn = db.Brain2(self,
        '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

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

        databaseConn.close()

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
        node = grav.nodeImg.NodeImg(self, name, nodeID, dir, centerX, centerY,
        width, height)
        node.setFlags(
            QtGui.QGraphicsItem.ItemIsSelectable |
            QtGui.QGraphicsItem.ItemIsMovable |
            QtGui.QGraphicsItem.ItemSendsScenePositionChanges
            )
        scene.addItem(node)

        # Set up signal/slot for clicking on nodes in selection views
        if hasattr(scene, 'role') and scene.role == 'select':
            node.signaler.select.connect(networkPortal.chooseNode)

        # Initialize the anchor graphics and set as children of node graphics
        for anchor in node.anchors:
            scene.addItem(anchor)
            anchor.setFlags(
                QtGui.QGraphicsItem.ItemIsSelectable |
                QtGui.QGraphicsItem.ItemIsMovable|
                QtGui.QGraphicsItem.ItemSendsScenePositionChanges)
            anchor.setParentItem(node)

        # Add text and set it as child of the node graphic
        node.text = scene.addText(node.nodeName + '\n' + str(node.nodeID))
        node.text.setTextWidth(width*0.9)
        font = QtGui.QFont('Arial')
        font.setPixelSize(textSize)
        node.text.setFont(font)
        node.text.setPos(   node.centerX-node.width/2+5,
                            node.centerY-node.height/2)
        node.text.setParentItem(node)

        # Return the node's pointer
        return node

    def addLink(self, scene, linkID_forward, linkID_reverse, nodeImg1, anchor1,
                nodeImg2, anchor2):
        # Add a link image into the network scene

        # Add link ID and its opposite to the opposite-linkIDs dictionary
        self.oppositeLinkIDs.update({linkID_forward: linkID_reverse})

        # Add link graphic to scene and set attributes
        linkImg = grav.nodeImg.RelationshipImg(self, None, linkID_forward,
        linkID_reverse, nodeImg1.centerX+anchor1.xOffset,
        nodeImg1.centerY+anchor1.yOffset, nodeImg2.centerX+anchor2.xOffset,
        nodeImg2.centerY+anchor2.yOffset, QtGui.QPen(QtCore.Qt.black, 1,
        QtCore.Qt.SolidLine))
        scene.addItem(linkImg)
        linkImg.nodeAtWhichEnd = {}

        # Add lines to the node image's list of lines
        nodeImg1.addLine(linkImg, nodeImg1.name+"-"+nodeImg2.name, 'p1',
            anchor1.dir)
        nodeImg2.addLine(linkImg, nodeImg1.name+"-"+nodeImg2.name, 'p2',
            anchor2.dir)

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
        self.removeImgSet(self.viewNetwork.networkElements,
        self.viewNetwork.scene())
        self.viewNetwork.networkElements = []
        self.viewNetwork.renderNetwork(dirs=[1, 2, 3, 4])
        self.removeImgSet(self.pinNodeImgs, self.scenePins)
        self.renderPins()
        self.removeImgSet(self.historyNodeImgs, self.sceneHistory)
        self.renderHistoryNodes()

    def center(self):
        # Center window in desktop
        frame = self.frameGeometry()
        centerPoint = QtGui.QDesktopWidget().availableGeometry().center()
        frame.moveCenter(centerPoint)
        self.move(frame.topLeft())

    def closeEvent(self, event):
        # Redefines superclass close event with a message box to confirm quit
        reply = QtGui.QMessageBox.question(self, 'Confirm exit',
        'Are you sure you want to quit?',
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def print_out(self):
        print 'Report'

    def exitCleanup(self):
        # Final cleanup if window is closed, including saving notes and shutting
        # down the db
        self.saveNotes()
        self.h2.kill()
        print "Database killed!"


#Code to make module into script-----------
if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    newWindow = Window()
    app.aboutToQuit.connect(newWindow.exitCleanup)
    sys.exit(app.exec_())

#------------------------------------------
# Secret message: Genie is great
