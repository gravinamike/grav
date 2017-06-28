
import sys
import site
from subprocess import Popen
from PyQt4.QtCore import(Qt, QSignalMapper)
from PyQt4.QtGui import(QMainWindow, QApplication, QWidget, QPushButton, qApp,
QVBoxLayout, QTableView, QApplication, QAbstractItemView)
from PyQt4.QtSql import(QSqlDatabase, QSqlQuery, QSqlQueryModel, QSqlTableModel)


class Window(QMainWindow):
    # Instantiates a Brain object that links to an active H2 database

    def __init__(self):

        super(Window, self).__init__()
        # Initialize Brain that is shown in window

        self.h2 = Popen(["java", "-cp",
        "C:/Program Files (x86)/TheBrain/lib/h2.jar", "org.h2.tools.Server",
        "-pg"])

        site_pack_path = site.getsitepackages()[1]
        QApplication.addLibraryPath(
        '{0}\\PyQt5\\plugins'.format(site_pack_path))

        self.__database = QSqlDatabase.addDatabase('QPSQL')
        self.__database.setHostName('localhost')
        self.__database.setDatabaseName(
        '~/Desktop/H2 testing/TESTING_LifeLoop_brain/brain_db/brain')
        self.__database.setPort(5435) #Possibly redundant
        self.__database.setUserName('sa')
        self.__database.setPassword('Th1nkingM0re')

        ok = self.__database.open()
        if ok == False:
            print 'Could not open database'
            print 'Text: ', self.__database.lastError().text()
            print 'Type: ', str(self.__database.lastError().type())
            print 'Number: ', str(self.__database.lastError().number())
            print 'Loaded drivers:', str(QSqlDatabase.drivers())



        self.modelDirections = QSqlTableModel(None, self.__database)
        self.modelDirections.setTable('PUBLIC.DIRECTIONS')
        #self.modelDirections.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.modelDirections.setEditStrategy(QSqlTableModel.OnRowChange)
        self.modelDirections.select()


        self.modelDirections.dataChanged.connect(self.saveIt) ######################## now transfer the model data to the database


        self.tableDirections = QTableView()
        self.tableDirections.setModel(self.modelDirections)
        #self.tableDirections.setEditTriggers(QAbstractItemView.DoubleClicked)


        self.buttonAddDir = QPushButton('Add direction')
        self.buttonAddDir.clicked.connect(self.createDirection)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tableDirections)
        vbox.addWidget(self.buttonAddDir)

        stretchBox = QWidget()
        stretchBox.setLayout(vbox)
        self.setCentralWidget(stretchBox)
        self.show()



    def createDirection(self):

        # Define and execute query to determine current max direction serial
        model = QSqlQueryModel()
        query = 'SELECT * FROM directions WHERE id=(SELECT MAX(id) FROM directions)'
        model.setQuery(query)
        if model.record(0).value('id').toString() == '':
            newDirectionSerial = 0
        else:
            newDirectionSerial = int(model.record(0).value('id').toString()) + 1

        # Define queries to insert new direction record
        queryText = [
        'INSERT INTO public.directions (id, text, olddir, opposite) \
        VALUES (%s, NULL, 1, NULL)' % (newDirectionSerial)
        ]
        query = QSqlQuery()
        query.exec_(queryText)
        #self.tableDirections.update()


    def saveIt(self):
        success = self.modelDirections.submit()
        print success
        if not success:
            print self.modelDirections.lastError().text()

    def print_out(self):
        print 'Signaled'


    def exitCleanup(self):
        # Final cleanup if window is closed, including shutting down the db
        self.h2.kill()
        print "Database killed!"



#Code to make module into script-----------
if __name__ == "__main__":

    app = QApplication(sys.argv)
    newWindow = Window()
    app.aboutToQuit.connect(newWindow.exitCleanup)
    sys.exit(app.exec_())
