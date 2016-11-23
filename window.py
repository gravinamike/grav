#! python3
#File: brainDB.py

"""
DESCRIPTION GOES HERE

author: Mike Gravina
last edited: August 2016
"""

import sys
import grav.db as db
from PyQt4.QtCore import(Qt, QCoreApplication)
from PyQt4.QtGui import(QIcon, QFont, QPainter, QMainWindow, QApplication,
QWidget, QDesktopWidget, QToolTip, QPushButton, QMessageBox, QAction, qApp,
QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, QTextEdit, QTableView,
QPen)


class NodeGraphic:
    # A graphical representation of a node containing a database model which
    # defines text and links with other nodes.
    def __init__(self, nodeID=1, centerX=250, centerY=200):
        # Define DB model for node
        self.nodeDBModel = db.nodeDBModel(nodeID)
        # Define node graphic geometry
        self.centerX = centerX
        self.centerY = centerY
        self.width = 100
        self.height = 50
        self.sourceAnchor = self.Anchor((self.centerX+self.width/2), self.centerY)
        self.destAnchor = self.Anchor((self.centerX-self.width/2), self.centerY)
        # Define node graphic text
        self.text = None

    def changeModel(self, nodeDBModelID):
        self.nodeDBModel = db.nodeDBModel()
        self.nodeDBModel.changeNodeID(nodeID=nodeDBModelID)

    def changePos(self, centerX, centerY):
        self.centerX = centerX
        self.centerY = centerY
        self.sourceAnchor.changePos((self.centerX+self.width/2), self.centerY)
        self.destAnchor.changePos((self.centerX-self.width/2), self.centerY)

    def changeDimensions(self, width, height):
        self.width = width
        self.height = height
        self.sourceAnchor.changePos((self.centerX+self.width/2), self.centerY)
        self.destAnchor.changePos((self.centerX-self.width/2), self.centerY)

    class Anchor:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def changePos(self, x, y):
            self.x = x
            self.y = y


class LinkGraphic:
    def __init__(self):
        self.sourceAnchor = None
        self.destAnchor = None

    def changeAnchors(self, sourceAnchor, destAnchor):
        self.sourceAnchor = sourceAnchor
        self.destAnchor = destAnchor


class Window(QMainWindow):
    # Implements a window widget displaying nodes in the database

    def __init__(self):
        # Initialization from superclass and call to class constructor
        super(Window, self).__init__()
        # Define Brain that is shown in window
        self.brain = db.Brain()
        # Define active node graphic
        self.activeNodeID = 30
        self.activeNodeGraphic = NodeGraphic(nodeID=self.activeNodeID)
        # Define link node graphics
        self.activeLinks = db.linksDBModel()
        self.activeLinks.setActiveNode(self.activeNodeID)
        self.destNodeIDs = self.activeLinks.destNodeIDs()
        relationTop = 100
        self.activeLinkNodeGraphics = []
        for i in range(len(self.destNodeIDs)):
            nodeGraphic = NodeGraphic(
                nodeID=self.destNodeIDs[i],
                centerX=400,
                centerY=relationTop+60*i
            )
            self.activeLinkNodeGraphics.append(nodeGraphic)
        # Initialize the window user interface
        self.initUI()


    def initUI(self, labelText=None):
        """ Window constructor. Sets window geometry, window title,
        window icon, menu bar, tool bar, status bar, tool tip, and quit
        button. Creates the display object."""
        # Set basic config of window
        self.resize(500, 400)
        self.center()
        # You can handle the size/position like this too:
        # self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Grav\'s window')
        self.setWindowIcon(QIcon('web.png'))
        # Set up actions for window
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
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
        #Display the window
        self.show()

    def center(self):
        # Centers window in desktop
        frame = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(centerPoint)
        self.move(frame.topLeft())

    def paintEvent(self, e):
        # This is where all the nodes and links are drawn
        qp = QPainter()
        qp.begin(self)
        # Draw active node
        self.drawNode(qp, self.activeNodeGraphic)
        # Draw sibling nodes and links
        for i in range(len(self.destNodeIDs)):
            self.drawNode(qp, self.activeLinkNodeGraphics[i])
            self.drawLink(qp, self.activeNodeGraphic.sourceAnchor,
            self.activeLinkNodeGraphics[i].destAnchor)
        qp.end()

    def drawNode(self, qp, nodeGraphic):
        # This defines how a node graphic is drawn on the window
        # Draw the rectangle
        node = qp.drawRoundedRect(
            nodeGraphic.centerX-nodeGraphic.width/2,
            nodeGraphic.centerY-nodeGraphic.height/2, nodeGraphic.width,
            nodeGraphic.height, 10, 10
        )
        # THIS IS THE NEW PART!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #node.mouseReleaseEvent = self.changeActiveNode(nodeID=nodeGraphic.nodeDBModel.model.record(0).value('name').toString())
        # Draw the text
        qp.drawText(
            nodeGraphic.centerX-nodeGraphic.width/2+5,
            nodeGraphic.centerY-nodeGraphic.height/2+25,
            nodeGraphic.nodeDBModel.model.record(0).value('name').toString()
        )

    def drawLink(self, qp, anchor1, anchor2):
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(anchor1.x, anchor1.y, anchor2.x, anchor2.y)

# VERIFY THAT THIS DOES SOMETHING AND IS BUILT RIGHT!!!
    def changeActiveNode(self, event, nodeID=1):
        self.activeNodeID = nodeID
        self.activeNode = db.nodeDBModel(nodeID=self.activeNodeID)
        self.activeLinks = db.linksDBModel(activeNode=self.activeNodeID)

    def closeEvent(self, event):
        # Redefines superclass close event with a message box to confirm quit
        reply = QMessageBox.question(self, 'Confirm exit',
        'Are you sure you want to quit?', QMessageBox.Yes |
        QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


#Code to make module into script-----------
if __name__ == "__main__":

    app = QApplication(sys.argv)
    newWindow = Window()
    sys.exit(app.exec_())
#------------------------------------------

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
#  Loose code below:
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###


"""        # Create an independently positioned label
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

        self.setCentralWidget(self.view) #stretchBox





            def close(self):
                self.__database.close()
                self.__database.removeDatabase()




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



    def query(self, queryString='SELECT * FROM thought'):
        query = QSqlQuery()
        query.exec_(queryString)
        # If call fails exec() returns false; info at QSqlDatabase.lastError()
        query.next()
        print str(query.value(0))




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



    def changeLabel(self, labelText='New text!'):

        # Changes text of label
        self.label1.setText(labelText)

    def changeTableView(self, newModel):
        # Changes model of table view
        self.view.setModel(newModel)





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

        print model.rowCount()
        input('Press enter...')

        for i in range(0, end):
            id = model.record(i).value('id').toInt()
            guid = model.record(i).value('guid').toString()
            #This thing was next:       qDebug() << name << salary
            stringOutput.append(str(id))
            stringOutput.append(guid)
            stringOutput.append('\n')
            #print str(id), guid

        return(' '.join(stringOutput))





        self.windowText = 'This is the default text'
        self.viewModel = QSqlQueryModel()


        # Set up window-wide tooltip
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This is <b>Grav\'s</b> window.')



                """
