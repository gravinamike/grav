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

import sys
from PyQt4.QtCore import(Qt, QCoreApplication)
from PyQt4.QtGui import(QIcon, QFont, QPainter, QMainWindow, QApplication,
QWidget, QDesktopWidget, QToolTip, QPushButton, QMessageBox, QAction, qApp,
QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QTextEdit, QTableView,
QPen)
from PyQt4.QtSql import(QSqlDatabase, QSqlQuery, QSqlQueryModel,
QSqlTableModel, QSqlRelationalTableModel, QSqlRelation)
import site


class Brain:

    def __init__(self):

        site_pack_path = site.getsitepackages()[1]
        QApplication.addLibraryPath('{0}\\PyQt5\\plugins'.format(site_pack_path))

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
        #SSL mode   disable
        #server-side prepare

        # Open database and give access to data. If call fails it
        # returns false; error info obtained from QSqlDatabase.lastError()
        ok = self.__database.open()
        if ok == False:
            print 'Could not open database'
            print 'Text: ', self.__database.lastError().text()
            print 'Type: ', str(self.__database.lastError().type())
            print 'Number: ', str(self.__database.lastError().number())
            print 'Loaded drivers:', str(QSqlDatabase.drivers())


    def close(self):

        self.__database.close()
        self.__database.removeDatabase()


    def query(self, queryString=
    'SELECT * FROM thought'):

        query = QSqlQuery()
        query.exec_(queryString)
        # If call fails exec() returns false; info at QSqlDatabase.lastError()
        query.next()
        print str(query.value(0))


    def queryModel(self, queryString=
    'SELECT * FROM thoughts', listNumber=False):
        #A read-write model based on a SQL query

        model = QSqlQueryModel()
        model.setQuery(queryString)

        if listNumber == False:
            end = model.rowCount()-1
        else:
            end = listNumber

        stringOutput = []

        """print model.rowCount()
        input('Press enter...')"""

        for i in range(0, end):
            id = model.record(i).value('id').toInt()
            guid = model.record(i).value('guid').toString()
            #This thing was next:       qDebug() << name << salary
            stringOutput.append(str(id))
            stringOutput.append(guid)
            stringOutput.append('\n')
            #print str(id), guid

        return(' '.join(stringOutput))


    def tableModel(self, table='PUBLIC.THOUGHTS', filter='id < 11'):
        #A read-write model that works on a single SQL table at a time

        model = QSqlTableModel()
        model.setTable(table)
        model.setFilter(filter)
        model.setSort(1, Qt.DescendingOrder)
        model.select()

        print model.rowCount()
        input('Press enter...')

        for i in range(1, model.rowCount()):
            id = model.record(i).value('id').toInt()
            guid = model.record(i).value('guid').toString()
            #This thing was next:       qDebug() << name << salary
            print str(id), guid

        return(model)


    def relationalModel(self, table='PUBLIC.LINKS', filter='id < 11'):
        #A read-write model that works on relations

        model = QSqlRelationalTableModel()
        model.setTable(table)
        model.setFilter(filter)
        model.setSort(1, Qt.DescendingOrder)
        key = model.primaryKey()
        model.setRelation(3, QSqlRelation('PUBLIC.THOUGHTS', 'id', 'name'))
        model.setRelation(4, QSqlRelation('PUBLIC.THOUGHTS', 'id', 'name'))
        model.setPrimaryKey(key)
        model.select()

        # print model.rowCount()
        input('Press enter...')

        for i in range(1, model.rowCount()):
            id = model.record(i).value('id').toInt()
            guid = model.record(i).value('guid').toString()
            #This thing was next:       qDebug() << name << salary
            print  str(id), guid

        return(model)


    def nodeModel(self, activeNode=1, listNumber=False):
        #A read-write model based on a SQL query on the THOUGHTS table

        model = QSqlQueryModel()
        query = 'SELECT * FROM thoughts WHERE id=' + str(activeNode)
        model.setQuery(query)

        return(model)


    def linkModel(self, activeNode=1, listNumber=False):
        #A read-write model based on a SQL query on the LINKS table

        model = QSqlQueryModel()
        query = 'SELECT * FROM links WHERE ida=' + str(activeNode) + \
        ' or idb=' + str(activeNode)
        model.setQuery(query)

        if listNumber == False:
            end = model.rowCount()-1
        else:
            end = listNumber

        stringOutput = []

        for i in range(0, end):
            id = model.record(i).value('id').toInt()
            guid = model.record(i).value('guid').toString()
            stringOutput.append(str(id))
            stringOutput.append(guid)
            stringOutput.append('\n')

        return(model)


