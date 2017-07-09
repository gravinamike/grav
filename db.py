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
from PyQt4 import QtCore, QtGui, QtSql


def openH2(jarName='C:/Program Files (x86)/TheBrain/lib/h2.jar'):
        # Open the database
        h2 = Popen(["java", "-cp",
        jarName, "org.h2.tools.Server",
        "-pg"])

        #IS THIS CORRECT? IT REFERS TO PYQT 5, NOT 4!
        site_pack_path = site.getsitepackages()[1]
        QtGui.QApplication.addLibraryPath(
        '{0}\\PyQt5\\plugins'.format(site_pack_path))

        return h2


class Brain2:
    # Instantiates a Brain object that links to an active H2 database

    def __init__(self, window, filename,
        jarName='C:/Program Files (x86)/TheBrain/lib/h2.jar'):
        # Initialize attributes
        self.window = window

        # Establish a connection to the database
        # Add this when it's actually an application:
        # QtGui.QApplication.addLibraryPath('C:/Users/Grav/AppData/Local/Programs
        # /Python/Python35-32/Lib/site-packages/PyQt5/plugins/sqldrivers')
        self.__database = QtSql.QSqlDatabase.addDatabase('QPSQL')
        self.__database.setHostName('localhost')
        self.__database.setDatabaseName(filename)
        # .h2.db? ;ifexists=true?
        self.__database.setPort(5435) #Possibly redundant
        self.__database.setUserName('sa')
        self.__database.setPassword('Th1nkingM0re')
        #SSL mode disable, server-side prepare?

        # Open database and give access to data. If call fails it
        # returns false; error info obtained from QtSql.QSqlDatabase.lastError()
        ok = self.__database.open()
        if ok == False:
            print 'Could not open database'
            print 'Text: ', self.__database.lastError().text()
            print 'Type: ', str(self.__database.lastError().type())
            print 'Number: ', str(self.__database.lastError().number())
            print 'Loaded drivers:', str(QtSql.QSqlDatabase.drivers())

    def database(self):
        return self.__database

    def close(self):
        connection = self.__database.connectionName()
        print connection
        self.__database.close()
        self.__database = QtSql.QSqlDatabase()
        self.__database.removeDatabase(connection)


