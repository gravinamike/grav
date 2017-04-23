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
from PyQt4.QtCore import(Qt, QObject, QString, QLatin1String)
from PyQt4.QtGui import(QApplication, QMessageBox, QInputDialog, QLineEdit)
from PyQt4.QtSql import(QSqlDatabase, QSqlQuery, QSqlQueryModel, QSqlTableModel)


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

        # If DIRECTIONS table doesn't yet exist, create it
        if self.__database.tables().contains(
        QLatin1String('PUBLIC.DIRECTIONS')):
            print 'Table found!'
        else:
            print 'Directions table not found - creating table!'
            queryTexts = [
            'CREATE TABLE public.directions(id integer, text varchar(255), \
            thebraindir integer, opposite integer)'
            ]
            # memo may instead be varchar(255)
            queries = self.querySet(queryTexts)

        # If DIRECTION field doesn't yet exist in LINKS table, create it
        if self.__database.record('PUBLIC.LINKS').contains(
        QLatin1String('DIRECTION')):
            print 'Field found!'
        else:
            print 'Direction field not found in links table- creating field!'
            queryTexts = [
            'ALTER TABLE public.links ADD direction integer',
            #
            'UPDATE public.links SET direction = dir WHERE direction IS NULL'
            ]
            queries = self.querySet(queryTexts)

        # Create a read-write model based the DIRECTIONS table
        self.modelDirections = QSqlTableModel(None, self.__database)
        self.modelDirections.setTable('PUBLIC.DIRECTIONS')
        self.modelDirections.setSort(0, Qt.AscendingOrder)
        self.modelDirections.setHeaderData(1, Qt.Horizontal, 'Direction')
        self.modelDirections.setHeaderData(2, Qt.Horizontal, 'TheBrainDir')
        self.modelDirections.setHeaderData(3, Qt.Horizontal, 'Opposite')
        self.modelDirections.setEditStrategy(QSqlTableModel.OnFieldChange)
        #self.modelDirections.dataChanged.connect(self.report1)
        self.modelDirections.select()

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

    def createDirection(self):
        # Add a new record to the DIRECTIONS table.

        """createDirection = self.modelDirections.insertRows(
        self.modelDirections.rowCount(), 1)
        print createDirection
        print self.modelDirections.rowCount()
        print self.modelDirections.lastError().databaseText()"""

        # Define and execute query to determine current max direction serial
        model = QSqlQueryModel()
        query = 'SELECT * FROM directions WHERE id=(SELECT MAX(id) FROM \
        directions)'
        model.setQuery(query)
        if model.record(0).value('id').toString() == '':
            newDirectionSerial = 0
        else:
            newDirectionSerial = int(model.record(0).value('id').toString()) + 1
        print str(newDirectionSerial)

        # Define queries to insert new direction record
        queryTexts = [
        'INSERT INTO public.directions (id, text, thebraindir, opposite) \
        VALUES (%s, NULL, 1, NULL)' % (newDirectionSerial)
        ]

        # Execute queries and update view
        queries = self.querySet(queryTexts)
        #self.modelDirections.select()
        #self.modelDirections.select()

    def deleteDirection(self):
        # Delete last record in the DIRECTIONS table.

        # Define and execute query to determine current max direction serial
        model = QSqlQueryModel()
        query = 'SELECT * FROM directions WHERE id=(SELECT MAX(id) FROM \
        directions)'
        model.setQuery(query)
        if model.record(0).value('id').toString() == '':
            print 'No records to delete!'
        else:
            directionSerial = int(model.record(0).value('id').toString())
            print str(directionSerial)

            # Define queries to remove last direction record
            queryTexts = [
            "DELETE FROM directions WHERE (id=" + str(directionSerial) + ")"
            ]

            # Execute queries and update view
            queries = self.querySet(queryTexts)
            self.modelDirections.select()

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

        # Determine the opposite and TheBrain classic direction numbers from the
        # relation direction
        model = QSqlQueryModel()
        query = 'SELECT * FROM directions WHERE id=(' + str(dir) + ')'
        model.setQuery(query)
        theBrainDir = int(model.record(0).value('thebraindir').toString())
        dirOpposite = int(model.record(0).value('opposite').toString())
        theBrainDirOpposites = {1: 2, 2: 1, 3: 3}

        # Define queries to insert new relation node and links
        queryTexts = [
        "INSERT INTO thoughts (id, brainid, guid, name, creationdatetime) " +
        "VALUES (%s, %s, '%s', '%s', '%s')" % (newNodeSerial, 1, GUID0, \
        newName, timeDateStamp),
        #
        "INSERT INTO links (id, brainid, guid, ida, idb, creationdatetime, " +
        "dir, direction) VALUES (%s, %s, '%s', %s, %s, '%s', %s, %s)" % \
        (linkSerial1, 1, GUID1, sourceNodeID, newNodeSerial, timeDateStamp, \
        theBrainDir, dir),
        #
        "INSERT INTO links (id, brainid, guid, ida, idb, creationdatetime, " +
        "dir, direction) VALUES (%s, %s, '%s', %s, %s, '%s', %s, %s)" % \
        (linkSerial2, 1, GUID2, newNodeSerial, sourceNodeID, timeDateStamp, \
        theBrainDirOpposites[theBrainDir], dirOpposite)
        ]

        # Execute queries, then refresh the network view
        queries = self.querySet(queryTexts)
        self.window.setActiveNode(self.window.activeNodeID)

    def deleteRelation(self, nodeID):
        # Delete a node and all its relations.

        # Display input box querying to continue or not
        confirm = QMessageBox.question(None, 'Confirm delete',
        'Delete this node?', QMessageBox.Yes, QMessageBox.No)

        # Either call the delete method or abort
        if confirm == QMessageBox.Yes:

            # Define and execute query to determine whether notes item exists
            model = QSqlQueryModel()
            query = 'SELECT * FROM entrytoobject WHERE objectid=' + str(nodeID)
            model.setQuery(query)
            notesQueryTexts = []

            if model.record(0).value('id').toString() != '':
                # Delete any notes and linkers
                noteLinkerID = int(model.record(0).value('id').toString())
                noteID = int(model.record(0).value('entryid').toString())

                # Define queries to delete notes and linkers if they exist
                notesQueryTexts = [
                "DELETE FROM entrytoobject WHERE id=" + str(noteLinkerID),
                #
                "DELETE FROM entries WHERE id=" + str(noteID)
                ]

            # Define queries to delete node and links
            queryTexts = [
            "DELETE FROM links WHERE (ida=" + str(nodeID) + \
            " or idb=" + str(nodeID) + ")",
            #
            "DELETE FROM thoughts WHERE id=" + str(nodeID)
            ]
            queryTexts.extend(notesQueryTexts)

            # Execute queries, then refresh the network view
            queries = self.querySet(queryTexts)
            self.window.setActiveNode(self.window.activeNodeID)
        else:
            print 'Canceled...'

    def createRelationship(self, sourceNodeID, sourceDir, destNodeID,
        destDir, sidedness):
        # Create a relationship link from one node to another

        # If method would link a node to itself, display error and return
        if sourceNodeID == destNodeID:
            message = QMessageBox.critical(None, 'Error',
            'Can\'t relate a Thing to itself!')
            return

        # Determine the opposite direction from the relation direction
        model = QSqlQueryModel()
        query = 'SELECT * FROM directions WHERE id=(' + str(sourceDir) + ')'
        model.setQuery(query)
        theBrainDirSource = int(model.record(0).value('thebraindir'\
        ).toString())
        sourceDirOpposite = int(model.record(0).value('opposite').toString())

        # If method would create paired relationships which are not opposites
        # of one another, display error and return
        if destDir != sourceDirOpposite:
            #message = QMessageBox.critical(None, 'Error',
            #'You can\'t relate two Things with relationship types that are \
            #not opposites!')
            return

        # Display input box querying to continue or not
        confirm = QMessageBox.question(None, 'Create relationship?',
        'Create relationship?', QMessageBox.Yes, QMessageBox.No)

        # Either call the delete method or abort
        if confirm == QMessageBox.Yes:
            # Get a new GUIDs and date/timestamp
            GUID0, GUID1 = uuid4(), uuid4()
            timeDateStamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'\
            )[:-3]

            # Define and execute query to determine current max link serial
            model = QSqlQueryModel()
            query = 'SELECT * FROM links WHERE id=(SELECT MAX(id) FROM links)'
            model.setQuery(query)
            linkSerial1 = str(int(model.record(0).value('id').toString()) + 1)
            linkSerial2 = str(int(model.record(0).value('id').toString()) + 2)

            # Determine the TheBrain classic direction numbers from the relation
            # direction
            model = QSqlQueryModel()
            query = 'SELECT * FROM directions WHERE id=(' + str(sourceDir) + ')'
            model.setQuery(query)
            theBrainDirSource = int(model.record(0).value('thebraindir'\
            ).toString())

            model = QSqlQueryModel()
            query = 'SELECT * FROM directions WHERE id=(' + str(destDir) + ')'
            model.setQuery(query)
            theBrainDirDest = int(model.record(0).value('thebraindir'\
            ).toString())

            # Define queries to insert new relationship links
            queryTexts = [
            "INSERT INTO links (id, brainid, guid, ida, idb, " +
            "creationdatetime, dir, direction) VALUES (%s, %s, '%s', %s, %s, \
            '%s', %s, %s)" % (linkSerial1, 1, GUID0, sourceNodeID, destNodeID, \
            timeDateStamp, theBrainDirSource, sourceDir),
            #
            "INSERT INTO links (id, brainid, guid, ida, idb, " +
            "creationdatetime, dir, direction) VALUES (%s, %s, '%s', %s, %s, \
            '%s', %s, %s)" % (linkSerial2, 1, GUID1, destNodeID, sourceNodeID, \
            timeDateStamp, theBrainDirDest, destDir)
            ]

            # Execute queries, then refresh the network view
            queries = self.querySet(queryTexts)
            self.window.setActiveNode(self.window.activeNodeID)
        else:
            print 'Canceled...'

    def saveNotes(self, notesText):

        # Define and execute query to determine whether notes item exists
        model = QSqlQueryModel()
        query = 'SELECT * FROM entries WHERE id=' + \
        str(self.window.notesDBModel.notesID)
        model.setQuery(query)
        timeDateStamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'
        )[:-3]
        if model.record(0).value('id').toString() == '':
            print 'No notes for this node. Creating notes.'

            # Define and execute query to determine current max note serial
            model = QSqlQueryModel()
            query = 'SELECT * FROM entries WHERE id=(SELECT MAX(id) FROM \
            entries)'
            model.setQuery(query)
            newEntrySerial = str(int(model.record(0).value('id').toString()) + \
            1)

            # Define/execute query to determine current max note-linker serial
            model = QSqlQueryModel()
            query = 'SELECT * FROM entrytoobject WHERE id=(SELECT MAX(id) FROM \
            entrytoobject)'
            model.setQuery(query)
            newLinkSerial = str(int(model.record(0).value('id').toString()) + \
            1)

            GUID = uuid4()

            """
            # Create a blank html template
            blankText = "N\'" + \
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" \
            "http://www.w3.org/TR/REC-html40/strict.dtd"><html><head>\
            <meta name="qrichtext" content ="1" /><style type="text/css"> \
            p, li { white space: pre-wrap; } </style></head>\
            <body style=" font-family:"MS Shell Dlg 2"; font-size:8.25pt; \
            font-weight:400; font-style:normal;">\
            <p style="-qt-paragraph-type:empty; margin-top:0px; \
            margin-bottom:0px; margin-left:0px; margin-right:0px; \
            -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>' + \
            "\'"
            """

            # Define queries to insert new notes item and linker
            queryTexts = [
            "INSERT INTO entries (id, brainid, guid, body, bodyformat, \
            creationdatetime, modificationdatetime, version, featured, \
            blogthis) " + \
            "VALUES (%s, %s, '%s', '%s', %s, '%s', '%s', %s, %s, %s)" \
            % (newEntrySerial, 1, GUID, notesText, "\'HTML\'", \
            timeDateStamp, timeDateStamp, 1, 1, 0),
            #
            "INSERT INTO entrytoobject (id, objecttype, objectid, entryid, \
            brainid) " + \
            "VALUES (%s, %s, %s, %s, %s)" % (newLinkSerial, 0, \
            self.window.activeNodeID, newEntrySerial, 1)
            ]

            # Execute queries, then refresh the notes view
            queries = self.querySet(queryTexts)
            self.window.renderNotes()
        else:
            # Define queries to update notes text
            queryTexts = [
            "UPDATE entries SET body=N\'" + notesText +
            "\' WHERE id=" + str(self.window.notesDBModel.notesID),
            #
            "UPDATE entries SET modificationdatetime=N\'" + timeDateStamp +
            "\' WHERE id=" + str(self.window.notesDBModel.notesID)
            ]

            # Execute queries
            queries = self.querySet(queryTexts)


class AxisDirectionsDBModel:
    #A read-write model based on a SQL query on the DIRECTIONS table
    def __init__(self, *dirs):

        # Define and execute query to retrieve direction info
        dirList = []
        for dir in dirs:
            dirList.append(str(dir))
        self.model = QSqlQueryModel()
        query = 'SELECT * FROM directions WHERE id=(' + \
        ') or id=('.join(dirList) + ')'
        self.model.setQuery(query)


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


class LinksDBModel:
    #A read-write model based on a SQL query on the LINKS table
    def __init__(self, activeNodeID, dirs=[1]):
        self.listNumber = False
        self.activeNodeID = activeNodeID
        self.dirs = dirs
        self.model = QSqlQueryModel()

        # Define and execute query
        query = 'SELECT * FROM links WHERE (ida=' + str(self.activeNodeID) + \
        ' or idb=' + str(self.activeNodeID) + ') and direction IN (' + \
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
