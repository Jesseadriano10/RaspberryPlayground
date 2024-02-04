from PyQt5 import QtCore, QtGui, QtWidgets, uic;
import sys;
import os;

# Importing the required classes
class ParkingLotApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(ParkingLotApp, self).__init__()
        uic.loadUi('parking_lot.ui', self)
        
        # Find the widgets using their object names set in Qt Designer
        self.sensorDisplay = self.findChild(QtWidgets.QLabel, 'sensorDisplay')
        self.messageInput = self.findChild(QtWidgets.QLineEdit, 'messageInput')
        self.displayBoard = self.findChild(QtWidgets.QTextEdit, 'displayBoard')
        self.sendMessageButton = self.findChild(QtWidgets.QPushButton, 'sendMessageButton')
        self.warningLightOnButton = self.findChild(QtWidgets.QPushButton, 'warningLightOnButton')
        self.warningLightOffButton = self.findChild(QtWidgets.QPushButton, 'warningLightOffButton')
        
        # Connect signals to slots
        self.sendMessageButton.clicked.connect(self.displayMessage)
        self.warningLightOnButton.clicked.connect(self.turnWarningLightOn)
        self.warningLightOffButton.clicked.connect(self.turnWarningLightOff)
        
        # TODO: Make a method to update sensor display
        # self.updateSensorDisplay()
        
        def displayMessage(self):
            # Get the message from the input field and do something with it
            message = self.messageInput.toMarkdown()
            self.displayBoard.append(message)
            self.messageInput.clear()
            print(message) # For debugging
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ParkingLotApp()
    window.show()
    sys.exit(app.exec_())