"""class Brain:
    # Instantiates a Brain object that links to an active H2 database

    def __init__(self, window, filename,
        jarName='C:/Program Files (x86)/TheBrain/lib/h2.jar'):
        # Initialize attributes
        self.window = window

        # Establish a connection to the database
        # Add this when it's actually an application:
        # QtGui.QApplication.addLibraryPath('C:/Users/Grav/AppData/Local/Programs
        # /Python/Python35-32/Lib/site-packages/PyQt5/plugins/sqldrivers')
        self.__database = QtSql.QSqlDatabase.addDatabase('QPSQL')
        self.__database.setHostName('localhost')
        self.__database.setDatabaseName(filename)
        # .h2.db? ;ifexists=true?
        self.__database.setPort(5435) #Possibly redundant
        self.__database.setUserName('sa')
        self.__database.setPassword('Th1nkingM0re')
        #SSL mode disable, server-side prepare?

        # Open database and give access to data. If call fails it
        # returns false; error info obtained from QtSql.QSqlDatabase.lastError()
        ok = self.__database.open()
        if ok == False:
            print 'Could not open database'
            print 'Text: ', self.__database.lastError().text()
            print 'Type: ', str(self.__database.lastError().type())
            print 'Number: ', str(self.__database.lastError().number())
            print 'Loaded drivers:', str(QtSql.QSqlDatabase.drivers())

    def close(self):
        connection = self.__database.connectionName()
        print connection
        self.__database.close()
        self.__database = QtSql.QSqlDatabase()
        self.__database.removeDatabase(connection)


        # If DIRECTIONS table doesn't yet exist, create it
        if self.__database.tables().contains(
        QtCore.QLatin1String('PUBLIC.DIRECTIONS')):
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
        QtCore.QLatin1String('DIRECTION')):
            print 'Field found!'
        else:
            print 'Direction field not found in links table- creating field!'
            queryTexts = [
            'ALTER TABLE public.links ADD direction integer',
            #
            'UPDATE public.links SET direction = dir WHERE direction IS NULL'
            ]
            queries = self.querySet(queryTexts)

        # Create a read-write model based on the DIRECTIONS table
        self.modelDirections = QtSql.QSqlTableModel(None, self.__database)
        self.modelDirections.setTable('PUBLIC.DIRECTIONS')
        self.modelDirections.setSort(0, QtCore.Qt.AscendingOrder)
        self.modelDirections.setHeaderData(1, QtCore.Qt.Horizontal, 'Direction')
        self.modelDirections.setHeaderData(2, QtCore.Qt.Horizontal, 'TheBrainDir')
        self.modelDirections.setHeaderData(3, QtCore.Qt.Horizontal, 'Opposite')
        self.modelDirections.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        #self.modelDirections.dataChanged.connect(self.report1)
        self.modelDirections.select()



    def querySet(self, queryTexts):
        # Define and execute a set of queries against the database

        # Initiate transaction
        #QtSql.QSqlDatabase.database().transaction()
        self.__database.transaction()

        # Iterate through supplied queries, executing and reporting success/fail
        sqlOk = 1
        for queryText in queryTexts:
            if type(queryText) is QtCore.QString:
                printable = queryText.toUtf8()
            else:
                printable = queryText.encode('utf8')
            print printable
            query = QtSql.QSqlQuery()
            sqlOk = query.exec_(queryText)
            if sqlOk != 1:
                break

        # Either detect any errors and rollback, or otherwise commit.
        if sqlOk == 1:
            self.__database.commit()
            print 'Committed'
        else:
            message = QtGui.QMessageBox.critical(None, 'Error',
            query.lastError().text())
            self.__database.rollback()

    def createDirection(self):
        # Add a new record to the DIRECTIONS table.

        createDirection = self.modelDirections.insertRows(
        self.modelDirections.rowCount(), 1)
        print createDirection
        print self.modelDirections.rowCount()
        print self.modelDirections.lastError().databaseText()

        # Define and execute query to determine current max direction serial
        model = QtSql.QSqlQueryModel()
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
        model = QtSql.QSqlQueryModel()
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
        entry, ok = QtGui.QInputDialog.getText(None, 'Enter name for new Thing',
        'Name:', QtGui.QLineEdit.Normal, '')
        # Detect invalid names and abort (return) method if necessary
        if ok and not entry == '':
            newName = entry
        else:
            return

        # Get a new GUIDs and date/timestamp
        GUID0, GUID1, GUID2 = uuid4(), uuid4(), uuid4()
        timeDateStamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Define and execute query to determine current max node serial
        model = QtSql.QSqlQueryModel()
        query = 'SELECT * FROM thoughts WHERE id=(SELECT MAX(id) FROM thoughts)'
        model.setQuery(query)
        newNodeSerial = str(int(model.record(0).value('id').toString()) + 1)

        # Define and execute query to determine current max link serial
        model = QtSql.QSqlQueryModel()
        query = 'SELECT * FROM links WHERE id=(SELECT MAX(id) FROM links)'
        model.setQuery(query)
        linkSerial1 = str(int(model.record(0).value('id').toString()) + 1)
        linkSerial2 = str(int(model.record(0).value('id').toString()) + 2)

        # Determine the opposite and TheBrain classic direction numbers from the
        # relation direction
        model = QtSql.QSqlQueryModel()
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
        self.window.viewNetwork.setActiveNode()

    def deleteRelation(self, nodeID):
        # Delete a node and all its relations.

        # Display input box querying to continue or not
        confirm = QtGui.QMessageBox.question(None, 'Confirm delete',
        'Delete this node?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        # Either call the delete method or abort
        if confirm == QtGui.QMessageBox.Yes:

            # Define and execute query to determine whether notes item exists
            model = QtSql.QSqlQueryModel()
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
            self.window.viewNetwork.setActiveNode()
        else:
            print 'Canceled...'

    def createRelationship(self, sourceNodeID, sourceDir, destNodeID,
        destDir, sidedness):
        # Create a relationship link from one node to another

        # If method would link a node to itself, display error and return
        if sourceNodeID == destNodeID:
            message = QtGui.QMessageBox.critical(None, 'Error',
            'Can\'t relate a Thing to itself!')
            return

        # Determine the opposite direction from the relation direction
        model = QtSql.QSqlQueryModel()
        query = 'SELECT * FROM directions WHERE id=(' + str(sourceDir) + ')'
        model.setQuery(query)
        theBrainDirSource = int(model.record(0).value('thebraindir'\
        ).toString())
        sourceDirOpposite = int(model.record(0).value('opposite').toString())

        # If method would create paired relationships which are not opposites
        # of one another, display error and return
        if destDir != sourceDirOpposite:
            #message = QtGui.QMessageBox.critical(None, 'Error',
            #'You can\'t relate two Things with relationship types that are \
            #not opposites!')
            return

        # Display input box querying to continue or not
        confirm = QtGui.QMessageBox.question(None, 'Create relationship?',
        'Create relationship?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        # Either call the delete method or abort
        if confirm == QtGui.QMessageBox.Yes:
            # Get a new GUIDs and date/timestamp
            GUID0, GUID1 = uuid4(), uuid4()
            timeDateStamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'\
            )[:-3]

            # Define and execute query to determine current max link serial
            model = QtSql.QSqlQueryModel()
            query = 'SELECT * FROM links WHERE id=(SELECT MAX(id) FROM links)'
            model.setQuery(query)
            linkSerial1 = str(int(model.record(0).value('id').toString()) + 1)
            linkSerial2 = str(int(model.record(0).value('id').toString()) + 2)

            # Determine the TheBrain classic direction numbers from the relation
            # direction
            model = QtSql.QSqlQueryModel()
            query = 'SELECT * FROM directions WHERE id=(' + str(sourceDir) + ')'
            model.setQuery(query)
            theBrainDirSource = int(model.record(0).value('thebraindir'\
            ).toString())

            model = QtSql.QSqlQueryModel()
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
            self.window.viewNetwork.setActiveNode()
        else:
            print 'Canceled...'"""




