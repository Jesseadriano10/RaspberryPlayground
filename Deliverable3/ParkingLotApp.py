from PyQt5 import QtCore, QtGui, QtWidgets, uic;
import sys;
import paho.mqtt.client as mqtt;
import json;

"""
DisplayBoardContainer class
This class is used to store the messages and timestamps for the display board
"""
class DisplayBoardContainer:
    def __init__(self):
        self.maxMessages = 10
        self.board = {"messages": [], "timestamp": []}
    
    def addMessage(self, message: str):
        self.board["messages"].append(message)
        self.board["timestamp"].append(QtCore.QDateTime.currentDateTime().toString())
        if len(self.board["messages"]) > self.maxMessages:
            self.board["messages"].pop(0)
            self.board["timestamp"].pop(0)
    def getMessages(self):
        return self.board["messages"]
    def getTimestamps(self):
        return self.board["timestamp"]
    

# Importing the required classes
class ParkingLotApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(ParkingLotApp, self).__init__()
        uic.loadUi('parking_lot.ui', self)
        self.setMinimumSize(800, 600)
        self.resize(1920, 1080)
        
        # Find the widgets using their object names set in Qt Designer
        self.sensorDisplay = self.findChild(QtWidgets.QLabel, 'sensorDisplay')
        self.messageInput = self.findChild(QtWidgets.QLineEdit, 'messageInput')
        self.displayBoard = self.findChild(QtWidgets.QTextEdit, 'displayBoard')
        self.sendMessageButton = self.findChild(QtWidgets.QPushButton, 'sendMessageButton')
        self.warningLightOnButton = self.findChild(QtWidgets.QPushButton, 'warningLightOnButton')
        self.warningLightOffButton = self.findChild(QtWidgets.QPushButton, 'warningLightOffButton')
        
        # Connect signals to slots
        self.sendMessageButton.clicked.connect(self.sendMessage)
        self.warningLightOnButton.clicked.connect(self.turnWarningLightOn)
        self.warningLightOffButton.clicked.connect(self.turnWarningLightOff)

        # data variables
        self.occupiedSlots = 0
        self.parkingLot = [0,0,0,0,0]
        self.sensorValue = 0
        self.isFull = False
        
        
        self.setupMQTT()
        self.displayBoardContainer = DisplayBoardContainer()

    def setupMQTT(self):
        self.broker = "test.mosquitto.org"
        self.client = mqtt.Client("jaa369_d3_qtApp")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, keepalive=60)
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self.client.subscribe("jaa369/parking/system/")
        self.client.subscribe("jaa369/parking/displayBoard/")
                
    def updateDisplayBoard(self):
        messages = self.displayBoardContainer.getMessages()
        timestamps = self.displayBoardContainer.getTimestamps()
        self.displayBoard.clear()
        for message, timestamp in zip(messages, timestamps):
            self.displayBoard.append(f"{message} - {timestamp}, \n\tSpots filled: {self.occupiedSlots}, isFull? {self.isFull}, \n\t Lot = {self.parkingLot}")
            
    def on_message(self, client, userdata, msg):
        # Parse the json payload and do something with it
        payload = json.loads(msg.payload)
        if msg.topic == "jaa369/parking/displayBoard/":
            self.displayBoardContainer.addMessage(payload["message"])
            self.updateDisplayBoard()
        elif msg.topic == "jaa369/parking/system/": 
            """
            Get the payload containing
            payload = {
            "sensorValue": self.dataSensor.read(),
            "parkingLotData": self.parkingSpot.spots,
            "occupiedSlots": self.parkingSpot.occupied,
            "isFull": self.parkingSpot.isFull()
            }   
            """
            self.sensorDisplay.setText(f"Sensor Value: {payload['sensorValue']}")
            self.updateParkingIndicators(payload["parkingLotData"])
            self.updateOccupiedSlots(payload["occupiedSlots"], payload["isFull"])
    def updateParkingIndicators(self, parkingLotData):
        # Update parking spot indicators based on ParkingLotData
        for i, occupied in enumerate(parkingLotData):
            indicator = self.findChild(QtWidgets.QPushButton, f"parkingIndicator{i+1}")
            if indicator:
                indicator.setProperty('status', 'occupied' if occupied else 'available')
                indicator.setStyle(indicator.style()) # Refresh style

    def updateOccupiedSlots(self, occupiedSlots, isFull):
        self.occupiedSlots = occupiedSlots
        self.isFull = isFull
    
    def turnWarningLightOn(self):
        # Send MQTT message to turn on the warning light: WARN ON
        self.client.publish("parking/system/", json.dumps({"command": "WARN ON"}))
    
    def turnWarningLightOff(self):
        # Send MQTT message to turn off the warning light: WARN OFF
        self.client.publish("parking/system/", json.dumps({"command": "WARN OFF"}))
    
        
            
        
    def sendMessage(self):
        message = self.messageInput.text()
        self.client.publish("jaa369/parking/displayBoard/", json.dumps({"message": message, "timestamp": QtCore.QDateTime.currentDateTime().toString()}))
        self.messageInput.clear()
            
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ParkingLotApp()
    window.setWindowTitle("Parking Lot App")
    window.show()
    sys.exit(app.exec_())