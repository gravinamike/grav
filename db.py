#! python3
#File: db.py

"""
Interface between grav package and TheBrain H2 database, making use of
ODBC PostgreSQL adaptor and PyQt database module.
Using code from http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/
BUILD/PyQt-x11-gpl-4.7.2/doc/html/qtsql.html#connecting-to-databases

author: Mike Gravina
last edited: November 2016
"""

import site
from subprocess import Popen
from PyQt4.QtGui import QApplication
from PyQt4.QtSql import(QSqlDatabase, QSqlQueryModel)


class Brain:
    # Instantiates a Brain object that links to an active H2 database

    def __init__(self):
        # Open the database
        self.h2 = Popen(["java", "-cp",
        "C:/Program Files (x86)/TheBrain/lib/h2.jar", "org.h2.tools.Server",
        "-pg"])

        #IS THIS CORRECT? IT REFERS TO PYQT 5, NOT 4!
        site_pack_path = site.getsitepackages()[1]
        QApplication.addLibraryPath(
        '{0}\\PyQt5\\plugins'.format(site_pack_path))

        # Establish a connection to the database
        # Add this when it's actually an application:
        # QApplication.addLibraryPath('C:/Users/Grav/AppData/Local/Programs
        # /Python/Python35-32/Lib/site-packages/PyQt5/plugins/sqldrivers')
        self.__database = QSqlDatabase.addDatabase('QPSQL')
        self.__database.setHostName('localhost')
        self.__database.setDatabaseName(
        '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')
        # .h2.db? ;ifexists=true?
        self.__database.setPort(5435) #Possibly redundant
        self.__database.setUserName('sa')
        self.__database.setPassword('Th1nkingM0re')
        #SSL mode disable, server-side prepare?

        # Open database and give access to data. If call fails it
        # returns false; error info obtained from QSqlDatabase.lastError()
        ok = self.__database.open()
        if ok == False:
            print 'Could not open database'
            print 'Text: ', self.__database.lastError().text()
            print 'Type: ', str(self.__database.lastError().type())
            print 'Number: ', str(self.__database.lastError().number())
            print 'Loaded drivers:', str(QSqlDatabase.drivers())


class nodeDBModel:
    #A read-write model based on a SQL query on the THOUGHTS table
    def __init__(self, nodeID=1):
        self.nodeID = nodeID
        listNumber = False

        # Define and execute query
        self.model = QSqlQueryModel()
        query = 'SELECT * FROM thoughts WHERE id=' + str(self.nodeID)
        self.model.setQuery(query)


class notesDBModel:
    #A read-write model based on a SQL query on the notes table
    def __init__(self, nodeID=1):
        self.nodeID = nodeID
        listNumber = False

        # Define and execute query for linker from node to notes
        self.modelNodeToNotes = QSqlQueryModel()
        query = 'SELECT * FROM entrytoobject WHERE objectid=' + str(self.nodeID)
        self.modelNodeToNotes.setQuery(query)
        notesID = self.modelNodeToNotes.record(0).value('entryid').toString()

        # Define and execute query for the notes themselves
        self.modelNotes = QSqlQueryModel()
        query = 'SELECT * FROM entries WHERE id=' + str(notesID)
        self.modelNotes.setQuery(query)

class linksDBModel:
    #A read-write model based on a SQL query on the LINKS table
    def __init__(self, activeNodeID, dirs=[1]):
        self.listNumber = False
        self.activeNodeID = activeNodeID
        self.dirs = dirs
        self.model = QSqlQueryModel()

        # Define and execute query
        query = 'SELECT * FROM links WHERE (ida=' + str(self.activeNodeID) + \
        ' or idb=' + str(self.activeNodeID) + ') and dir IN (' + \
        ', '.join(str(dir) for dir in self.dirs) + ')'
        self.model.setQuery(query)

    def destNodeIDs(self):
        # Queries and returns the IDs of nodes related to the active node

        # Determines whether all or only a fixed number of links are queried
        if self.listNumber == False:
            end = self.model.rowCount()
        else:
            end = self.listNumber

        # Defines and performs the query and adds the nodes to a list
        destNodeIDs = []
        for i in range(0, end):
            if self.model.record(i).value('ida') == self.activeNodeID:
                destNodeIDs.append(self.model.record(i).value('idb').toString())
            # There are actually 2 links for each visible link. Double links are
            # created at the same time, and have sequential IDs. We are ignoring
            # the second one, but the code below would reinstantiate it (and
            # create false link nodes "mirroring" the active node).
            #if self.model.record(i).value('idb') == self.activeNodeID:
                #destNodeIDs.append(self.model.record(i).value('ida').toString())

        # Returns the related node IDs
        return destNodeIDs
