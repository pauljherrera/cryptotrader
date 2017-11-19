import logging
import json
import sys
import os
import time , hmac, hashlib, base64
from websocket import create_connection
from requests.auth import AuthBase
import requests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber
from core.libraries.websocket_thread import ConnectThread
from core.libraries.channels import channels as ch
from core.libraries.gdax_auth import Authentication


class GDAXWebSocketClient():

    def __init__(self,data,channels=[]):
        self.url = "wss://ws-feed.gdax.com"

        self.params = json.dumps(data)
        self.pub = Publisher(channels)
        self.stop = False

        for c in channels:
            channel = Subscriber(c)
            channel.pub = Publisher(events=['incoming_data'])
            self.pub.register(c, channel)

    def on_message(self, message):
        if message['type'] == "match":
            self.pub.dispatch(message['product_id'], message)

    def on_open(self):
        print("--Subscribed--")

    def on_error(self, err):
        try:
            self.connect()
        except:
            self.stop = True
            print('{}'.format(err))

    def connect(self):
        self.on_open()
        self.ws = create_connection(self.url)
        self.ws.send(self.params)
        self.listen()

    def listen(self):
        while not self.stop:
            try:
                if int(time.time()%30) == 0:
                        self.ws.ping("alive")

                msg = json.loads(self.ws.recv())
                self.on_message(msg)
            except ValueError as e:
                self.on_error(e)
            except Exception as e:
                self.on_error(e)

def main():
    pairs=["ETH-USD","BTC-USD"]

    API_KEY = ""
    API_SECRET = ""
    API_PASS = ""

    auth=Authentication(API_KEY, API_SECRET, API_PASS)
    request = {"type": "subscribe",
            "channels": [{"name": "full", "product_ids": pairs }]}
    res = requests.get('https://api.gdax.com/'+ 'accounts', auth=auth)
    #test page example
    print(res.json())


    ws=GDAXWebSocketClient(request,pairs)
    ws.connect()
if __name__=="__main__":
    main()
