# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Paúl Herrera
"""

import logging
import json
from socketclusterclient import Socketcluster

# Custom libraries.
from libraries.common import PubSubPattern
from libraries import channels as ch

class Channel(PubSubPattern):
    counter = 0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

    def on_channel_message(self, key, message):
        self.publish(message)
        print(message)
        self.__class__.counter += 1
        print(self.__class__.counter)


class CoinigyWebsocket():
    def __init__(self, key, secret, channels=[], reconnect=True):
        # Disabbling logging.
#        logger = logging.getLogger()
#        logger.disabled = True
        
        # API credentials.
        self.api_credentials = json.loads('{}')
        self.api_credentials["apiKey"] = key
        self.api_credentials["apiSecret"] = secret
        
        # Socket parameters.
        self.socket = Socketcluster.socket("wss://sc-02.coinigy.com/socketcluster/")
        self.socket.setreconnection(reconnect)
        self.channels = {}
        
        # Composing different channels.
        for c in channels:
            self.channels[c] = Channel()
            self.socket.onchannel(c, self.channels[c].on_channel_message)
        
        # Connecting to socket.
        self.socket.setBasicListener(self.onconnect, self.ondisconnect, 
                                     self.onConnectError)
        self.socket.setAuthenticationListener(self.onSetAuthentication, 
                                              self.onAuthentication)
        
    def connect(self):
        self.socket.connect()
    
    def onconnect(self, socket):
        print('Connecting to websocket')     
    
    def ondisconnect(self, socket):
        pass
    
    def onConnectError(self, socket, error):
        logging.info("On connect error got called")
        self.socket.disconnect()
    
    def onSetAuthentication(self, socket, token):
        logging.info("Token received " + token)
        socket.setAuthtoken(token)
        socket.emitack("auth", self.api_credentials, self.ack)
    
    def onAuthentication(self, socket, isauthenticated):
        print('Authenticating user')     
        logging.info("Authenticated is " + str(isauthenticated))
    
    def ack(self, eventname, error, data):
        print('error', error)
        for c in self.channels.keys():
            print("Subscribing to channel: {}".format(c)) 
            self.socket.subscribeack(c, self.subscribe_callback)
    
    def subscribe_callback(self, channel, error, object_):
        if error is '':
            print("Subscribed successfully to channel " + channel)
        else:
            print("Error: " + error)

    def print_message(self, key, error, message):
        print(message)
    
    
if __name__ == "__main__":
    # Variables.
    key = "0ac92a25bd0e3744713ec4d22dda3bd2"
    secret = "9499f4c7b0b6b424d382872b70659f9a"
    channels=[
        'TRADE-GDAX--BTC--USD',
    ]
    
    # Connecting to websocket.
    ws = CoinigyWebsocket(key, secret, channels=channels, reconnect=True)
    ws.connect()
    
#    
#    ws = CoinigyWebsocket(key, secret, channels=channels, reconnect=False)
#    ws.connect()
    