# A QWidget is a less specific form of window - QMainWindow has menubars, etc.
class Window(QMainWindow):

    def __init__(self):
        # Initialization from superclass and call to class constructor
        super(Window, self).__init__()

        self.windowText = 'This is the default text'
        self.viewModel = QSqlQueryModel()

        self.brain = Brain()
        self.activeNodeID = 30
        self.activeNode = self.brain.nodeModel(activeNode=self.activeNodeID)
        self.activeLinks = self.brain.linkModel(activeNode=self.activeNodeID)

        self.initUI()


    def initUI(self, labelText=None):
        """ Window class constructor. Sets window geometry, window title,
        window icon, menu bar, tool bar, status bar, tool tip, and quit
        button. Creates the display object."""

        # Set basic config of window
        self.resize(500, 400)
        self.center()
        # You can handle the size/position like this too:
        # self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Grav\'s window')
        self.setWindowIcon(QIcon('web.png'))

        # Set up window-wide tooltip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This is <b>Grav\'s</b> window.')

        # Set up actions for window
        exitAction = QAction(QIcon('exit24.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        # Set up menu bar, tool bar, status bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)

        self.statusBar().showMessage('Ready')

        # Create a quit button
        quitButton = QPushButton('Quit', self)
        quitButton.clicked.connect(QCoreApplication.instance().quit)
        quitButton.resize(quitButton.sizeHint())
        quitButton.move(50, 100)
        quitButton.setToolTip('This is a quit button.')

        #Create a relational table view
        self.view = QTableView()
        self.view.setModel(self.viewModel)
        self.view.move(50, 200)

        """# Create an independently positioned label
        if labelText == None:
            labelText = self.windowText

        self.label1 = QLabel(labelText, self)
        self.label1.move(50, 150)
        self.label1.resize(200, 200)

        # Create a grid layout widget
        grid = QGridLayout()
        grid.setSpacing(10)

        gridNames = ['11', '', '', '14',
                     '21', '', '23', 'TEST',
                     '?', '', '33', '34']

        positions = [ (i,j) for i in range(3) for j in range (4)]

        for position, name in zip(positions, gridNames):
            if name == '':
                continue
            button = QPushButton(name)
            grid.addWidget(button, *position)

        lineEdit = QLineEdit()
        textEdit = QTextEdit()

        grid.addWidget(lineEdit, 0, 1)
        grid.addWidget(textEdit, 1, 1, 2, 1)

        gridBox = QWidget()
        gridBox.setLayout(grid)

        # Create a central widget of the main window with a stretch
        # factor layout, and include the grid layout from above
        stretchBox = QWidget()

        upButton = QPushButton('Up')
        downButton = QPushButton('Down')

        hbox = QHBoxLayout()
        hbox.addWidget(gridBox)
        hbox.addStretch(1)
        hbox.addWidget(upButton)
        hbox.addWidget(downButton)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        stretchBox.setLayout(vbox)

        self.setCentralWidget(self.view) #stretchBox"""

        #Display the window
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawNodes(qp, nodeCenter=[200, 175])
        self.drawLinks(qp)
        qp.end()

    def drawNodes(self, qp, nodeCenter):
        nodeWidth = 100
        nodeHeight = 50
        linkVertex = nodeCenter[0] + nodeWidth/2

        qp.drawRoundedRect(nodeCenter[0], nodeCenter[1], nodeWidth, nodeHeight, 10, 10)
        qp.drawText(nodeCenter[0]+5, nodeCenter[1]+25, self.activeNode.record(0).value('name').toString())

    def drawLinks(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)

        qp.setPen(pen)
        qp.drawLine(250, 225, 400, 200)

    def changeLabel(self, labelText='New text!'):

        # Changes text of label
        self.label1.setText(labelText)

    def changeTableView(self, newModel):

        # Changes model of table view
        self.view.setModel(newModel)

    def changeActiveNode(self, nodeID=1):

        # Changes text of label
        self.activeNodeID = nodeID
        self.activeNode = self.brain.nodeModel(activeNode=self.activeNodeID)
        self.activeLinks = self.brain.linkModel(activeNode=self.activeNodeID)

    def closeEvent(self, event):

        # Redefines superclass close event with a message box to confirm quit
        reply = QMessageBox.question(self, 'Confirm exit',
        'Are you sure you want to quit?', QMessageBox.Yes |
        QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):

        # Centers window in desktop
        frame = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(centerPoint)
        self.move(frame.topLeft())


class Anchor:
    def __init__(self):
        self.x = 1
        self.y = 1

    def changePos(x, y):
        self.x = x
        self.y = y


class Node:
    def __init__(self):
        self.centerX = 200
        self.centerY = 175
        self.width = 100
        self.height = 50
        self.linkAnchor = Anchor()
        self.linkAnchor.changePos(self.centerX+self.width/2, self.centerY)
        self.text = None


#Code to make module into script-----------
if __name__ == "__main__":

    app = QApplication(sys.argv)
    #newBrain = Brain()
    newWindow = Window()
    #newWindow.changeLabel(newBrain.queryModel())
    #newWindow.changeTableView(newBrain.relationalModel(filter=None))
    sys.exit(app.exec_())
#------------------------------------------
