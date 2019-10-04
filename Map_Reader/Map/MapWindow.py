from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, QJsonValue, QVariant
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import webbrowser
import sys
import json


class MapWindow(QDialog):
    def __init__(self, ref, points):
        super(MapWindow, self).__init__()
        
        self.ref = ref
        self.points = points

        self.setFixedSize(1080, 768)
        self.setWindowTitle('Map')
        self.setModal(True)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.initUI()

        self.show()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        layout = QVBoxLayout()

        # setup a page with my html
        
        
        self.mapView = QWebEngineView()

        self.webchannel = QWebChannel(self.mapView)
        self.mapView.page().setWebChannel(self.webchannel)
        self.webchannel.registerObject('backend', self)
        self.mapView.load(QUrl('file:///index.html'))

        layout.addWidget(self.mapView)
        self.setLayout(layout)

    @pyqtSlot(result=list)
    def getRef(self):
        return [{'lat': self.ref[0], 'lng': self.ref[1]}]

    @pyqtSlot(list)
    def printRef(self, ref):
        ref, *_ = ref
        print('inside printRef:', ref)

    def closeEvent(self, event):
        sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MapWindow((37.12345, -120.12345), None)
    sys.exit(app.exec_())