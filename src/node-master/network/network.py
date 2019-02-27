import paho.mqtt.client as mqtt
import time
import os
import sys

"""
    This module handles communication with the central server.
    Each node starts a connection with the server and then communicates with it over mqtt
    each client saves an ID for easy lookup in the webserver (since mqtt id's change with each connection)
    This module relays the given information between the server and the atmega
"""

class File:
    """
        The File class handles file input and output
        Never forget to call the cleanup method.
        This handles the closing of the file.
        Never use this class if multiple instances of the same file are used since whe never close it
        during its lifespan
    """
    # filename is located in the directory of the module
    # this should be launched from launch.py
    def __init__(self, file):
        if __name__ == '__main__':
            self.filename = os.getcwd()+ '/' + __file__.replace(os.path.basename(__file__), '') + file
        else:
            self.filename =  __file__.replace(os.path.basename(__file__), '') + file

    def read(self):
        self.file = open(self.filename, "r+")
        value = self.file.read()
        self.cleanup()
        return value

    def write(self, value):
        self.file = open(self.filename, "w+")
        self.file.write(value)
        self.cleanup()

    def cleanup(self):
        self.file.close()

class ID:
    """
        The ID class figures out if we already have an ID otherwise we get assigned one
    """
    def __init__(self, filename, client):
        self.file = File(filename)
        self.client = client
        self.check()

    def check(self):
        self.id = self.file.read()
        if self.id  == '':
            print('No id provided, requesting id')
            self.request()
        else:
            print('ID from file: ' + self.id)
    
    def request(self):
        self.client.subscribe("id")

    def save(self):
        self.file.write(self.id)


class MQTT:
    """
        The mqtt class is the main class of this module.
        It handles the connection between the client and server.

        Important notes

        When you aren't sending information using MQTT.send()
        use MQTT.start() this will listen for incomming events
        And don't forget to call MQTT.end() before sending information
        When you don't need MQTT anymore use disconnect this will end the client connection
    """
    def __init__(self, host, port):
        self.client = mqtt.Client()
        self.client.connect(host, port, 60)
        self.client.on_message = self.on_message
        self.id = ID('id.txt', self.client)



    def send(self, item):
        self.client.publish("node", item)

    def disconnect(self):
        self.client.disconnect()

    def start(self):
        self.client.loop_start()

    def end(self):
        self.client.loop_stop()
    
    # The callback for when a PUBLISH message is received from the server.
    # this should parse the information and propagate it
    # TODO : send information to the atmega if nececery 
    def on_message(self, client, userdata, msg):
        if msg.topic == 'id':
            self.id.id = str(msg.payload.decode("utf-8"))
            print("Received id: " + self.id.id)
            self.id.save()

# This function should send information to the server 
def eventHandler(server):
    while True:
        server.send("Hello")
        server.start()
        time.sleep(1)
        server.end()

def start(name):
    server = MQTT("localhost", 1884)

    eventHandler(server)

    server.disconnect()

if __name__ == '__main__':
    start("Hello")