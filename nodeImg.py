#! python3
#File: nodeImg.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: December 2016
"""

import grav.db as db
from PyQt4.QtCore import(Qt, QLineF, QPointF, QSignalMapper, QMimeData)
from PyQt4.QtGui import(QAction, QLineEdit, QGraphicsItem, QGraphicsRectItem,
QGraphicsEllipseItem, QMenu, QDrag, QPen, QCursor, qApp)


class NodeImg(QGraphicsRectItem):
    # A graphical representation of a node, referring to a database model which
    # defines text and links with other nodes. Adds connecting-lines
    # functionality to basic rectangle graphic class

    def __init__(self, window, name, nodeID=1, dir=0, centerX=0, centerY=0,
                width=100, height=50):
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
        self.leftAnchor = Anchor(self.window, self, 4, self.width/-2, 0)
        self.rightAnchor = Anchor(self.window, self, 3, self.width/2, 0)
        self.topAnchor = Anchor(self.window, self, 2, 0, self.height/-2)
        self.bottomAnchor = Anchor(self.window, self, 1, 0, self.height/2)
        self.anchors = [self.leftAnchor, self.rightAnchor, self.topAnchor,
                        self.bottomAnchor]

        # Instantiate node graphic DB model
        self.nodeDBModel = db.NodeDBModel(nodeID)

        # Create an empty array for holding the node's linked lines
        self.lines = {}

    def addLine(self, line, name, p1orP2, dirFromNode):
        # Links a line object and line properties to the rectangle
        line.name = name
        #line.dirFromNode = dirFromNode
        if p1orP2 == 'p1':
            line.dirFromNodeP1 = dirFromNode
        elif p1orP2 == 'p2':
            line.dirFromNodeP2 = dirFromNode
        line.nodeAtWhichEnd.update({self.name: p1orP2})
        self.lines.update({name: line})

    def itemChange(self, change, value):
        # Reinstantiates itemChange method to call endpoint-mover method
        if (change == QGraphicsItem.ItemPositionChange):
            newPos = value.toPointF()
            for lineName, line in self.lines.iteritems():
                self.moveLineEndpoint(newPos, lineName,
                line.nodeAtWhichEnd[self.name])
        return QGraphicsItem.itemChange(self, change, value)

    def moveLineEndpoint(self, newPos, lineName, p1orP2):
        # Moves line endpoint when associated node is moved

        # Determines the relevant anchor and offsets of the moving node image.
        dirAnchors = {2: self.topAnchor, 1: self.bottomAnchor,
        4: self.leftAnchor, 3: self.rightAnchor}
        if self.lines[lineName].nodeAtWhichEnd[self.name] == 'p1':
            dirAnchor = dirAnchors[self.lines[lineName].dirFromNodeP1]
        elif self.lines[lineName].nodeAtWhichEnd[self.name] == 'p2':
            dirAnchor = dirAnchors[self.lines[lineName].dirFromNodeP2]
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
        signalMapper1 = QSignalMapper()
        self.addPinAction.triggered.connect(signalMapper1.map)
        signalMapper1.setMapping(self.addPinAction, int(self.nodeID))
        signalMapper1.mapped.connect(self.window.addPin)
        menu.addAction(self.addPinAction)

        # Action to delete this node
        self.deleteAction = QAction('Delete node', None)
        signalMapper2 = QSignalMapper()
        self.deleteAction.triggered.connect(signalMapper2.map)
        signalMapper2.setMapping(self.deleteAction, int(self.nodeID))
        signalMapper2.mapped.connect(self.window.brain.deleteRelation)
        menu.addAction(self.deleteAction)

        # Displays the menu
        menu.exec_(event.screenPos())

    def print_out(self, fake):
        # Prints out the word "Triggered"
        print 'Triggered', str(self.nodeID)


class Anchor(QGraphicsEllipseItem):
    # Defines an anchor for the node with two offsets

    def __init__(self, window, node, dir, xOffset, yOffset):
        # Define anchor graphic's parameters
        self.window = window
        self.node = node
        self.dir = dir
        oppositeDirs = {1: 2, 2: 1, 3: 4, 4: 3}
        self.oppositeDir = oppositeDirs[self.dir]
        self.direction = self.window.axisAssignments[str(self.dir)]
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.dragLink = None
        self.dragCircle = None

        # Initialization from superclass and call to class constructor
        super(Anchor, self).__init__(-5, -5, 10, 10)
        self.setPos(self.node.centerX + self.xOffset,
        self.node.centerY + self.yOffset)

        self.setAcceptDrops(True)

    def mouseDoubleClickEvent(self, event):
        # On double-click, open dialog to create a new relation node
        self.window.brain.createRelation(self.node.nodeID, self.direction, None)

    def mouseMoveEvent(self, event):
        # Reimplements mouseMoveEvent to drag out a line which can be used to
        # form a new link with mouseReleaseEvent

        # Screen out all but left-click movements
        if event.buttons() != Qt.LeftButton:
            return

        # If beginning a drag, create a new line and circle
        if self.dragLink == None:
            self.dragLink = self.window.sceneNetwork.addLine(
                self.scenePos().x(), self.scenePos().y(), event.scenePos().x(),
                event.scenePos().y(), QPen(Qt.black, 1, Qt.SolidLine)
            )
            self.dragCircle = QGraphicsEllipseItem(-5, -5, 10, 10)
            self.dragCircle.setPos(event.scenePos().x(),
            event.scenePos().y())
            self.window.sceneNetwork.addItem(self.dragCircle)
        # If a drag is in progress...
        else:
            # ...move the existing line and circle to the mouse cursor
            self.dragLink.setLine(QLineF(self.scenePos().x(), self.scenePos().y(),
            event.scenePos().x(), event.scenePos().y()))
            self.dragCircle.setPos(event.scenePos().x(),
            event.scenePos().y())
            # ...if you did move the line and circle, if there is an
            # opposite anchor under the mouse, make the lasso circle bigger,
            # otherwise make it small
            anchor = False
            for x in self.window.sceneNetwork.collidingItems(self.dragCircle):
                if isinstance(x, Anchor):
                    anchor = x
            if anchor and anchor.dir == self.oppositeDir:
                self.dragCircle.setRect(-10, -10, 20, 20)
            else:
                self.dragCircle.setRect(-5, -5, 10, 10)

    def mouseReleaseEvent(self, event):
        # If in a mouse drag from mouseMoveEvent, and hovering over a node's
        # anchor, makes a link from one node to another.

        # If the line already exists,
        if self.dragLink != None:

            # If there is an anchor under the mouse, call the linkgen method
            for x in self.window.sceneNetwork.collidingItems(self.dragCircle):
                if isinstance(x, Anchor):
                    anchor = x
                    self.window.brain.createRelationship(self.node.nodeID,
                    self.direction, anchor.node.nodeID, anchor.direction, None)

            # Remove the line and circle now that the mouse is released
            self.window.sceneNetwork.removeItem(self.dragLink)
            self.dragLink = None
            self.window.sceneNetwork.removeItem(self.dragCircle)
            self.dragCircle = None
