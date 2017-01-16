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
from uuid import uuid4
from datetime import datetime
from PyQt4.QtGui import(QApplication, QMessageBox, QInputDialog, QLineEdit)
from PyQt4.QtSql import(QSqlDatabase, QSqlQuery, QSqlQueryModel)


class Brain:
    # Instantiates a Brain object that links to an active H2 database

    def __init__(self, window):
        # Initialize attributes
        self.window = window

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

    def querySet(self, queryTexts):
        # Define and execute a set of queries against the database

        # Initiate transaction
        #QSqlDatabase.database().transaction()
        self.__database.transaction()

        # Iterate through supplied queries, executing and reporting success/fail
        sqlOk = 1
        for queryText in queryTexts:
            query = QSqlQuery()
            print queryText
            sqlOk = query.exec_(queryText)
            if sqlOk != 1:
                break

        # Either detect any errors and rollback, or otherwise commit.
        if sqlOk == 1:
            self.__database.commit()
            print 'Committed'
        else:
            message = QMessageBox.critical(None, 'Error',
            query.lastError().text())
            self.__database.rollback()

    def createRelation(self, sourceNodeID, dir, sidedness):
        # Create a related node to the active node and associated links

        # Display input box querying for name value
        entry, ok = QInputDialog.getText(None, 'Enter name for new Thing',
        'Name:', QLineEdit.Normal, '')
        # Detect invalid names and abort (return) method if necessary
        if ok and not entry == '':
            newName = entry
        else:
            return

        # Get a new GUIDs and date/timestamp
        GUID0, GUID1, GUID2 = uuid4(), uuid4(), uuid4()
        timeDateStamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Define and execute query to determine current max node serial
        model = QSqlQueryModel()
        query = 'SELECT * FROM thoughts WHERE id=(SELECT MAX(id) FROM thoughts)'
        model.setQuery(query)
        newNodeSerial = str(int(model.record(0).value('id').toString()) + 1)

        # Define and execute query to determine current max link serial
        model = QSqlQueryModel()
        query = 'SELECT * FROM links WHERE id=(SELECT MAX(id) FROM links)'
        model.setQuery(query)
        linkSerial1 = str(int(model.record(0).value('id').toString()) + 1)
        linkSerial2 = str(int(model.record(0).value('id').toString()) + 2)

        # Determine the opposite direction number from the relation direction
        if dir % 2 == 1:
            dirOpposite = dir + 1
        else:
            dirOpposite = dir - 1

        # Define queries to insert new relation node and links
        queryTexts = [
        "INSERT INTO thoughts (id, brainid, guid, name, creationdatetime) " +
        "VALUES (%s, %s, '%s', '%s', '%s')" % (newNodeSerial, 1, GUID0, \
        newName, timeDateStamp),
        #
        "INSERT INTO links (id, brainid, guid, ida, idb, creationdatetime, " +
        "dir) VALUES (%s, %s, '%s', %s, %s, '%s', %s)" % \
        (linkSerial1, 1, GUID1, sourceNodeID, newNodeSerial, timeDateStamp, \
        dir),
        #
        "INSERT INTO links (id, brainid, guid, ida, idb, creationdatetime, " +
        "dir) VALUES (%s, %s, '%s', %s, %s, '%s', %s)" % \
        (linkSerial2, 1, GUID2, newNodeSerial, sourceNodeID, timeDateStamp, \
        dirOpposite)
        ]

        # Execute queries, then refresh the network view
        queries = self.querySet(queryTexts)
        self.window.setActiveNode(self.window.activeNodeID)

    def deleteRelation(self, nodeID):
        # Delete a node and all its relations.

        # Display input box querying to continue or not
        confirm = QMessageBox.question(None, 'Confirm delete',
        'Delete this node?', QMessageBox.Yes, QMessageBox.No)

        # Either call the delete methood or abort
        if confirm == QMessageBox.Yes:
            # Define queries to delete node and links
            queryTexts = [
            "DELETE FROM links WHERE (ida=" + str(nodeID) + \
            " or idb=" + str(nodeID) + ")",
            #
            "DELETE FROM thoughts WHERE id=" + str(nodeID)
            ]
            # Execute queries, then refresh the network view
            queries = self.querySet(queryTexts)
            self.window.setActiveNode(self.window.activeNodeID)

        else:
            print 'Canceled...'##########################################################


class NodeDBModel:
    #A read-write model based on a SQL query on the THOUGHTS table
    def __init__(self, nodeID=1):
        self.nodeID = nodeID
        listNumber = False

        # Define and execute query
        self.model = QSqlQueryModel()
        query = 'SELECT * FROM thoughts WHERE id=' + str(self.nodeID)
        self.model.setQuery(query)


class NotesDBModel:
    #A read-write model based on a SQL query on the notes table
    def __init__(self, window, nodeID=1):
        self.window = window
        self.nodeID = nodeID
        listNumber = False

        # Define and execute query for linker from node to notes
        self.modelNodeToNotes = QSqlQueryModel()
        query = 'SELECT * FROM entrytoobject WHERE objectid=' + str(self.nodeID)
        self.modelNodeToNotes.setQuery(query)
        self.notesID = self.modelNodeToNotes.record(0).value(
        'entryid').toString()

        # Define and execute query for the notes themselves
        self.modelNotes = QSqlQueryModel()
        query = 'SELECT * FROM entries WHERE id=' + str(self.notesID)
        self.modelNotes.setQuery(query)

    def saveNotes(self, notesText):
        # Define and execute query to save written notes to database notes
        QSqlDatabase.database().transaction()
        updateQuery = QSqlQuery()
        queryText = "UPDATE entries SET body=N\'" + notesText + \
        "\' WHERE id=" + str(self.notesID)
        updateIt = updateQuery.exec_(queryText)
        QSqlDatabase.database().commit()
        self.window.renderNotes()


class LinksDBModel:
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
