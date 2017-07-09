#! python3
#File: signaler.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: Jun 2017
"""

import grav.window
import grav.nodeImg
from PyQt4 import QtCore


class Signaler(QtCore.QObject):
    # An object which sends signals - gets over the limitations of PyQt when it
    # comes to signals.

    select = QtCore.pyqtSignal(grav.window.Window, int)
    deleteRelation = QtCore.pyqtSignal(grav.window.Window, int)
    deleteRelationship = QtCore.pyqtSignal(grav.window.Window, int)
    portalInit = QtCore.pyqtSignal(object, int, int)

    def __init__(self):
        super(Signaler, self).__init__()
