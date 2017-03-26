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
from grav.axes import(AxisHandleLong, AxisHandlePole)
from grav.textEdit import TextEdit
from grav.htmlParse import htmlParse
from PyQt4.QtCore import(Qt, QSignalMapper, QPointF)
from PyQt4.QtGui import(QIcon, QMainWindow, QApplication, QWidget, QPushButton,
QDesktopWidget, QMessageBox, QAction, qApp, QHBoxLayout, QVBoxLayout, QLineEdit,
QTextEdit, QPen, QFont, QGraphicsView, QGraphicsScene, QGraphicsItem, QMenu,
QGraphicsRectItem, QTableView)


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
        # Set relationship directions to each view axis
        self.axisDirections = db.AxisDirectionsDBModel(1, 2, 3, 4)
        self.axisAssignments = {'1': 1, '2': 2, '3': 3, '4': 4}
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
        #self.sceneNetwork.setSceneRect(0, 0, 800, 600)
        self.view = QGraphicsView(self.sceneNetwork)
        self.view.setMinimumWidth(800)
        self.view.setMinimumHeight(600)
        self.networkElements = []
        self.directionElements = []

        # Create the pin scene/view
        self.scenePins = QGraphicsScene()
        self.viewPins = QGraphicsView(self.scenePins)

        # Create the history scene/view
        self.sceneHistory = QGraphicsScene()
        self.viewHistory = QGraphicsView(self.sceneHistory)

        # Create the direction table portal and direction-add/remove buttons
        self.tableDirections = QTableView()
        self.tableDirections.setModel(self.brain.modelDirections)
        #self.tableDirections.setColumnHidden(0, True)
        self.tableDirections.setColumnWidth(1, 170)
        self.tableDirections.setColumnWidth(2, 170)
        self.tableDirections.setColumnWidth(3, 170)

        self.buttonAddDir = QPushButton('Add direction')
        self.buttonAddDir.clicked.connect(self.brain.createDirection)
        self.buttonDelDir = QPushButton('Delete direction')
        self.buttonDelDir.clicked.connect(self.brain.deleteDirection)

        self.directionsBox = QVBoxLayout()
        self.directionsBox.addWidget(self.tableDirections)
        self.directionsBox.addWidget(self.buttonAddDir)
        self.directionsBox.addWidget(self.buttonDelDir)

        # Create the axis-direction-setting view
        self.sceneDirections = QGraphicsScene()
        self.sceneDirections.setSceneRect(-200, -200, 400, 400)
        self.viewDirections = QGraphicsView(self.sceneDirections)
        self.viewDirections.setFixedSize(400, 400)
        self.viewDirections.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viewDirections.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
        attribBox.addLayout(self.directionsBox)
        attribBox.addWidget(self.viewDirections)

        # Set main-widget box/stretch layout using the above views
        # Network pane
        viewPane = QVBoxLayout()
        viewPane.addWidget(self.viewPins)
        viewPane.addWidget(self.view)
        viewPane.addWidget(self.viewHistory)
        # Network/notes pane
        hbox = QHBoxLayout()
        self.notesEditor = TextEdit(self)
        hbox.addWidget(self.notesEditor)
        hbox.addLayout(viewPane)
        # Network/notes/attribute pane
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(attribBox)
        # Encapsulating widget
        stretchBox = QWidget()
        stretchBox.setLayout(vbox)
        self.setCentralWidget(stretchBox)

        # Display the network, pins, history and direction-selector
        self.setActiveNode(nodeID=self.activeNodeID)
        self.renderPins()
        self.historyNodeImgs = []
        self.renderDirections(self.sceneDirections)
        #self.renderHistoryNodes()

        # Display the window
        self.show()

    def assignAxis(self, axisDir, assignedDir):
        self.axisAssignments[str(axisDir)] = assignedDir
        self.renderDirections(self.sceneDirections)
        self.setActiveNode(self.activeNodeID)

    def assignAxisAndOpposite(self, axisDir, assignedDir, oppositeDir):
        self.axisAssignments[str(axisDir)] = assignedDir
        axisOppositeDirs = {'1': 2, '2': 1, '3': 4, '4': 3}
        self.axisAssignments[str(axisOppositeDirs[str(axisDir)])] = oppositeDir
        self.renderDirections(self.sceneDirections)
        self.setActiveNode(self.activeNodeID)

    def renderDirections(self, scene):
        # Render the directions-selection dummy axes

        # Clear out the old directions scene
        self.removeImgSet(self.directionElements, self.sceneDirections)
        self.directionElements = []

        # Specify and render the polar axis handles
        handleInfo = [['1', 1, 0, 150], ['2', 2, 0, -150], ['3', 3, 150, 0],
        ['4', 4, -150, 0]]

        for name, axisDir, centerX, centerY in handleInfo:
            axisHandlePole = AxisHandlePole(self, name, axisDir, centerX,
            centerY, 50, 50)
            scene.addItem(axisHandlePole)
            self.directionElements.append(axisHandlePole)

        # Specify and render the long axis handles
        handleInfo = [['1-2', 1, 0, 75, 10, 100], ['2-1', 2, 0, -75, 10, 100],
        ['3-4', 3, 75, 0, 100, 10], ['4-3', 4, -75, 0, 100, 10]]

        for name, axisDir, centerX, centerY, width, height in handleInfo:
            axisHandleLong = AxisHandleLong(self, name, axisDir, centerX,
            centerY, width, height)
            scene.addItem(axisHandleLong)
            self.directionElements.append(axisHandleLong)

        # Render the central square
        centerSquare = QGraphicsRectItem(-25, -25, 50, 50)
        scene.addItem(centerSquare)
        self.directionElements.append(centerSquare)

        # Render the text
        pixelSize = 12
        model = self.axisDirections.model
        axisTexts = {
        'Down': [None, 20+pixelSize/2, 30, 90],
        'Up': [None, -20-pixelSize/2, -30, -90],
        'Right': [None, 30, -20-pixelSize/2, 0],
        'Left': [None, -30, 35-pixelSize/2, 180]
        }
        axisDirToRelationDir = {'Down': 1, 'Up': 2, 'Right': 3, 'Left': 4}
        for key in axisTexts.keys():
            for row in range(0, model.rowCount()):
                if int(model.record(row).value(
                'id').toString()) == self.axisAssignments[str(
                axisDirToRelationDir[key])]:
                    axisTexts[key][0] = str(model.record(row).value(
                    'text').toString())

        font = QFont('Arial', weight=75)
        font.setPixelSize(pixelSize)
        for key in axisTexts.keys():
            text = self.sceneDirections.addText(axisTexts[key][0])
            self.directionElements.append(text)
            text.setTextWidth(100)
            text.setFont(font)
            text.setPos(axisTexts[key][1], axisTexts[key][2])
            text.rotate(axisTexts[key][3])

    def setActiveNode(self, nodeID=1):
        # Set the active node and re-display the network accordingly

        # Reassign active node ID
        self.activeNodeID = nodeID

        # Create destNodeID lists for each direction from the active node
        self.activeLinks_dir1 = db.LinksDBModel(self.activeNodeID,
        dirs=[self.axisAssignments['1']])
        self.destNodeIDs_dir1 = self.activeLinks_dir1.destNodeIDs()
        self.activeLinks_dir2 = db.LinksDBModel(self.activeNodeID,
        dirs=[self.axisAssignments['2']])
        self.destNodeIDs_dir2 = self.activeLinks_dir2.destNodeIDs()
        self.activeLinks_dir3 = db.LinksDBModel(self.activeNodeID,
        dirs=[self.axisAssignments['3']])
        self.destNodeIDs_dir3 = self.activeLinks_dir3.destNodeIDs()
        self.activeLinks_dir4 = db.LinksDBModel(self.activeNodeID,
        dirs=[self.axisAssignments['4']])
        self.destNodeIDs_dir4 = self.activeLinks_dir4.destNodeIDs()

        # Remove the old network, refresh element list, and render everything
        self.removeImgSet(self.networkElements, self.sceneNetwork)
        self.networkElements = []
        self.renderNetwork(dirs=[1, 2, 3])
        self.renderNotes()

    def renderNetwork(self, dirs=[1, 2, 3, 4]):
        # Render the node network on the main view

        # Set network geometry
        self.networkCenterX = 500
        self.networkCenterY = 500
        self.relationOrbit = 200

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

        # Add relation node/link images into the scene for each axis direction
        axisDirectionMultipliers = {'1': ['X', 0, 1], '2': ['X', 0, -1],
        '3': ['Y', 1, 0], '4': ['Y', -1, 0]}
        self.activeLinkNodeImgs = {}
        for axisDir in [1, 2, 3, 4]:
            # Add node images into the scene for this axis direction
            linkNodeImgs_thisAxisDir = []
            destNodeIDs = eval('self.destNodeIDs_dir'+str(axisDir))
            startLimitAxis, xSign, ySign = axisDirectionMultipliers[str(
            axisDir)]

            for i in range(len(destNodeIDs)):
                if startLimitAxis == 'X':
                    relationStartLimit = self.networkCenterX - \
                    self.nodeImgWidth*0.55*(len(destNodeIDs)-1)
                    centerX = relationStartLimit + self.nodeImgWidth*1.1*i
                    centerY = self.networkCenterY + ySign*self.relationOrbit
                elif startLimitAxis == 'Y':
                    relationStartLimit = self.networkCenterY - \
                    self.nodeImgHeight*0.55*(len(destNodeIDs)-1)
                    centerX = self.networkCenterX + xSign*self.relationOrbit
                    centerY = relationStartLimit + self.nodeImgHeight*1.1*i

                linkNodeImg = self.addNode(
                    name='activeLinkNodeImg_dir'+str(axisDir)+'_'+str(i),
                    nodeID=destNodeIDs[i],
                    scene=self.sceneNetwork,
                    dir=axisDir,
                    centerX=centerX,
                    centerY=centerY,
                    width=self.nodeImgWidth,
                    height=self.nodeImgHeight,
                    textSize=self.nodeImgTextSize
                )
                linkNodeImgs_thisAxisDir.append(linkNodeImg)
                self.activeLinkNodeImgs.update(
                {str(axisDir): linkNodeImgs_thisAxisDir})
                self.networkElements.append(linkNodeImg)

            # Add link images into the scene for this direction
            self.activeLinkImgs = []
            for i in range(len(destNodeIDs)):
                if axisDir == 1:
                    anchor1=self.activeNodeImg.bottomAnchor
                    anchor2=self.activeLinkNodeImgs[str(axisDir)][i].topAnchor
                elif axisDir == 2:
                    anchor1=self.activeNodeImg.topAnchor
                    anchor2=self.activeLinkNodeImgs[str(
                    axisDir)][i].bottomAnchor
                elif axisDir == 3:
                    anchor1=self.activeNodeImg.rightAnchor
                    anchor2=self.activeLinkNodeImgs[str(axisDir)][i].leftAnchor
                elif axisDir == 4:
                    anchor1=self.activeNodeImg.leftAnchor
                    anchor2=self.activeLinkNodeImgs[str(axisDir)][i].rightAnchor
                linkImg = self.addLink(
                    scene=self.sceneNetwork,
                    nodeImg1=self.activeNodeImg,
                    anchor1=anchor1,
                    nodeImg2=self.activeLinkNodeImgs[str(axisDir)][i],
                    anchor2=anchor2
                )
                self.activeLinkImgs.append(linkImg)
                self.networkElements.append(linkImg)

    def renderNotes(self):
        # Render the notes for the active node
        self.notesDBModel = db.NotesDBModel(self, self.activeNodeID)
        self.notesEditor.text.setText(
            self.notesDBModel.modelNotes.record(0).value('body').toString()
        )

    def saveNotes(self):
        # Save the notes for the active node
        notesText = htmlParse(self.notesEditor.text.toHtml())
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
