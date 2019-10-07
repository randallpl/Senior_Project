from PyQt5.QtWidgets import *

class Button(QPushButton):
    def __init__(self, name=None):
        super(Button, self).__init__()
        self.setMouseTracking(True)
        self.setText(name)
        
    def enterEvent(self, event):
        if self.isEnabled():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(2)
            shadow.setOffset(3, 3)
            self.setGraphicsEffect(shadow)

    def leaveEvent(self, event):
        self.setGraphicsEffect(None)

class LineEdit(QLineEdit):
    def __init__(self, name=None):
        super(LineEdit, self).__init__()
        self.setText(name)
    def focusInEvent(self, event):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(2)
        shadow.setOffset(3, 3)
        self.setGraphicsEffect(shadow)

    def focusOutEvent(self, event):
        self.setGraphicsEffect(None)
