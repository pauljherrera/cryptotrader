# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Paúl Herrera
"""

from core import strategies, trader
from core.strategies_gdax import Strategy
from core.coinigy_data_feeder import CoinigyWebsocket
from core.libraries.websocket_thread import ConnectThread
from core.GDAX_data_feeder import GDAXWebSocketClient
from core.libraries.gdax_auth import Authentication

if __name__ == "__main__":
	# User Variables.
    #needs coments
    channels = ["ETH-USD"]
    bars=[5,15,30]
    #minutes
    parameters = {
        'pairs': "ETH-USD",
        'ATR-Period': 14,
        'Bars': bars}


    #Authentication
    API_KEY = ""
    API_SECRET = ""
    API_PASS = ""

    auth = Authentication(API_KEY, API_SECRET, API_PASS).get_dict()

    request = {"type": "subscribe",
            "channels": [{"name": "full", "product_ids": channels }]}

    request.update(auth)
    #comment this for no auth

    ws = GDAXWebSocketClient(request, channels)
    connectThread = ConnectThread(ws)
    connectThread.setDaemon(False)
    # Setting strategy and subscriptions.
    strategy = Strategy(**parameters)
    for c in channels:
    	ws.pub.register(c, strategy)

    # Setting trader and subscriptions.
    #Trader = trader.Trader(key, secret, auth_id=auth_id)
    #strategy.pub.register('signals', trader)

    # Start connection.
    connectThread.start()
