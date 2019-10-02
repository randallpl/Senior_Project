import sys
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QGridLayout, QLabel, QApplication, QDialog
from PyQt5.QtGui import QCursor, QFont
from geopy.distance import geodesic
from collections import namedtuple
import math

from MouseController import MouseController

#Dependencies
#PyQt5: conda install -c anaconda pyqt 
#geopy: conda install -c conda-forge geopy

#Create namedtuple for readability to store point data
Point = namedtuple('Point', 'x y')

#Tracker class to handle mouse movement for locating point and setting scale
#Two modes: scale and location
class Tracker(QDialog):
    
    def __init__(self, mode, parent=None, hidden=True, ref=None, scale=None, units=None):
        super(Tracker, self).__init__(parent)

        if mode not in ['scale', 'location']:
            raise ValueError(mode)

        self.ref = ref
        self.mode = mode
        self.hidden = hidden
        self.scale = scale
        self.units = units

        self.mouseController = MouseController()
        self.origMouseSpeed = self.mouseController.getSpeed()
        self.origAcceleration = self.mouseController.getAcceleration()

        self.zeroVariables()
           
        self.cursor = QCursor()
        self.initUI()
        
        
    def initUI(self):
        '''
        Setup GUI elements of mouse tracker screen.
        '''      
        grid = QGridLayout()

        #Increase font size and set window dimensions
        font = QFont()
        font.setPointSize(14)
        self.label = QLabel()
        self.label.setFont(font)          
        grid.addWidget(self.label, 0, 0, Qt.AlignTop)
        self.setLayout(grid)
        self.updateLabel(0, 0)

        self.setWindowTitle(self.mode)
        self.setModal(True)
        self.showFullScreen()
        
    def getCenter(self):
        '''
        Find the center point of the window by adding half the distance of
        the height and width to the absolute x, y location of the window.
        '''
        #Reference to geometry of screen and cursor
        geo = self.geometry()
        cur = self.cursor
        
        #Get x, y coords of the screen, left upper corner
        x_pos = geo.x()
        y_pos = geo.y()
            
        #Get width and height of screen distances from left upper corner
        width = geo.width()
        height = geo.height()
            
        #Find center point of screen
        x_center = x_pos + (width//2)
        y_center = y_pos + (height//2)
        
        return Point(x_center, y_center)
    
    def getCursorPos(self):
        '''
        Return the current position of the cursor relative to the upper
        left corner of the window.
        '''
        x = self.cursor.pos().x()
        y = self.cursor.pos().y()
        
        return Point(x, y)

    def getDX(self):
        '''
        Calculate distance from center in x direction
        '''
        center = self.getCenter()
        curPos = self.getCursorPos()

        return curPos.x - center.x

    def getDY(self):
        '''
        Calculate distance from center in y direction
        '''
        center = self.getCenter()
        curPos = self.getCursorPos()

        #reverse y for inverted y-axis
        return center.y - curPos.y

    def getDistance(self, dx, dy):
        '''
        Calculate straight line distance from point a to b using net distance
        in x and y direction

        Args:
            dx (float): total distance in pixels traveled in x direction
            dy (float): total distance in pixels traveled in y direction
        
        Returns:
            Total distance
        '''
        try:
            return round(math.sqrt(dx**2 + dy**2), 4)
        except:
            return 0

    def getBearing(self, dx, dy):
        '''
        Calculate the bearing of the mouse movement

        Args:
            dx (float): total distance in pixels traveled in x direction
            dy (float): total distance in pixels traveled in y direction

        Returns:
            bearing (float): bearing in degrees
        '''
        try:
            bearing = math.degrees(math.atan2(dy, dx))

        except Exception as e:
            print('Error: getBearing:', e.__class__.__name__)
            #do something to handle error
            return 1

        else:
            #shift bearing so 0 degrees is now grid north
            bearing = (360 + (90 - bearing)) % 360

            return round(bearing, 4)
    
    def convert(self, dist, scale):
        '''
        Convert distance in pixels to unit of measurement (km, mi, etc...)

        Args:
            dist (float): Euclidean distances from start to end point
            scale (int): scale to convert pixels to proper units

        Returns:
            convDist (float): converted mouse movement in correct unit of measurement
        '''
        try:
            convDist = dist / scale

        except Exception as e:
            print('Error: convert:', e.__class__.__name__)
            #do something to handle error
            return 1

        else:
            return round(convDist, 4)
    
    def newLocation(self, ref, dist, bearing):
        '''
        Computes the latitude and longitude using mouse movements distance
        and bearing from a reference point

        Args:
            ref (tuple): latitude and longitude of the reference point
            dist (float): converted euclidean distance of mouse movement
            bearing (float): bearing in degrees of mouse movement

        Returns:
            coords.latitude (float): latitude of new location
            coords.longitude(float): longitude of new location
        '''
        #kilometers
        if self.units == 'km':
            coords = geodesic(kilometers=dist).destination(ref, bearing)
        #miles    
        elif self.units == 'mi':
            coords = geodesic(miles=dist).destination(ref, bearing)
        #meters        
        elif self.units == 'm':
            coords = geodesic(meters=dist).destination(ref, bearing)
        #feet    
        elif self.units == 'ft':
            coords = geodesic(feet=dist).destination(ref, bearing)
    
        return Point(round(coords.latitude, 5), round(coords.longitude, 5))
    
    def zeroVariables(self):
        '''
        Zero out all instance variables after mouse has been released.
        '''
        self.dx = 0
        self.dy = 0
        self.dist = 0
        self.dist_px = 0
        self.bearing = 0
        self.newLoc = Point(0, 0)

    def updateLabel(self, dx_px, dy_px):
        '''
        Constantly update data on window label
        '''
        results = f'\n\tdx_px: {self.dx + dx_px}\n'
        results += f'\tdy_px: {self.dy + dy_px}\n'
        results += f'\tDistance_px: {self.dist_px}\n'

        if self.mode == 'location':
            results += f'\n\tReference: {self.ref}\n'
            results += f'\tBearing: {self.bearing}\n'
            results += f'\tDistance_{self.units}: {self.dist}\n'
            results += f'\tNew Location: {self.newLoc.x, self.newLoc.y}'

        self.label.setText(results)

    def update(self):
        '''
        Tracks current x and y distance and updates label
        '''
        geo = self.geometry()
        cur = self.cursor
        center = self.getCenter()
        
        #Get current x, y, and straight line distance from center
        dx_px = self.getDX()
        dy_px = self.getDY()
        self.dist_px = self.getDistance(self.dx + dx_px, self.dy + dy_px)

        if self.mode == 'location':
            self.bearing = self.getBearing(self.dx + dx_px, self.dy + dy_px)
            self.dist = self.convert(self.dist_px, self.scale)
            self.newLoc = self.newLocation(self.ref, self.dist, self.bearing)
            
        #Check if cursor is within window boundaries
        #Only update dx, dy instance variables when border has been reached
        curLoc = {cur.pos().x(), cur.pos().y()}
        boundaries = {0, geo.width()-1, geo.height()-1}

        if curLoc.intersection(boundaries):
            self.dx += dx_px
            self.dy += dy_px
            cur.setPos(center.x, center.y)

        self.updateLabel(dx_px, dy_px)
        
    def mousePressEvent(self, e):
        '''
        When mouse is pressed cursor will be repositioned at the center
        of the window and tracking will start.
        '''
        center = self.getCenter()
        self.cursor.setPos(center.x, center.y)

        #Max out mouse pointer speed
        #self.mouseController.setSpeed(20)

        #turn mouse acceleration off
        self.mouseController.setAcceleration(False)
                
        if self.hidden:
            QApplication.setOverrideCursor(Qt.CrossCursor)
        else:
            QApplication.setOverrideCursor(Qt.CrossCursor)
    
    def mouseReleaseEvent(self, e):
        '''
        When mouse is released cursor type will be reset or shown
        again if hidden.
        '''
        #restore cursor type and zero out variables
        QApplication.restoreOverrideCursor()

        #Reset mouse speed to original setting
        self.mouseController.setSpeed(self.origMouseSpeed)

        #Reset mouse acceleration
        self.mouseController.setAcceleration(self.origAcceleration)

        #Call function to launch windown depending on scale or location mode
        if self.parent():
            if self.mode == 'scale':
                self.parent().confirmScale(self.dist_px)
            else:
                self.parent().confirmLocation(self.newLoc.x, self.newLoc.y, self.dist, self.bearing, self.units)

        self.zeroVariables()
        
    def mouseMoveEvent(self, e):
        '''
        When mouse button is pressed and moving all fields will be actively updated.
        The current distance x, y, and total from the center will be added to the 
        overall distance to track current bearing, distance, and current location.
        '''
        self.update()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = Tracker(
        'location', 
        ref=(38.0, -120.0), 
        scale=131.5, 
        units='km'
    )
    sys.exit(app.exec_())