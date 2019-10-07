from PyQt5.QtWidgets import *

class Button(QPushButton):
    def __init__(self, name=None):
        super(Button, self).__init__()
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(3)
        shadow.setOffset(3, 3)
        self.setText(name)
        self.setGraphicsEffect(shadow)
        self.setStyleSheet(open('./Resources/stylesheet.css').read())