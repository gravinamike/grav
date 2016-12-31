#! python3
#File: nodeImg.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: December 2016
"""

import grav.db as db
from PyQt4.QtCore import(QLineF, QPointF, QSignalMapper)
from PyQt4.QtGui import(QAction, QLineEdit, QGraphicsItem, QGraphicsRectItem,
QMenu)


class NodeImg(QGraphicsRectItem):
    # A graphical representation of a node, referring to a database model which
    # defines text and links with other nodes. Adds connecting-lines
    # functionality to basic rectangle graphic class

    def __init__(self, window, name, nodeID=1, dir=0, centerX=0, centerY=0, width=100,
                height=50):
        # Initialization from superclass and call to class constructor
        super(NodeImg, self).__init__(centerX-width/2, centerY-height/2, width,
        height)

        # Define basic attributes of node graphic
        self.name = name
        self.nodeID = nodeID
        self.dir = dir
        self.window = window

        # Define geometry of node graphic and link anchors
        self.centerX, self.centerY = centerX, centerY
        self.width, self.height = width, height
        self.leftAnchor = self.Anchor(self.width/-2, 0)
        self.rightAnchor = self.Anchor(self.width/2, 0)
        self.topAnchor = self.Anchor(0, self.height/-2)
        self.bottomAnchor = self.Anchor(0, self.height/2)

        # Instantiate node graphic DB model
        self.nodeDBModel = db.nodeDBModel(nodeID)

        # Create an empty array for holding the node's linked lines
        self.lines = {}

    def addLine(self, line, name, p1orP2, dirFromNode):
        # Links a line object and line properties to the rectangle
        line.name = name
        line.dirFromNode = dirFromNode
        line.nodeAtWhichEnd.update({self.name: p1orP2})
        self.lines.update({name: line})

    def itemChange(self, change, value):
        # Reinstantiates itemChange method to call endpoint-mover method
        if (change == QGraphicsItem.ItemPositionChange):
            newPos = value.toPointF()
            for lineName in self.lines.keys():
                for line in self.lines.values():
                    self.moveLineEndpoint(newPos, lineName,
                    line.nodeAtWhichEnd[self.name])
        return QGraphicsItem.itemChange(self, change, value)

    def moveLineEndpoint(self, newPos, lineName, p1orP2):
        # Moves line endpoint when associated node is moved

        # Determines the relevant anchor and offsets of the moving node image
        if self.dir == 0:
            if self.lines[lineName].dirFromNode == 1:
                dirAnchor = self.bottomAnchor
            elif self.lines[lineName].dirFromNode == 2:
                dirAnchor = self.topAnchor
            elif self.lines[lineName].dirFromNode == 3:
                dirAnchor = self.rightAnchor
        elif self.dir == 1:
            dirAnchor = self.topAnchor
        elif self.dir == 2:
            dirAnchor = self.bottomAnchor
        elif self.dir == 3:
            dirAnchor = self.leftAnchor
        xOffset = self.centerX + dirAnchor.xOffset
        yOffset = self.centerY + dirAnchor.yOffset
        newMovingPointPos = QPointF(newPos.x()+xOffset, newPos.y()+yOffset)

        # Sets line geometry depending on which point is being moved
        if p1orP2 == 'p1':
            stayingPointPos = self.lines[lineName].line().p2()
            self.lines[lineName].setLine(QLineF(newMovingPointPos,
            stayingPointPos))
        elif p1orP2 == 'p2':
            stayingPointPos = self.lines[lineName].line().p1()
            self.lines[lineName].setLine(QLineF(stayingPointPos,
            newMovingPointPos))

    def mouseDoubleClickEvent(self, event):
        # On double-click, sets the node as active and increments history
        self.window.setActiveNode(self.nodeID)
        self.window.addHistoryNode(self.nodeID)

    def contextMenuEvent(self, event):
        # Defines right-click menu and associated actions

        # Create the menu object
        menu = QMenu()

        # A test action
        testAction = QAction('Test', None)
        testAction.triggered.connect(self.print_out)
        menu.addAction(testAction)

        # Action to add a pin
        self.addPinAction = QAction('Add to pins', None)
        signalMapper = QSignalMapper()
        self.addPinAction.triggered.connect(signalMapper.map)
        signalMapper.setMapping(self.addPinAction, int(self.nodeID))
        signalMapper.mapped.connect(self.window.addPin)
        menu.addAction(self.addPinAction)

        # Displays the menu
        menu.exec_(event.screenPos())

    def print_out(self):
        # Prints out the word "Triggered"
        print 'Triggered', str(self.nodeID)

    class Anchor:
        # Defines an anchor for the node with two offsets
        def __init__(self, xOffset, yOffset):
            self.xOffset = xOffset
            self.yOffset = yOffset
