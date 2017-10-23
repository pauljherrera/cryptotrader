# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Paúl Herrera
"""

import logging
import json
import sys
import os

from socketclusterclient import Socketcluster

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber
from core.libraries.websocket_thread import ConnectThread
from core.libraries.channels import channels as ch
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
            self.socket.subscribeack(channelName, self.subscribeack)

    def subscribeack(self, channel, error, data):
        if error is '':
            print("Subscribed successfully to channel " + channel)

    def onChannelMessage(self,event, message):
        print(message)
        self.pub.dispatch(event, message)


    def print_message(self, key, error, message):
        print(message)


if __name__ == "__main__":
    # Variables.
    key = "5d69efe677adf65c82ab8fd65477737a"
    secret = "cb83efff6c3b2d75e27db699f2d50349"
    channels=[
        'TRADE-GDAX--BTC--USD',
        'TRADE-PLNX--USDT--BTC',
        'TRADE-BTRX--BTC--USDT',
    ]

    #channels = ch


    # Connecting to websocket.
    ws = CoinigyWebsocket(key, secret, channels=channels, reconnect=True)
    connnectThread = ConnectThread(ws)
    connnectThread.setDaemon(True)
    connnectThread.start()
    x=input()
