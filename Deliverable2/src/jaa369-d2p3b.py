import paho.mqtt.client as mqtt
import time

broker = "broker.hivemq.com"
client = mqtt.Client("jaa369_publish")
client.connect(broker)

run = True
listOfCommands = ["ledOn", "ledRed", "ledGreen", "ledBlue", "readSen"]

while(run):
    print("<----------------------------------------->")
    print("Choose the following commands to execute:")
    print("   1.) ledOn")
    print("   2.) ledRed")
    print("   3.) ledGreen")
    print("   4.) ledBlue")
    print("   5.) readSen")
    print("   6.) quit")
    print()

    msg = input("Enter the command you want to execute: ")

    print()
    if (msg == "quit"):
        run = False
    elif (msg in listOfCommands):
        client.publish("jaa369_read", msg)
        print("Executing Command: ", msg)
    else:
        print("Command is not unknown...")
    print()
    time.sleep(3)



