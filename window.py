#! python3
#File: window.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: December 2016
"""

import sys
import grav.db as db
from PyQt4.QtCore import(Qt, QCoreApplication, QRectF, QLineF, QPointF)
from PyQt4.QtGui import(QIcon, QFont, QPainter, QMainWindow, QApplication,
QWidget, QDesktopWidget, QToolTip, QPushButton, QMessageBox, QAction, qApp,
QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QTextEdit, QTableView,
QPen, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
QGraphicsLineItem, QGraphicsSimpleTextItem)


class NodeImg(QGraphicsRectItem):
    # A graphical representation of a node containing a database model which
    # defines text and links with other nodes.
    # Subclasses the rectangle graphic to have connected lines

    def __init__(self, window, name, nodeID=1, centerX=0, centerY=0, width=100,
                height=50):
        # Initialization from superclass and call to class constructor
        super(NodeImg, self).__init__(centerX-width/2, centerY-height/2, width,
        height)
        # Define node graphic basic info
        self.name = name
        self.nodeID = nodeID
        self.window = window
        # Define node graphic geometry
        self.centerX, self.centerY = centerX, centerY
        self.width, self.height = width, height
        self.sourceAnchor = self.Anchor(self.width/2, 0)
        self.destAnchor = self.Anchor(self.width/-2, 0)
        # Define DB model for node
        self.nodeDBModel = db.nodeDBModel(nodeID)
        # Create an empty array for holding the node's linked lines
        self.lines = {}

    def changeDimensions(self, width, height):
        self.width, self.height = width, height
        self.sourceAnchor = self.Anchor(self.width/2, 0)
        self.destAnchor = self.Anchor(self.width/-2, 0)

    def addLine(self, line, name, p1orP2):
        # Links a line object to the rectangle and indicates whether the
        # rectangle is at point 1 or point 2 of the line
        line.name = name
        line.nodeAtWhichEnd.update({self.name: p1orP2})
        self.lines.update({name: line})

    def itemChange(self, change, value):
        if (change == QGraphicsItem.ItemPositionChange):
            newPos = value.toPointF()
            for lineName in self.lines.keys():
                for line in self.lines.values():
                    self.moveLineEndpoint(newPos, lineName,
                    line.nodeAtWhichEnd[self.name])
        return QGraphicsItem.itemChange(self, change, value)

    def moveLineEndpoint(self, newPos, lineName, p1orP2):
        if p1orP2 == 'p1':
            xOffset = self.centerX + self.sourceAnchor.xOffset
            yOffset = self.centerY + self.sourceAnchor.yOffset
            newEndpointPos = QPointF(newPos.x()+xOffset,
            newPos.y()+yOffset)
            p1 = newEndpointPos
            p2 = self.lines[lineName].line().p2()
        else:
            xOffset = self.centerX + self.destAnchor.xOffset
            yOffset = self.centerY + self.destAnchor.yOffset
            newEndpointPos = QPointF(newPos.x()+xOffset,
            newPos.y()+yOffset)
            p1 = self.lines[lineName].line().p1()
            p2 = newEndpointPos
        self.lines[lineName].setLine(QLineF(p1, p2))

    def mouseDoubleClickEvent(self, event):
        self.window.removeNetwork()
        self.window.changeActiveNode(self.nodeID)
        self.window.renderNetwork()

    class Anchor:
        def __init__(self, xOffset, yOffset):
            self.xOffset = xOffset
            self.yOffset = yOffset


class Window(QMainWindow):
    # Implements a window widget displaying nodes in the database

    def __init__(self):
        # Initialization from superclass and call to class constructor
        super(Window, self).__init__()
        # Define Brain that is shown in window
        self.brain = db.Brain()
        # Define active node
        self.activeNodeID = 30
        # Define link nodes
        self.activeLinks = db.linksDBModel()
        self.activeLinks.setActiveNode(self.activeNodeID)
        self.destNodeIDs = self.activeLinks.destNodeIDs()
        # Initialize the window user interface
        self.initUI()

    def initUI(self, labelText=None):
        # Window constructor. Sets window geometry, window title, window icon,
        # menu bar, tool bar, status bar, tool tip, and quit button. Creates
        # the display object.
        # Set basic config of window
        self.resize(1000, 800)
        self.center()
        # You can handle the size/position like this too:
        # self.setGeometry(300, 300, 300, 220)
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
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        # Show the node tree
        self.renderNetwork()
        # Set central widget to be the view
        self.setCentralWidget(self.view)
        # Display the window
        self.show()

    def renderNetwork(self):
        # Add the active node image into the scene
        self.activeNodeImg = self.addNode(name='activeNodeImg',
        nodeID=self.activeNodeID, centerX=500, centerY=400)
        # Add sibling node images into the scene
        relationTop = 275
        self.activeLinkNodeImgs = []
        for i in range(len(self.destNodeIDs)):
            linkNodeImg = self.addNode(
                name='activeLinkNodeImg_'+str(i),
                nodeID=self.destNodeIDs[i],
                centerX=800,
                centerY=relationTop+60*i
            )
            self.activeLinkNodeImgs.append(linkNodeImg)
        # Add link images into the scene
        self.activeLinkImgs = []
        for i in range(len(self.destNodeIDs)):
            linkImg = self.addLink(
                nodeImg1=self.activeNodeImg,
                anchor1=self.activeNodeImg.sourceAnchor,
                nodeImg2=self.activeLinkNodeImgs[i],
                anchor2=self.activeLinkNodeImgs[i].destAnchor
            )
            self.activeLinkImgs.append(linkImg)

    def removeNetwork(self):
        # Remove active node image from the scene
        for child in self.activeNodeImg.childItems():
            self.scene.removeItem(child)
            del child
        self.scene.removeItem(self.activeNodeImg)
        del self.activeNodeImg
        # Remove sibling node images from the scene
        for i in self.activeLinkNodeImgs:
            for child in i.childItems():
                self.scene.removeItem(child)
                del child
            self.scene.removeItem(i)
            del i
        # Remove link images from the scene
        for i in self.activeLinkImgs:
            for child in i.childItems():
                self.scene.removeItem(child)
                del child
            self.scene.removeItem(i)
            del i

    def addNode(self, name, nodeID, centerX=0, centerY=0, width=100, height=50):
        # Add the node graphic and set properties
        node = NodeImg(self, name, nodeID, centerX, centerY,
        width, height)
        node.setFlag(QGraphicsItem.ItemIsSelectable)
        node.setFlag(QGraphicsItem.ItemIsMovable)
        node.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.scene.addItem(node)
        # Add the text and set it as child of the node graphic
        text = self.scene.addText(
            node.nodeDBModel.model.record(0).value('ID').toString() + '\n\n' +
            node.nodeDBModel.model.record(0).value('name').toString()
        )
        text.setPos(node.centerX-node.width/2+5,
        node.centerY-node.height/2)
        text.setParentItem(node)
        # Return the pointer for the node
        return node

    def addLink(self, nodeImg1, anchor1, nodeImg2, anchor2):
        # Add the link graphic
        linkImg = self.scene.addLine(
            nodeImg1.centerX+anchor1.xOffset, nodeImg1.centerY+anchor1.yOffset,
            nodeImg2.centerX+anchor2.xOffset, nodeImg2.centerY+anchor2.yOffset,
            QPen(Qt.black, 1, Qt.SolidLine)
        )
        linkImg.nodeAtWhichEnd = {}
        nodeImg1.addLine(linkImg, nodeImg1.name+"-"+nodeImg2.name, 'p1')
        nodeImg2.addLine(linkImg, nodeImg1.name+"-"+nodeImg2.name, 'p2')
        # Return the pointer for the link
        return linkImg

    def changeActiveNode(self, nodeID=1):
        self.activeNodeID = nodeID
        self.activeLinks.setActiveNode(self.activeNodeID)
        self.destNodeIDs = self.activeLinks.destNodeIDs()

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
