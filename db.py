#! python3
#File: brainDB.py

"""
Interface between grav package and TheBrain H2 database, making use of
ODBC PostgreSQL adaptor and PyQt database module.
Using code from http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/
BUILD/PyQt-x11-gpl-4.7.2/doc/html/qtsql.html#connecting-to-databases

author: Mike Gravina
last edited: August 2016
"""

import site
from PyQt4.QtCore import(Qt, QCoreApplication)
from PyQt4.QtGui import(QApplication)
from PyQt4.QtSql import(QSqlDatabase, QSqlQuery, QSqlQueryModel,
QSqlTableModel, QSqlRelationalTableModel, QSqlRelation)


class Brain:
    def __init__(self):
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
    def __init__(self):
        self.nodeID = 1
        listNumber = False

        self.model = QSqlQueryModel()
        query = 'SELECT * FROM thoughts WHERE id=' + str(self.nodeID)
        self.model.setQuery(query)

    def changeNodeID(self, nodeID):
        self.nodeID = nodeID
        query = 'SELECT * FROM thoughts WHERE id=' + str(self.nodeID)
        self.model.setQuery(query)


class linksDBModel:
    #A read-write model based on a SQL query on the LINKS table
    def __init__(self):
        self.listNumber = False
        self.model = QSqlQueryModel()

    def setActiveNode(self, activeNodeID):
        self.activeNodeID = activeNodeID
        query = 'SELECT * FROM links WHERE ida=' + str(self.activeNodeID) + \
        ' or idb=' + str(self.activeNodeID)
        self.model.setQuery(query)

    def destNodeIDs(self):
        if self.listNumber == False:
            end = self.model.rowCount()-1
        else:
            end = self.listNumber

        destNodeIDs = []
        for i in range(0, end):
            if self.model.record(i).value('ida').toInt() == self.activeNodeID:
                destNodeIDs.append(self.model.record(i).value('idb').toInt())
            else:
                destNodeIDs.append(self.model.record(i).value('ida').toInt())

        return(destNodeIDs)


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
#  Loose code below:
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

"""
        stringOutput = []
        for i in range(0, end):
            id = model.record(i).value('id').toInt()
            guid = model.record(i).value('guid').toString()
            stringOutput.append(str(id))
            stringOutput.append(guid)
            stringOutput.append('\n')"""
