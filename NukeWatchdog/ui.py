import sys
from PySide import QtCore, QtGui


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setCentralWidget(JobList())
        self.setWindowTitle('Hello')
        self.show()


class JobList(QtGui.QWidget):
    def __init__(self, parent=None):
        super(JobList, self).__init__(parent)

        self.layout = QtGui.QVBoxLayout()

        self.list = QtGui.QListWidget()
        self.list.addItems(['hello', 'dicks'])
        self.layout.addWidget(self.list)

        self.setLayout(self.layout)

    def updateList(self, pool):

        jobs = pool.currentActive()
        print jobs

        # self.list.clear()
        # for job in jobs:
        #     item = QtGui.QListWidgetItem()
        #     item.setText(str(job))
        #     self.list.addItem(item)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())
