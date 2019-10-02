from Map_Reader.Windows import LocationWindow
from PyQt5 import QtCore
import pytest

@pytest.fixture
def window():
    window = LocationWindow(38.12345, -121.12345, 100, 95, 'km')
    return window

def test_1(qtbot, window):
    '''
    Test if all field are populated and save button is enabled by default
    '''
    qtbot.addWidget(window)

    assert window.latEdit.text() == '38.12345'
    assert window.lonEdit.text() == '-121.12345'
    assert window.distEdit.text() == '100'
    assert window.bearingEdit.text() == '95'
    assert window.descBox.toPlainText() == ''
    assert window.saveButton.isEnabled() == True

def test_2(qtbot, window):
    '''
    Test lat, lon values below -90, -180 can't be saved
    '''

    window.latEdit.setText(None)
    window.lonEdit.setText(None)

    qtbot.keyClicks(window.latEdit, '-91.343')
    qtbot.keyClicks(window.lonEdit, '-180.234')
    qtbot.mouseClick(window.saveButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == True

def test_3(qtbot, window):
    '''
    Test lat, lon values above 90, 180 can't be saved
    '''

    window.latEdit.setText(None)
    window.lonEdit.setText(None)

    qtbot.keyClicks(window.latEdit, '91.343')
    qtbot.keyClicks(window.lonEdit, '180.234')
    qtbot.mouseClick(window.saveButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == True

def test_4(qtbot, window):
    '''
    Test lat, lon fields are limited to 5 decimals
    '''

    window.latEdit.setText(None)
    window.lonEdit.setText(None)

    qtbot.keyClicks(window.latEdit, '70.1234567')
    qtbot.keyClicks(window.lonEdit, '112.1234567')

    assert window.latEdit.text() == '70.12345'
    assert window.lonEdit.text() == '112.12345'

def test_5(qtbot, window):
    '''
    Test if save is disabled when lat data is not entered
    '''
    window.latEdit.setText(None)

    assert window.saveButton.isEnabled() == False

def test_6(qtbot, window):
    '''
    Test if save is disabled when lon data is not entered
    '''
    window.lonEdit.setText(None)

    assert window.saveButton.isEnabled() == False

def test_7(qtbot, window):
    '''
    Test if save is disabled when distance data is not entered
    '''
    window.distEdit.setText(None)

    assert window.saveButton.isEnabled() == False

def test_8(qtbot, window):
    '''
    Test if save is disabled when bearing data is not entered
    '''
    window.bearingEdit.setText(None)

    assert window.saveButton.isEnabled() == False

def test_9(qtbot, window):
    '''
    Test if save is enabled if description data is not entered
    '''
    window.descBox.setText(None)

    assert window.saveButton.isEnabled() == True

def test_10(qtbot, window):
    '''
    Test if bearing value below 0 can't be entered
    '''
    window.bearingEdit.setText(None)

    qtbot.keyClicks(window.bearingEdit, '-12.234')

    assert window.bearingEdit.text() == '12.234'

def test_11(qtbot, window):
    '''
    Test if bearing value over 360 can't be saved
    '''
    window.bearingEdit.setText(None)

    qtbot.keyClicks(window.bearingEdit, '361.123')
    qtbot.mouseClick(window.saveButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == True

def test_12(qtbot, window):
    '''
    Test if distance value below 0 can't be entered
    '''
    window.distEdit.setText(None)

    qtbot.keyClicks(window.distEdit, '-1')

    assert window.distEdit.text() == '1'

def test_13(qtbot, window):
    '''
    Test that 0 distance values can't be saved
    '''
    window.distEdit.setText(None)

    qtbot.keyClicks(window.distEdit, '0')
    qtbot.mouseClick(window.saveButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == True


def test_14(qtbot, window):
    '''
    Test data is saved and window is closed when all fields are entered correctly
    '''
    window.latEdit.setText(None)
    window.lonEdit.setText(None)
    window.distEdit.setText(None)
    window.bearingEdit.setText(None)
    window.descBox.setText(None)

    qtbot.keyClicks(window.latEdit, '31.12345')
    qtbot.keyClicks(window.lonEdit,'-121.12345')
    qtbot.keyClicks(window.distEdit, '1000')
    qtbot.keyClicks(window.bearingEdit, '30.3')
    qtbot.keyClicks(window.descBox, 'Test description')
    qtbot.mouseClick(window.saveButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == False

def test_15(qtbot, window):
    '''
    Test that window is closed when cancel is pressed
    '''
    qtbot.mouseClick(window.cancelButton, QtCore.Qt.LeftButton)

    assert window.isActiveWindow() == False  