#! python3
#File: nodeImg.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: December 2016
"""

import sys
import grav.db as db
from PyQt4.QtCore import(Qt, QCoreApplication, QRectF, QLineF, QPointF,
QSignalMapper)
from PyQt4.QtGui import(QIcon, QFont, QPainter, QMainWindow, QApplication,
QWidget, QDesktopWidget, QToolTip, QPushButton, QMessageBox, QAction, qApp,
QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QTextEdit, QTableView,
QPen, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
QGraphicsLineItem, QGraphicsSimpleTextItem, QMenu)


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
        self.window.removeImgSet(self.window.networkElements,
            self.window.sceneNetwork)
        self.window.setActiveNode(self.nodeID)
        self.window.renderNetwork()
        self.window.addHistoryNode(self.nodeID)

    def contextMenuEvent(self, event):
        menu = QMenu()

        testAction = QAction('Test', None)
        testAction.triggered.connect(self.print_out)
        menu.addAction(testAction)

        self.addPinAction = QAction('Add to pins', None)
        signalMapper = QSignalMapper()
        self.addPinAction.triggered.connect(signalMapper.map)
        signalMapper.setMapping(self.addPinAction, self.nodeID)
        signalMapper.mapped.connect(self.window.addPin)
        menu.addAction(self.addPinAction)

        menu.exec_(event.screenPos())

    def print_out(self):
        print 'Triggered'

    class Anchor:
        def __init__(self, xOffset, yOffset):
            self.xOffset = xOffset
            self.yOffset = yOffset
