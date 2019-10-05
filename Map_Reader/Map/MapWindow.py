import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, QJsonValue, QVariant
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import webbrowser
import sys
import json
import random


class MapWindow(QDialog):
    def __init__(self, api, ref, points):
        super(MapWindow, self).__init__()
        self.api = api
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
        self.mapView = QWebEngineView()

        self.webchannel = QWebChannel(self.mapView)
        self.mapView.page().setWebChannel(self.webchannel)
        self.webchannel.registerObject('backend', self)

        current_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(current_dir, 'index.html')
        self.mapView.load(QUrl.fromLocalFile(filename))

        layout.addWidget(self.mapView)
        self.setLayout(layout)

    #pass reference point to index.html
    @pyqtSlot(result=list)
    def getRef(self):
        return [{'lat': self.ref[0], 'lng': self.ref[1]}]

    #pass reference point to index.html
    @pyqtSlot(result=list)
    def getPoints(self):
        gmapsPoints = [{
            'Point': {'lat': p['Latitude'], 'lng': p['Longitude']},
            'Description': p['Description'],
            'Date': p['Date']
        } for p in self.points]

        return gmapsPoints


    def closeEvent(self, event):
        sys.exit()