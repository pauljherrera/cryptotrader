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
    API_KEY = "c2c736241299f78327809504d2ffb0e7 "
    API_SECRET = "xzYSvcKvfP8Nx1uS+FxK7yWtoSfJplenN0vv9zGywfQcjTqEfqTmvGWsGixSQHCtkh9JdNoncEU1rEL1MXDWkA=="
    API_PASS = "si3b5hm7609"
    
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
    trader = GDAXTrader(auth=auth)
    strategy.trader = trader

    # Start connection.
    connectThread.start()
