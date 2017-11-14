import logging
import json
import sys
import os
import time
import websocket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber
from core.libraries.websocket_thread import ConnectThread
from core.libraries.channels import channels as ch

class GDAXWebSocketClient():

    def __init__(self,data):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://ws-feed.gdax.com",
                                        on_message=self.on_message,
                                        on_open=self.on_open)
        self.sub = json.dumps(data)
        self.ws.op_open = self.on_open
        self.ws.run_forever()

    def on_message(self, ws, message):
        types = json.loads(message)['type']
        if types == "received" or types == "open":
            print(message)

    def on_open(self, ws):
        ws.send(self.sub)


def main():
    pairs=["ETH-USD","BTC-USD"]

    request={"type": "subscribe", "channels": [{ "name": "full",
            "product_ids": pairs }] }

    GDAXWebSocketClient(request)

if __name__=="__main__":
    main()
