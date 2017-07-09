#! python3
#File: axisHandle.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: February 2017
"""

from PyQt4 import QtCore, QtGui

class AxisHandlePole(QtGui.QGraphicsEllipseItem):
    # A graphical representation of one isolated polarity of an axis

    def __init__(self, window, name, axisDir=0, centerX=0, centerY=0,
                width=100, height=100):
        # Initialization from superclass and call to class constructor
        super(AxisHandlePole, self).__init__(centerX-width/2, centerY-height/2,
        width, height)

        # Define basic attributes of graphic
        self.name = name
        self.axisDir = axisDir
        self.window = window

        # Define geometry of graphic
        self.centerX, self.centerY = centerX, centerY

    def mouseDoubleClickEvent(self, event):
        # On double-click, ######################
        pass

    def contextMenuEvent(self, event):
        # Defines right-click menu and associated actions

        # Create the menu object
        menu = QtGui.QMenu()

        # Create an action for each available axis direction
        self.axisDirectionsIDs, self.axisDirectionsOpposites, \
        self.axisDirectionsTexts = self.window.axisDirectionsIDs, \
        self.window.axisDirectionsOpposites, self.window.axisDirectionsTexts
        self.dirActions = []
        self.signalMappers = []
        for row in range(len(self.axisDirectionsIDs)):
            self.dirActions.append(QtGui.QAction(
            self.axisDirectionsTexts[row], None))
            self.signalMappers.append(QtCore.QSignalMapper())
            self.dirActions[row].triggered.connect(self.signalMappers[row].map)
            self.signalMappers[row].setMapping(self.dirActions[row], row)
            self.signalMappers[row].mapped.connect(self.assignAxis)
            menu.addAction(self.dirActions[row])

        # Displays the menu
        menu.exec_(event.screenPos())

    def assignAxis(self, row):
        # Passes choice from context menu onto window's axis-assignment method
        assignedDir = self.axisDirectionsIDs[row]
        self.window.assignAxis(self.axisDir, assignedDir)


class AxisHandleLong(QtGui.QGraphicsRectItem):
    # A graphical representation of one polarity of an axis related to another

    def __init__(self, window, name, axisDir=0, centerX=0, centerY=0,
                width=10, height=10):
        # Initialization from superclass and call to class constructor
        super(AxisHandleLong, self).__init__(centerX-width/2, centerY-height/2,
        width, height)

        # Define basic attributes of graphic
        self.name = name
        self.axisDir = axisDir
        self.window = window

        # Define geometry of graphic
        self.centerX, self.centerY = centerX, centerY

    def mouseDoubleClickEvent(self, event):
        # On double-click, ######################
        pass

    def contextMenuEvent(self, event):
        # Defines right-click menu and associated actions

        # Create the menu object
        menu = QtGui.QMenu()

        # Create an action for each available axis direction
        self.dirActions = []
        self.signalMappers = []
        for row in range(len(self.window.axisDirectionsIDs)):
            self.dirActions.append(QtGui.QAction(self.window.axisDirectionsTexts[row],
            None))
            self.signalMappers.append(QtCore.QSignalMapper())
            self.dirActions[row].triggered.connect(self.signalMappers[row].map)
            self.signalMappers[row].setMapping(self.dirActions[row], row)
            self.signalMappers[row].mapped.connect(self.assignAxisAndOpposite)
            menu.addAction(self.dirActions[row])

        # Displays the menu
        menu.exec_(event.screenPos())

    def assignAxisAndOpposite(self, row):
        # Passes choice from context menu onto window's axis-assignment method
        assignedDir = self.window.axisDirectionsIDs[row]
        oppositeDir = self.window.axisDirectionsOpposites[row]
        self.window.assignAxisAndOpposite(self.axisDir, assignedDir,
        oppositeDir)
