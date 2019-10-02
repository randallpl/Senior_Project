from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from geopy.distance import geodesic
from collections import namedtuple
import webbrowser

from MouseController import MouseController

#Class to confirm the scale input data
class ScaleWindow(QDialog):
    def __init__(self, dist_px, parent=None):
        super(ScaleWindow, self).__init__(parent)

        self.dist_px = dist_px
        self.scale = 1

        self.setFixedSize(300, 100)
        self.setWindowTitle('Scale')
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout() 
        self.pixelEdit = QLineEdit(str(self.dist_px))
        self.pixelEdit.setValidator(QDoubleValidator(0.99, 1000.00, 2))
        self.pixelEdit.textChanged.connect(self.checkFields)
        self.scaleEdit = QLineEdit(str(self.scale))
        self.scaleEdit.setValidator(QDoubleValidator(0.99, 1000.00, 2))
        self.scaleEdit.textChanged.connect(self.checkFields)

        label = QLabel('Pixels:')

        units = ['km', 'm', 'ft', 'mi']
        self.comboBox = QComboBox()
        self.comboBox.addItems(units)

        hLayout.addWidget(label)
        hLayout.addWidget(self.pixelEdit)
        hLayout.addWidget(self.scaleEdit)
        hLayout.addWidget(self.comboBox)

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        if self.pixelEdit.text() and self.scaleEdit.text():
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

    def save(self):
        '''
        Send scale and unit values entered by user back to mouse tracker
        screen when save button is clicked.
        '''
        #Get text values from each element
        scale = eval(self.scaleEdit.text())
        dist_px = eval(self.pixelEdit.text())
        units = self.comboBox.currentText()
        
        #check values entered by user are correct
        
        if scale > 0 and dist_px > 0:
            pxPerUnit = dist_px / scale
            if self.parent():
                self.parent().setScale(pxPerUnit, units) 

            self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.close()
        
#Class to confirm the reference point data
class ReferenceWindow(QDialog):
    def __init__(self, parent=None):
        super(ReferenceWindow, self).__init__(parent)
        self.setFixedSize(300, 100)
        self.setWindowTitle('Add Reference Point')
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout() 
        self.latEdit = QLineEdit()
        self.latEdit.setValidator(QDoubleValidator(-90, 90, 5))
        self.latEdit.setPlaceholderText('Latitude')
        self.latEdit.textChanged.connect(self.checkFields)

        self.lonEdit = QLineEdit()
        self.lonEdit.setValidator(QDoubleValidator(-180, 180, 5))
        self.lonEdit.setPlaceholderText('Longitude')
        self.lonEdit.textChanged.connect(self.checkFields)

        hLayout.addWidget(self.latEdit)
        hLayout.addWidget(self.lonEdit)

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)
        self.saveButton.setEnabled(False)

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        if self.lonEdit.text() and self.latEdit.text():
            self.saveButton.setEnabled(True)

    def save(self):
        '''
        Send reference point back to main window to be stored
        '''
        #Get text values from each element
        lat = eval(self.latEdit.text())
        lon = eval(self.lonEdit.text())
        
        #check values entered by user are correct
        if lat > -90 and lat < 90 and lon > -180 and lon < 180:

            if self.parent():
                self.parent().setReference((lat, lon))
            self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.close()
        
#Class to confirm lat, lon data
class LocationWindow(QDialog):
    def __init__(self, lat, lon, dist, bearing, units, parent=None):
        super(LocationWindow, self).__init__(parent)
        self.lat = lat
        self.lon = lon
        self.dist = dist
        self.bearing = bearing
        self.units = units

        #self.setFixedSize(300, 100)
        self.setWindowTitle('Confirm Location')
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout() 
        self.latEdit = QLineEdit(str(self.lat))
        self.latEdit.setValidator(QDoubleValidator(-90, 90, 5)) 
        self.latEdit.textChanged.connect(self.checkFields)
        self.lonEdit = QLineEdit(str(self.lon))
        self.lonEdit.setValidator(QDoubleValidator(-180, 180, 5))   
        self.lonEdit.textChanged.connect(self.checkFields)

        hLayout.addWidget(QLabel('Lat:'))
        hLayout.addWidget(self.latEdit)

        hLayout.addWidget(QLabel('Lon:'))
        hLayout.addWidget(self.lonEdit)

        #add description box
        self.descBox = QTextEdit()
        self.descBox.setFixedHeight(100)
        self.descBox.setPlaceholderText('Description')

        h2Layout = QHBoxLayout() 

        self.distEdit = QLineEdit(str(self.dist))
        self.distEdit.setValidator(QDoubleValidator(0, 100000000, 5)) 
        self.distEdit.textChanged.connect(self.checkFields)
        self.bearingEdit = QLineEdit(str(self.bearing))
        self.bearingEdit.setValidator(QDoubleValidator(0, 360, 5))
        self.bearingEdit.textChanged.connect(self.checkFields)

        h2Layout.addWidget(QLabel(f'Distance ({self.units}):'))
        h2Layout.addWidget(self.distEdit)

        h2Layout.addWidget(QLabel('Bearing:'))
        h2Layout.addWidget(self.bearingEdit)

        #horizontal layout containing save and cancel buttons
        h3Layout = QHBoxLayout()
        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h3Layout.addWidget(self.saveButton)
        h3Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(h2Layout)
        mainLayout.addWidget(self.descBox)
        mainLayout.addLayout(h3Layout)

        self.mandatoryFields = [self.latEdit, self.lonEdit, self.distEdit, self.bearingEdit]
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''

        if all(t.text() for t in self.mandatoryFields):
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)


    def save(self):
        '''
        Send scale and unit values entered by user back to mouse mainwindow
        screen when save button is clicked.
        '''
        #Get text values from each element
        lat = eval(self.latEdit.text())
        lon = eval(self.lonEdit.text())
        desc = self.descBox.toPlainText()
        dist = eval(self.distEdit.text())
        bearing = eval(self.bearingEdit.text())
        units = self.units
        
        #check values entered by user are correct
        upperBound = [90, 180, 10000, 360]
        lowerBound = [-90, -180, 0.01, 0]
        fieldVals = [lat, lon, dist, bearing]

        upperCheck = all(field < limit for field, limit in zip(fieldVals, upperBound))
        lowerCheck = all(field >= limit for field, limit in zip(fieldVals, lowerBound))

        if upperCheck and lowerCheck:
            if self.parent():
                self.parent().setLocation(lat, lon, desc, dist, bearing, units)

            self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.close()

class MouseSettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(MouseSettingsWindow, self).__init__(parent)

        self.mc = MouseController()

        #store original settings
        self.origSpeed = self.mc.getSpeed()
        self.origAccel = self.mc.getAcceleration()

        #create variables for updated settings
        self.speedSetting = self.origSpeed
        self.accelSetting = self.origAccel

        self.setFixedSize(300, 150)
        self.setWindowTitle('Mouse Settings')
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing lineedits, unit selector, and label
        hLayout = QHBoxLayout()
        sliderLabel = QLabel('Sensitivity:')

        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(1)
        self.sl.setMaximum(20)
        self.sl.setValue(self.origSpeed)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(5)
        self.sl.valueChanged.connect(lambda: self.mc.setSpeed(self.sl.value()))

        self.checkBox = QCheckBox('Acceleration')
        self.checkBox.setChecked(self.origAccel)
        self.checkBox.stateChanged.connect(lambda: self.mc.setAcceleration(self.checkBox.isChecked()))

        hLayout.addWidget(sliderLabel)
        hLayout.addWidget(self.sl)

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addWidget(self.checkBox)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def save(self):
        '''
        Exit window with updated mouse settings
        '''
        self.close()

    def cancel(self):
        '''
        Set mouse and acceleration back to original settings and close window
        '''
        self.mc.setSpeed(self.origSpeed)
        self.mc.setAcceleration(self.origAccel)
        self.close()

class MapWindow(QDialog):
    def __init__(self, api_key, ref, points):
        super(MapWindow, self).__init__()
        
        self.api = api_key
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

        #Create point string to hold all JS point variables
        point_str = ''

        #Define center point of map and set to reference point
        center = {'lat': self.ref[0], 'lng': self.ref[1]}
        point_str += self.addMarker(center, 'green')

        #Add all traced points to JS point variables
        for p in self.points:
            point = {'lat': p['Latitude'], 'lng': p['Longitude']}
            point_str += self.addMarker(point, 'red')
        
        mapView = QWebEngineView()
        mapView.setHtml(f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simple Map</title>
            <meta name="viewport" content="initial-scale=1.0">
            <meta charset="utf-8">
            <style>
            /* Always set the map height explicitly to define the size of the div
            * element that contains the map. */
            #map {{
                height: 100%;
            }}
            /* Optional: Makes the sample page fill the window. */
            html, body {{
                height: 100%;
                margin: 0;
                padding: 0;
            }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
            var map;
            function initMap() {{
                map = new google.maps.Map(document.getElementById('map'), {{
                center: {center},
                zoom: 10
                }});
                {point_str}
            }}
            </script>
            <script src="https://maps.googleapis.com/maps/api/js?key={self.api}&callback=initMap"
            async defer></script>
        </body>
        </html>
        ''')
 
        layout.addWidget(mapView)
        self.setLayout(layout)

    def addMarker(self, point, color):
        '''
        Add point to map by converting to JS format
        '''
        marker = f'''
        var marker = new google.maps.Marker({{
            icon : 'http://maps.google.com/mapfiles/ms/icons/{color}-dot.png',
            position: {point},
            map: map,
            title: 'Reference Point'
        }});
        '''
        return marker

class APIKeyWindow(QDialog):
    def __init__(self, parent=None):
        super(APIKeyWindow, self).__init__(parent)

        self.setFixedSize(350, 100)
        self.setWindowTitle('Enter API Key')
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        hLayout = QHBoxLayout()
        self.apiKeyEdit = QLineEdit()
        self.apiKeyEdit.setPlaceholderText('Google API Key')
        self.apiKeyEdit.textChanged.connect(self.checkFields)

        self.helpButton = QPushButton('?')
        self.helpButton.setMaximumWidth(25)
        self.helpButton.clicked.connect(lambda: webbrowser.open('https://developers.google.com/maps/documentation/javascript/get-api-key'))

        hLayout.addWidget(self.apiKeyEdit)
        hLayout.addWidget(self.helpButton)

        #horizontal layout containing save and cancel buttons
        h2Layout = QHBoxLayout()
        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.cancel)

        h2Layout.addWidget(self.saveButton)
        h2Layout.addWidget(self.cancelButton)

        mainLayout.addLayout(hLayout)
        mainLayout.addLayout(h2Layout)
    
        self.setLayout(mainLayout)
        self.setModal(True)
        self.show()

    def checkFields(self):
        '''
        Check if all mandatory fields are entered
        '''
        if self.apiKeyEdit.text():
            self.saveButton.setEnabled(True)

    def save(self):
        '''
        Send scale and unit values entered by user back to mouse tracker
        screen when save button is clicked.
        '''
        self.parent().setAPI(self.apiKeyEdit.text())
        self.close()

    def cancel(self):
        '''
        Return to mouse tracker screen if cancel button is clicked
        '''
        self.close()
    

if __name__=='__main__':
    import sys

    app = QApplication(sys.argv)
    window = APIKeyWindow()
    sys.exit(app.exec_())

