# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Paúl Herrera
"""

import logging
import json
from socketclusterclient import Socketcluster
from .libraries.pub_sub import Publisher, Subscriber
from .libraries.websocket_thread import ConnectThread

from .libraries.channels import channels as ch
# Custom libraries.
# from libraries.common import PubSubPattern

class CoinigyWebsocket():
    """
    Main class. Has all the websocket implementations.
    """

    def __init__(self, key, secret, channels=[], reconnect=True):
        # Disabbling logging.
        logger = logging.getLogger()
        logger.disabled = True
        
        # API credentials.
        self.api_credentials = json.loads('{}')
        self.api_credentials["apiKey"] = key
        self.api_credentials["apiSecret"] = secret
        
        # Socket parameters.
        self.socket = Socketcluster.socket("wss://sc-02.coinigy.com/socketcluster/")
        self.socket.setreconnection(reconnect)

        self.pub = Publisher(channels)
        # Populates the channels dictionary with all the different channels instances as values.
        for c in channels:
            channel = Subscriber(c)
            channel.pub = Publisher(events=['incoming_data'])
            self.pub.register(c, channel)
            self.socket.onchannel(c, self.onChannelMessage)
        
        # Connecting to socket.
        self.socket.setBasicListener(self.onconnect, self.ondisconnect, 
                                     self.onConnectError)
        self.socket.setAuthenticationListener(self.onSetAuthentication, 
                                              self.onAuthentication)
    
    def getChannels(self):
        channels= []
        for subscriber, callback in self.pub.get_subscribers().items():
            channels.append[subscriber]
        return channels

    def unSubscribe(self,event, channel):
        self.socket.unsubscribe(event)
        self.pub.unregister(event,channel)


    def subscribe(self,event, channel):
        self.socket.subscribe(event)
        self.pub.register(event, channel)
        self.socket.onchannel(event, self.onChannelMessage)

    def connect(self):
        self.socket.connect()
    
    def onconnect(self, socket):
        print('Connecting to websocket')     
    
    def ondisconnect(self, socket):
        pass
    
    def onConnectError(self, socket, error):
        logging.info("On connect error got called")
    
    def onSetAuthentication(self, socket, token):
        logging.info("Token received " + token)
        socket.setAuthtoken(token)
    
    def onAuthentication(self, socket, isauthenticated):
        print('Authenticating user')     
        logging.info("Authenticated is " + str(isauthenticated))
        socket.emitack("auth", self.api_credentials, self.ack)
    
    def ack(self, eventname, error, data):
        for channelName,channel in self.pub.get_events().items():
            print("Subscribing to channel: {}".format(channelName)) 
            self.socket.subscribe(channelName)

    def onChannelMessage(self,event, message):
        self.pub.dispatch(event, message)

        
    def print_message(self, key, error, message):
        print(message)
    
    
if __name__ == "__main__":
    # Variables.
    key = "67a4cf6b2800fb2a177693a61bff2b1a"
    secret = "8f756b95e898a8e42bbed7b0abb858d5"
    channels=[
        'TRADE-BTCE--BTC--USD', 
        'TRADE-OK--BTC--CNY',
        'TRADE-BITF--BTC--USD',
        'TRADE-GDAX--BTC--USD',
        'TRADE-PLNX--USDT--BTC',
        'TRADE-BTRX--BTC--USDT',
        'TRADE-HUOB--BTC--CNY',
    ]

    channels = ch
    
    # pub = Publisher(channels)
    # channel1 = Subscriber('channel1')
    # channel2 = Subscriber('channel2')
    # channel3 = Subscriber('channel3')

    # pub.register("TRADE-BTCE--BTC--USD", channel1)
    # pub.register("TRADE-BTRX--BTC--USDT", channel2)
    # pub.register("TRADE-BTCE--BTC--USD", channel3)
    # pub.register("TRADE-BTRX--BTC--USDT", channel3)

    # pub.dispatch("TRADE-BTCE--BTC--USD", "It's USD!")
    # pub.dispatch("TRADE-BTRX--BTC--USDT", "Its USDT")
    # Connecting to websocket.
    ws = CoinigyWebsocket(key, secret, channels=channels, reconnect=False)
    connnectThread = ConnectThread(ws)
    connnectThread.setDaemon(True)
    connnectThread.start()
    x=input("Press any key to exit")
