#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Avanti Financial Services
"""

from core.strategies_gdax import Strategy
from core.libraries.websocket_thread import ConnectThread
from core.GDAX_data_feeder import GDAXWebSocketClient
from core.libraries.gdax_auth import Authentication
from core.trader import GDAXTrader


class CustomStrategy(Strategy):
    def on_tick(self):
        pass

    def on_minute_bar(self):
        print('\nNew minute bar')
        #could be 5, 10, 15... N minutes
        print(self.get_timeframe(5))
        #print(self.trader.get_accounts())

    def on_bar(self):

        """
        Main methods you can use.
        self.vstop
        self.get_timeframe()
        self.trader.place_order()
        self.trader.close_last_order()
        """


if __name__ == "__main__":
	# User Variables.
    API_KEY = 'c2c736241299f78327809504d2ffb0e7'
    API_PASS = 'si3b5hm7609'
    API_SECRET = 'xzYSvcKvfP8Nx1uS+FxK7yWtoSfJplenN0vv9zGywfQcjTqEfqTmvGWsGixSQHCtkh9JdNoncEU1rEL1MXDWkA=='

    access_token =  "1df9662461b596ca098ac8b08cbdc5c328cc0bf1beca81cf2659f3a51cebf00e"
    refresh_token = "40e687e0fe1dd3e0731187c44c5162dc6c157e4e4c050ef8031b1d21ad7acd06"

    product = "BTC-USD"
    ATR_period = 14
    timeframe = 60
    VStop_multiplier = 2
    data_days = 2

    #Authentication
    auth = Authentication(API_KEY, API_SECRET, API_PASS)
    request = {"type": "subscribe",
               "channels": [{"name": "full", "product_ids": [product] }]}

    request.update(auth.get_dict())     #comment this for no auth

    # Setting data feeder.
    ws = GDAXWebSocketClient(request, [product])
    connectThread = ConnectThread(ws)
    connectThread.setDaemon(False)

    # Setting strategy and subscribing to data channels.
    parameters = {
        'pairs': product,
        'ATR-Period': ATR_period,
        'vstop timeframe': timeframe,
        'vstop multiplier': VStop_multiplier,
        'data days': data_days}

    strategy = CustomStrategy(**parameters)
    for c in [product]:
    	ws.pub.register(c, strategy)

    # Setting trader.
    trader = GDAXTrader(auth=auth, access_token=access_token, refresh_token=refresh_token)
    strategy.trader = trader

    #Shows data of every wallet
    data_acc = trader.get_accounts()['data']
    [print (item['balance'], item['name']) for item in data_acc]


    # Start connection.
    connectThread.start()