def validateDatabase(window): ################## TODO: Initiate one of these at the beginning of the main script

    databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

    # If DIRECTIONS table doesn't yet exist, create it
    if databaseConn.tables().contains(
    QtCore.QLatin1String('PUBLIC.DIRECTIONS')):
        print 'Table found!'
    else:
        print 'Directions table not found - creating table!'
        queryTexts = [
        'CREATE TABLE public.directions(id integer, text varchar(255), \
        thebraindir integer, opposite integer)'
        ]
        # memo may instead be varchar(255)
        queries = querySet(queryTexts)

    # If DIRECTION field doesn't yet exist in LINKS table, create it
    if databaseConn.record('PUBLIC.LINKS').contains(
    QtCore.QLatin1String('DIRECTION')):
        print 'Field found!'
    else:
        print 'Direction field not found in links table- creating field!'
        queryTexts = [
        'ALTER TABLE public.links ADD direction integer',
        #
        'UPDATE public.links SET direction = dir WHERE direction IS NULL'
        ]
        queries = querySet(queryTexts)

    databaseConn.close()



class DirectionsModel:

    def __init__(self, window):
        #print 'directions' #foo
        databaseConn = Brain2(window,
        '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

        # Create a read-write model based on the DIRECTIONS table
        self.modelDirections = QtSql.QSqlTableModel(None, databaseConn)
        self.modelDirections.setTable('PUBLIC.DIRECTIONS')
        self.modelDirections.setSort(0, QtCore.Qt.AscendingOrder)
        self.modelDirections.setHeaderData(1, QtCore.Qt.Horizontal, 'Direction')
        self.modelDirections.setHeaderData(2, QtCore.Qt.Horizontal, 'TheBrainDir')
        self.modelDirections.setHeaderData(3, QtCore.Qt.Horizontal, 'Opposite')
        self.modelDirections.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.modelDirections.select()

        databaseConn.close()


def querySet(databaseConn, window, queryTexts):
    # Define and execute a set of queries against the database

    # Initiate transaction
    #QtSql.QSqlDatabase.database().transaction()
    databaseConn.database().transaction()

    # Iterate through supplied queries, executing and reporting success/fail
    sqlOk = 1
    for queryText in queryTexts:
        if type(queryText) is QtCore.QString:
            printable = queryText.toUtf8()
        else:
            printable = queryText.encode('utf8')
        print printable
        query = QtSql.QSqlQuery()
        sqlOk = query.exec_(queryText)
        if sqlOk != 1:
            break

    # Either detect any errors and rollback, or otherwise commit.
    if sqlOk == 1:
        databaseConn.database().commit()
        print 'Committed'
    else:
        message = QtGui.QMessageBox.critical(None, 'Error',
        query.lastError().text())
        databaseConn.database().rollback()


def createDirection(self): #################################### TODO: Make these 2 methods work!
    # Add a new record to the DIRECTIONS table.

    """createDirection = self.modelDirections.insertRows(
    self.modelDirections.rowCount(), 1)
    print createDirection
    print self.modelDirections.rowCount()
    print self.modelDirections.lastError().databaseText()"""

    # Define and execute query to determine current max direction serial
    model = QtSql.QSqlQueryModel()
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
    model = QtSql.QSqlQueryModel()
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


def createRelation(window, sourceNodeID, dir, sidedness):
    # Create a related node to the active node and associated links

    databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

    # Display input box querying for name value
    entry, ok = QtGui.QInputDialog.getText(None, 'Enter name for new Thing',
    'Name:', QtGui.QLineEdit.Normal, '')
    # Detect invalid names and abort (return) method if necessary
    if ok and not entry == '':
        newName = entry
    else:
        return

    # Get a new GUIDs and date/timestamp
    GUID0, GUID1, GUID2 = uuid4(), uuid4(), uuid4()
    timeDateStamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Define and execute query to determine current max node serial
    model = QtSql.QSqlQueryModel()
    query = 'SELECT * FROM thoughts WHERE id=(SELECT MAX(id) FROM thoughts)'
    model.setQuery(query)
    newNodeSerial = str(int(model.record(0).value('id').toString()) + 1)

    # Define and execute query to determine current max link serial
    model = QtSql.QSqlQueryModel()
    query = 'SELECT * FROM links WHERE id=(SELECT MAX(id) FROM links)'
    model.setQuery(query)
    linkSerial1 = str(int(model.record(0).value('id').toString()) + 1)
    linkSerial2 = str(int(model.record(0).value('id').toString()) + 2)

    # Determine the opposite and TheBrain classic direction numbers from the
    # relation direction
    model = QtSql.QSqlQueryModel()
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
    queries = querySet(databaseConn, window, queryTexts)
    databaseConn.close()
    window.viewNetwork.setActiveNode()


def deleteRelation(window, nodeID):
    # Delete a node and all its relations.

    databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

    # Display input box querying to continue or not
    confirm = QtGui.QMessageBox.question(None, 'Confirm delete',
    'Delete this node?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    # Either call the delete method or abort
    if confirm == QtGui.QMessageBox.Yes:

        # Define and execute query to determine whether notes item exists
        model = QtSql.QSqlQueryModel()
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
        queries = querySet(databaseConn, window, queryTexts)
        databaseConn.close()
        window.viewNetwork.setActiveNode()
    else:
        databaseConn.close()
        print 'Canceled...'




def createRelationship(window, sourceNodeID, sourceDir, destNodeID,
    destDir, sidedness):
    # Create a relationship link from one node to another

    databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

    # If method would link a node to itself, display error and return
    if sourceNodeID == destNodeID:
        message = QtGui.QMessageBox.critical(None, 'Error',
        'Can\'t relate a Thing to itself!')
        return

    # Determine the opposite direction from the relation direction
    model = QtSql.QSqlQueryModel()
    query = 'SELECT * FROM directions WHERE id=(' + str(sourceDir) + ')'
    model.setQuery(query)
    theBrainDirSource = int(model.record(0).value('thebraindir'\
    ).toString())
    sourceDirOpposite = int(model.record(0).value('opposite').toString())

    # If method would create paired relationships which are not opposites
    # of one another, display error and return
    if destDir != sourceDirOpposite:
        #message = QtGui.QMessageBox.critical(None, 'Error',
        #'You can\'t relate two Things with relationship types that are \
        #not opposites!')
        return

    # Display input box querying to continue or not
    confirm = QtGui.QMessageBox.question(None, 'Create relationship?',
    'Create relationship?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    # Either call the delete method or abort
    if confirm == QtGui.QMessageBox.Yes:
        # Get a new GUIDs and date/timestamp
        GUID0, GUID1 = uuid4(), uuid4()
        timeDateStamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'\
        )[:-3]

        # Define and execute query to determine current max link serial
        model = QtSql.QSqlQueryModel()
        query = 'SELECT * FROM links WHERE id=(SELECT MAX(id) FROM links)'
        model.setQuery(query)
        linkSerial1 = str(int(model.record(0).value('id').toString()) + 1)
        linkSerial2 = str(int(model.record(0).value('id').toString()) + 2)

        # Determine the TheBrain classic direction numbers from the relation
        # direction
        model = QtSql.QSqlQueryModel()
        query = 'SELECT * FROM directions WHERE id=(' + str(sourceDir) + ')'
        model.setQuery(query)
        theBrainDirSource = int(model.record(0).value('thebraindir'\
        ).toString())

        model = QtSql.QSqlQueryModel()
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
        queries = querySet(databaseConn, window, queryTexts)
        databaseConn.close()
        window.viewNetwork.setActiveNode()
    else:
        databaseConn.close()
        print 'Canceled...'


def deleteRelationships(window, relationshipID):###################### Change this so you can input any number of relationship IDs
    # Delete a node and all its relations.

    databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')

    relationshipIDs = [str(relationshipID), str(
    window.oppositeLinkIDs[relationshipID])]

    # Display input box querying to continue or not
    confirm = QtGui.QMessageBox.question(None, 'Confirm delete',
    'Delete this relationship (and any opposite relationship)?',
    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    # Either call the delete method or abort
    if confirm == QtGui.QMessageBox.Yes:

        # Define queries to delete links
        queryTexts = [
        "DELETE FROM links WHERE (id=" + \
        ') or id=('.join(relationshipIDs) + ')'
        ]

        # Execute queries, then refresh the network view
        queries = querySet(databaseConn, window, queryTexts)
        databaseConn.close()
        window.viewNetwork.setActiveNode()

    else:
        databaseConn.close()
        print 'Canceled...'


def saveNotes(databaseConn, notesText):

    # Define and execute query to determine whether notes item exists
    model = QtSql.QSqlQueryModel()
    query = 'SELECT * FROM entries WHERE id=' + \
    str(databaseConn.window.notesID)
    model.setQuery(query)
    timeDateStamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'
    )[:-3]
    if model.record(0).value('id').toString() == '':
        print 'No notes for this node. Creating notes.'

        # Define and execute query to determine current max note serial
        model = QtSql.QSqlQueryModel()
        query = 'SELECT * FROM entries WHERE id=(SELECT MAX(id) FROM \
        entries)'
        model.setQuery(query)
        newEntrySerial = str(int(model.record(0).value('id').toString()) + \
        1)

        # Define/execute query to determine current max note-linker serial
        model = QtSql.QSqlQueryModel()
        query = 'SELECT * FROM entrytoobject WHERE id=(SELECT MAX(id) FROM \
        entrytoobject)'
        model.setQuery(query)
        newLinkSerial = str(int(model.record(0).value('id').toString()) + \
        1)

        GUID = uuid4()

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
        databaseConn.window.viewNetwork.activeNodeID, newEntrySerial, 1)
        ]

        # Execute queries, then refresh the notes view
        queries = databaseConn.querySet(queryTexts)
        databaseConn.window.renderNotes()
    else:
        # Define queries to update notes text
        queryTexts = [
        "UPDATE entries SET body=N\'" + notesText +
        "\' WHERE id=" + str(databaseConn.window.notesID),
        #
        "UPDATE entries SET modificationdatetime=N\'" + timeDateStamp +
        "\' WHERE id=" + str(databaseConn.window.notesID)
        ]

        # Execute queries
        queries = databaseConn.querySet(queryTexts)


def databaseInfo(window, GUID=None):

    databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')
    #print 'databaseInfo' #foo
    model = QtSql.QSqlQueryModel()
    # Define and execute query
    if GUID != None:
        query = 'SELECT * FROM brains WHERE guid=\'' + str(GUID) + '\''
    else:
        query = 'SELECT * FROM brains'
    model.setQuery(query)

    if model.rowCount() == 0:
        GUID = None
    else:
        GUID = model.record(0).value('GUID').toString()

    databaseConn.close()

    return GUID




def axisDirectionsInfo(window, *dirs):

    databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')
    #print 'axisDirectionsInfo'  #foo
    # Define and execute query to retrieve direction info
    dirList = []
    for dir in dirs:
        dirList.append(str(dir))
    model = QtSql.QSqlQueryModel()
    query = 'SELECT * FROM directions WHERE id=(' + \
    ') or id=('.join(dirList) + ')'
    model.setQuery(query)

    directionIDs = []
    directionOpposites = []
    directionTexts = []
    for row in range(0, model.rowCount()):
        directionIDs.append(int(model.record(row).value('id').toString()))
        directionOpposites.append(int(model.record(row).value(
        'opposite').toString()))
        directionTexts.append(str(model.record(row).value('text').toString()))

    databaseConn.close()

    return directionIDs, directionOpposites, directionTexts



def nodeDBInfo(window, nodeID=None, nodeGUID=None, nodeName=None):

    #print 'nodeDBinfo'  #foo
    listNumber = False

    if not (nodeID or nodeGUID or nodeName):
        print 'Error! No information entered for query!'
        return

    # Define and execute query
    model = QtSql.QSqlQueryModel()
    queryArgs = [nodeID, nodeGUID, nodeName]
    queryParts = ['id=%s' % str(nodeID), 'guid=\'%s\'' % str(nodeGUID),
    'name=\'%s\'' % str(nodeName)]
    query = 'SELECT * FROM thoughts WHERE ' + ' and '.join(
    [queryParts[i] for i in range(len(queryArgs)) if queryArgs[i] != None])
    model.setQuery(query)
    if model.rowCount() != 0:
        nodeID = str(model.record(0).value('id').toString())
    else:
        nodeID = None
    nodeGUID = str(model.record(0).value('GUID').toString())
    nodeName = str(model.record(0).value('name').toString())

    return nodeID, nodeGUID, nodeName


def notesInfo(window, nodeID=1):

    databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')
    #print 'notesInfo'  #foo
    listNumber = False

    # Define and execute query for linker from node to notes
    modelNodeToNotes = QtSql.QSqlQueryModel()
    query = 'SELECT * FROM entrytoobject WHERE objectid=' + str(nodeID)
    modelNodeToNotes.setQuery(query)
    notesID = modelNodeToNotes.record(0).value('entryid').toString()

    # Define and execute query for the notes themselves
    modelNotes = QtSql.QSqlQueryModel()
    query = 'SELECT * FROM entries WHERE id=' + str(notesID)
    modelNotes.setQuery(query)

    notesID = modelNotes.record(0).value('id').toString()
    notesText = modelNotes.record(0).value('body').toString()

    databaseConn.close()

    return notesID, notesText


def linksIDs(window, activeNodeID, dirs=[1]):

    """databaseConn = Brain2(window,
    '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')"""
    #print 'linksIDs'  #foo
    listNumber = False
    dirsAndOppositeDirs = dirs + window.axisAssignmentOpposites.values()
    destLinksModel = QtSql.QSqlQueryModel()
    destAndReturnLinksModel = QtSql.QSqlQueryModel()

    # Define and execute queries
    query = 'SELECT * FROM links WHERE (ida=' + str(activeNodeID) + \
    ' or idb=' + str(activeNodeID) + ') and direction IN (' + \
    ', '.join(str(dir) for dir in dirs) + ')'
    destLinksModel.setQuery(query)

    query = 'SELECT * FROM links WHERE (ida=' + str(activeNodeID) + \
    ' or idb=' + str(activeNodeID) + ') and direction IN (' + \
    ', '.join(str(dir) for dir in dirsAndOppositeDirs) + ')'
    destAndReturnLinksModel.setQuery(query)

    # Determines whether all or only a fixed number of links are queried
    if listNumber == False:
        end = destLinksModel.rowCount()
    else:
        end = listNumber

    # Adds the nodes to a list
    destNodeIDs = []
    for i in range(0, end):
        if destLinksModel.record(i).value('ida') == activeNodeID:
            destNodeIDs.append(
            destLinksModel.record(i).value('idb').toString())
        # There are actually 2 links for each visible link. Double links are
        # created at the same time, and have sequential IDs. We are ignoring
        # the second one, but the code below would reinstantiate it (and
        # create false link nodes "mirroring" the active node).


    # Create dictionaries of forward and reverse links for each node, with
    # Nones if there are no links in that direction.
    linkIDs_forward = {}
    linkIDs_reverse = {}
    for i in range(0, len(destNodeIDs)):
        destNodeID = int(destNodeIDs[i])
        linkIDs_forward.update({destNodeID: None})
        linkIDs_reverse.update({destNodeID: None})
        for j in range(0, destAndReturnLinksModel.rowCount()):
            if int(destAndReturnLinksModel.record(j).value('idb').toString()) == destNodeID:
                linkIDs_forward[destNodeID] = int(destAndReturnLinksModel.record(j).value('id').toString())
            if int(destAndReturnLinksModel.record(j).value('ida').toString()) == destNodeID:
                linkIDs_reverse[destNodeID] = int(destAndReturnLinksModel.record(j).value('id').toString())
            # There are actually 2 links for each visible link. Double links are
            # created at the same time, and have sequential IDs.

    """databaseConn.close()"""

    # Returns the related node IDs and relationship IDs
    return destNodeIDs, linkIDs_forward, linkIDs_reverse
