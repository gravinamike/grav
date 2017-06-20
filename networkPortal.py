#! python3
#File: networkPortal.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: Jun 2017
"""

import grav.db as db
import grav.nodeImg
from grav import axes, htmlParse, textEdit, nodeimg
from PyQt4 import QtCore, QtGui

class NetworkPortal(QtGui.QGraphicsView):
    # A portal which allows you to see and manipulate a part of the node network

    def __init__(self, interfaceOwner, activeNodeID=1, sizeX=None, sizeY=None,
    posX=None, posY=None, role='main', scrollbars=True, ringCount=3, orbit=200):
        # Initialization from superclass and call to class constructor
        super(NetworkPortal, self).__init__(QtGui.QGraphicsScene())

        # Defining the owner attributes
        self.interfaceOwner = interfaceOwner
        if QtGui.QMainWindow in interfaceOwner.__class__.__bases__:
            self.window = interfaceOwner
        if type(interfaceOwner) == grav.nodeImg.Anchor:
            self.anchor = interfaceOwner
            self.window = interfaceOwner.window

        # Define basic attributes
        self.activeNodeID = activeNodeID
        self.scene().role = role
        self.ringCount = ringCount
        self.orbit = orbit
        self.networkElements = []
        if sizeX != None and sizeY != None and posX != None and posY != None:
            self.scene().setSceneRect(sizeX/-2, sizeY/-2, sizeX, sizeY)
            self.setGeometry(posX-sizeX/2, posY-sizeY/2, sizeX, sizeY)
            self.centerOn(0, 0)
        if scrollbars == False:
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def setActiveNode(self, nodeID=None):
        # Set the active node and re-display the network accordingly

        # Reassign active node ID
        if nodeID == None:
            pass
        else:
            self.activeNodeID = nodeID

        # Remove the old network, refresh element list, and render everything
        self.window.removeImgSet(self.networkElements, self.scene())
        self.networkElements = []
        self.renderNetwork(dirs=[1, 2, 3, 4], ringCount=self.ringCount)
        self.window.renderNotes()

    def renderNetwork(self, dirs=[1, 2, 3, 4], ringCount=3):
        # Render the node network

        centerList = [[0, 0]]
        nodeList = [None]
        self.activeLinkNodeIDs = []
        self.activeLinkNodeImgs = []
        self.oppositeLinkIDs = {}

        for ring in range(0, ringCount):

            nextCenterList = []
            nextNodeList = []

            length = len(centerList)
            for i in range(0, length):
                centerCoords = centerList[i]
                centerNode = nodeList[i]
                newCenters, newNodeIDs, nodeImgs = self.renderOneRing(
                centerCoords, centerNode, ring)
                nextCenterList.extend(newCenters)
                nextNodeList.extend(nodeImgs)

            centerList = nextCenterList
            nodeList = nextNodeList

            nextCenterList = []
            nextNodeList = []

        length = len(centerList)
        for i in range(0, length):
            centerCoords = centerList[i]
            centerNode = nodeList[i]
            self.renderLastLinksRing(centerCoords, centerNode)
        self.scene().update()

    def renderOneRing(self, centerCoords, focusNodeImg, ring):
        # Render a single ring of relations around a central node

        if ring == 0:
            focusNodeID = self.activeNodeID
        else:
            focusNodeID = focusNodeImg.nodeID

        # Create destNodeID and relationship lists for each direction from the
        # active node
        destNodeIDs_dir0 = [focusNodeID]
        linkIDs_forward_dir0, linkIDs_reverse_dir0 = [None], [None]

        activeLinks_dir1 = db.LinksDBModel(self.window, focusNodeID,
        dirs=[self.window.axisAssignments[1]])
        destNodeIDs_dir1 = activeLinks_dir1.destNodeIDs()
        linkIDs_forward_dir1, linkIDs_reverse_dir1 = activeLinks_dir1.linkIDs()

        activeLinks_dir2 = db.LinksDBModel(self.window, focusNodeID,
        dirs=[self.window.axisAssignments[2]])
        destNodeIDs_dir2 = activeLinks_dir2.destNodeIDs()
        linkIDs_forward_dir2, linkIDs_reverse_dir2 = activeLinks_dir2.linkIDs()

        activeLinks_dir3 = db.LinksDBModel(self.window, focusNodeID,
        dirs=[self.window.axisAssignments[3]])
        destNodeIDs_dir3 = activeLinks_dir3.destNodeIDs()
        linkIDs_forward_dir3, linkIDs_reverse_dir3 = activeLinks_dir3.linkIDs()

        activeLinks_dir4 = db.LinksDBModel(self.window, focusNodeID,
        dirs=[self.window.axisAssignments[4]])
        destNodeIDs_dir4 = activeLinks_dir4.destNodeIDs()
        linkIDs_forward_dir4, linkIDs_reverse_dir4 = activeLinks_dir4.linkIDs()

        # Set network geometry
        networkCenterX = centerCoords[0]
        networkCenterY = centerCoords[1]
        relationOrbit = self.orbit

        # Add relation node/link images into the scene for each axis direction
        axisDirectionMultipliers = {'0': ['X', 0, 0], '1': ['X', 0, 1],
        '2': ['X', 0, -1], '3': ['Y', 1, 0], '4': ['Y', -1, 0]}
        ringLinkNodeIDs = []
        activeLinkNodeCenters = []
        ringLinkNodeImgs = {}
        linkNodeImgs_all = []

        if ring == 0:
            axisDirSet = [0]
        else:
            axisDirSet = [1, 2, 3, 4]

        for axisDir in axisDirSet:
            # Add node images into the scene for this axis direction
            linkNodeImgs_thisAxisDir = []
            destNodeIDs = eval('destNodeIDs_dir'+str(axisDir))
            linkIDs_forward = eval('linkIDs_forward_dir'+str(axisDir))
            linkIDs_reverse = eval('linkIDs_reverse_dir'+str(axisDir))
            startLimitAxis, xSign, ySign = axisDirectionMultipliers[str(
            axisDir)]

            for i in range(len(destNodeIDs)):
                if startLimitAxis == 'X':
                    relationStartLimit = networkCenterX - \
                    self.window.nodeImgWidth*0.55*(len(destNodeIDs)-1)
                    centerX = relationStartLimit + \
                    self.window.nodeImgWidth*1.1*i
                    centerY = networkCenterY + ySign*relationOrbit
                elif startLimitAxis == 'Y':
                    relationStartLimit = networkCenterY - \
                    self.window.nodeImgHeight*0.55*(len(destNodeIDs)-1)
                    centerX = networkCenterX + xSign*relationOrbit
                    centerY = relationStartLimit + \
                    self.window.nodeImgHeight*1.1*i

                if int(destNodeIDs[i]) in self.activeLinkNodeIDs:
                    # If the node already exists on the graph, pass
                    pass
                else:
                    # If the node doesn't exist on the graph yet, create the
                    # node image
                    linkNodeImg = self.window.addNode(
                        name='activeLinkNodeImg_ring'+str(ring)+'_dir'+\
                        str(axisDir)+'_'+str(i),
                        nodeID=destNodeIDs[i],
                        scene=self.scene(),
                        dir=axisDir,
                        centerX=centerX,
                        centerY=centerY,
                        width=self.window.nodeImgWidth,
                        height=self.window.nodeImgHeight,
                        textSize=self.window.nodeImgTextSize
                    )
                    linkNodeImgs_all.append(linkNodeImg)
                    linkNodeImgs_thisAxisDir.append(linkNodeImg)
                    ringLinkNodeImgs.update(
                    {str(axisDir): linkNodeImgs_thisAxisDir})
                    self.networkElements.append(linkNodeImg)
                    activeLinkNodeCenters.append([centerX, centerY])
                    ringLinkNodeIDs.append(destNodeIDs[i])
                    self.activeLinkNodeIDs.append(int(destNodeIDs[i]))
                    self.activeLinkNodeImgs.append(linkNodeImg)

            # Add link images into the scene for this direction
            activeLinkImgs = []
            if focusNodeImg != None:
                for i in range(len(destNodeIDs)):
                    if int(destNodeIDs[i]) in self.activeLinkNodeIDs:
                        destNodeImg = self.activeLinkNodeImgs[
                        self.activeLinkNodeIDs.index(int(destNodeIDs[i]))]
                        focusAnchorDirs = {1: 'bottom', 2: 'top', 3: 'right',
                        4: 'left'}
                        destAnchorDirs = {1: 'top', 2: 'bottom', 3: 'left',
                        4: 'right'}
                        anchor1 = eval('focusNodeImg.'+focusAnchorDirs[
                        axisDir]+'Anchor')
                        anchor2 = eval('destNodeImg.'+destAnchorDirs[
                        axisDir]+'Anchor')
                        linkImg = self.window.addLink(
                            scene=self.scene(),
                            linkID_forward=linkIDs_forward[int(destNodeIDs[i])],
                            linkID_reverse=linkIDs_reverse[int(destNodeIDs[i])],
                            nodeImg1=focusNodeImg,
                            anchor1=anchor1,
                            nodeImg2=self.activeLinkNodeImgs[
                            self.activeLinkNodeIDs.index(int(destNodeIDs[i]))],
                            anchor2=anchor2
                        )
                        activeLinkImgs.append(linkImg)
                        self.networkElements.append(linkImg)
                    else:
                        if axisDir == 1:
                            anchor1=focusNodeImg.bottomAnchor
                            anchor2=ringLinkNodeImgs[str(axisDir)][i].topAnchor
                        elif axisDir == 2:
                            anchor1=focusNodeImg.topAnchor
                            anchor2=ringLinkNodeImgs[str(axisDir)][i].bottomAnchor
                        elif axisDir == 3:
                            anchor1=focusNodeImg.rightAnchor
                            anchor2=ringLinkNodeImgs[str(axisDir)][i].leftAnchor
                        elif axisDir == 4:
                            anchor1=focusNodeImg.leftAnchor
                            anchor2=ringLinkNodeImgs[str(axisDir)][i].rightAnchor
                        linkImg = self.window.addLink(
                            scene=self.scene(),
                            linkID_forward=linkIDs_forward[int(destNodeIDs[i])],
                            linkID_reverse=linkIDs_reverse[int(destNodeIDs[i])],
                            nodeImg1=focusNodeImg,
                            anchor1=anchor1,
                            nodeImg2=ringLinkNodeImgs[str(axisDir)][i],
                            anchor2=anchor2
                        )
                        activeLinkImgs.append(linkImg)
                        self.networkElements.append(linkImg)

        return activeLinkNodeCenters, ringLinkNodeIDs, linkNodeImgs_all

    def renderLastLinksRing(self, centerCoords, focusNodeImg):
        # Render the last set of links after the final ring of nodes (only those
        # which connect to nodes already on the view)

        focusNodeID = focusNodeImg.nodeID

        # Create destNodeID and relationship lists for each direction from the
        # active node
        destNodeIDs_dir0 = [focusNodeID]
        linkIDs_forward_dir0, linkIDs_reverse_dir0 = [None], [None]

        activeLinks_dir1 = db.LinksDBModel(self.window, focusNodeID,
        dirs=[self.window.axisAssignments[1]])
        destNodeIDs_dir1 = activeLinks_dir1.destNodeIDs()
        linkIDs_forward_dir1, linkIDs_reverse_dir1 = activeLinks_dir1.linkIDs()

        activeLinks_dir2 = db.LinksDBModel(self.window, focusNodeID,
        dirs=[self.window.axisAssignments[2]])
        destNodeIDs_dir2 = activeLinks_dir2.destNodeIDs()
        linkIDs_forward_dir2, linkIDs_reverse_dir2 = activeLinks_dir2.linkIDs()

        activeLinks_dir3 = db.LinksDBModel(self.window, focusNodeID,
        dirs=[self.window.axisAssignments[3]])
        destNodeIDs_dir3 = activeLinks_dir3.destNodeIDs()
        linkIDs_forward_dir3, linkIDs_reverse_dir3 = activeLinks_dir3.linkIDs()

        activeLinks_dir4 = db.LinksDBModel(self.window, focusNodeID,
        dirs=[self.window.axisAssignments[4]])
        destNodeIDs_dir4 = activeLinks_dir4.destNodeIDs()
        linkIDs_forward_dir4, linkIDs_reverse_dir4 = activeLinks_dir4.linkIDs()

        # Set network geometry
        networkCenterX = centerCoords[0]
        networkCenterY = centerCoords[1]

        # Add relation link images into the scene for each axis direction
        axisDirectionMultipliers = {'0': ['X', 0, 0], '1': ['X', 0, 1],
        '2': ['X', 0, -1], '3': ['Y', 1, 0], '4': ['Y', -1, 0]}
        ringLinkNodeIDs = []
        activeLinkNodeCenters = []
        ringLinkNodeImgs = {}
        linkNodeImgs_all = []

        axisDirSet = [1, 2, 3, 4]

        for axisDir in axisDirSet:
            # Add node images into the scene for this axis direction
            linkNodeImgs_thisAxisDir = []
            destNodeIDs = eval('destNodeIDs_dir'+str(axisDir))
            linkIDs_forward = eval('linkIDs_forward_dir'+str(axisDir))
            linkIDs_reverse = eval('linkIDs_reverse_dir'+str(axisDir))
            startLimitAxis, xSign, ySign = axisDirectionMultipliers[str(
            axisDir)]

            # Add link images into the scene for this direction
            activeLinkImgs = []
            for i in range(len(destNodeIDs)):
                if int(destNodeIDs[i]) in self.activeLinkNodeIDs:
                    destNodeImg = self.activeLinkNodeImgs[
                    self.activeLinkNodeIDs.index(int(destNodeIDs[i]))]
                    focusAnchorDirs = {1: 'bottom', 2: 'top', 3: 'right',
                    4: 'left'}
                    destAnchorDirs = {1: 'top', 2: 'bottom', 3: 'left',
                    4: 'right'}
                    anchor1 = eval('focusNodeImg.'+focusAnchorDirs[
                    axisDir]+'Anchor')
                    anchor2 = eval('destNodeImg.'+destAnchorDirs[
                    axisDir]+'Anchor')
                    linkImg = self.window.addLink(
                        scene=self.scene(),
                        linkID_forward=linkIDs_forward[int(destNodeIDs[i])],
                        linkID_reverse=linkIDs_reverse[int(destNodeIDs[i])],
                        nodeImg1=focusNodeImg,
                        anchor1=anchor1,
                        nodeImg2=self.activeLinkNodeImgs[
                        self.activeLinkNodeIDs.index(int(destNodeIDs[i]))],
                        anchor2=anchor2
                    )
                    activeLinkImgs.append(linkImg)
                    self.networkElements.append(linkImg)


def remoteLinkInterface(interfaceOwner, posX, posY):
    # Create a target-selector portal for remote linking

    # Create remote-link-target selector portal
    interfaceOwner.linkPortal = NetworkPortal(interfaceOwner, 30, 490,
    490, posX, posY, 'select', False, 2, 150)

    if QtGui.QMainWindow in interfaceOwner.__class__.__bases__:
        window = interfaceOwner
    if type(interfaceOwner) == grav.nodeImg.Anchor:
        window = interfaceOwner.window
        interfaceOwner.window.linkPortal = interfaceOwner.linkPortal

    region = QtGui.QRegion(interfaceOwner.linkPortal.rect(),
    QtGui.QRegion.Ellipse)
    interfaceOwner.linkPortal.setMask(region)
    interfaceOwner.proxyPortal = window.viewNetwork.scene().addWidget(
    interfaceOwner.linkPortal)

    interfaceOwner.portalRim = QtGui.QGraphicsEllipseItem(posX-250,
    posY-250, 500, 500)
    interfaceOwner.portalRim.setPen(QtGui.QPen(QtCore.Qt.black, 10,
    QtCore.Qt.SolidLine))
    window.viewNetwork.scene().addItem(interfaceOwner.portalRim)
    window.viewNetwork.scene().role = 'background'

    # Display input box querying for seed node
    entry, ok = QtGui.QInputDialog.getText(None, 'Enter name of seed Thing\
    you want to relate to:',
    'Thing name:', QtGui.QLineEdit.Normal, '')

    # Detect invalid names and abort (return) method if necessary
    if ok and not entry == '':
        nodeModel = db.NodeDBModel(nodeName=entry)
        if nodeModel.nodeID != None:
            interfaceOwner.linkPortal.setActiveNode(nodeModel.nodeID)
            return
    linkPortalClose(interfaceOwner)


def chooseNode(window, nodeID):
    # Responds to single-click signal from node in remote selector portal
    # by entering the create-relationship method, if this node opened
    # that portal

    # Limit this method to only fire if the remote link portal is open
    if window.linkPortal == None:
        return

    if QtGui.QMainWindow in window.linkPortal.interfaceOwner.__class__.__bases__:
        window.notesEditor.setNodeLinkOnSelection_postSignal(nodeID)
        linkPortalClose(window.linkPortal.interfaceOwner)
    elif type(window.linkPortal.interfaceOwner) == grav.nodeImg.Anchor:
        anchor = window.linkPortal.anchor

        # Limit following actions to only remote link portals with the role 'select' and
        # to anchors which are the owners of the link portal
        if (not hasattr(anchor.scene(), 'role') or anchor.scene() is None or \
        anchor.scene().role != 'background'):
            return
        if anchor.linkPortal == None:
            return

        window.brain.createRelationship(anchor.node.nodeID, anchor.direction,
        nodeID, anchor.oppositeDirection, None)
        linkPortalClose(anchor)


def linkPortalClose(interfaceOwner):
    # Removes remote-link portal from the network view

    if QtGui.QMainWindow in interfaceOwner.__class__.__bases__:
        window = interfaceOwner
    if type(interfaceOwner) == grav.nodeImg.Anchor:
        window = interfaceOwner.window

    window.viewNetwork.scene().removeItem(
    window.linkPortal.graphicsProxyWidget())
    window.linkPortal = None
    window.viewNetwork.scene().removeItem(
    interfaceOwner.portalRim)
    del interfaceOwner.portalRim
    window.viewNetwork.scene().role = 'main'
    interfaceOwner.linkPortal = None
