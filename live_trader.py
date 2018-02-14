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
        """
        self.get_timeframe(5)

        could be 5, 10, 15... N minutes
        returns a dataframe with the timeframe specified

        self.trader.list_accounts()

        returns the account balance dict
		"""
        print('{}: o={}, h={}, l={}, c={}, v={}'.format(
            self.main_df.index[-1],
            self.main_df['open'][-1],
            self.main_df['high'][-1],
            self.main_df['low'][-1],
            self.main_df['close'][-1],
            self.main_df['volume'][-1]))

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
    API_KEY = ''
    API_PASS = ''
    API_SECRET = ''

    product = "BTC-USD"
    ATR_period = 14
    timeframe = 5
    VStop_multiplier = 3
    data_days = 1

    # Authentication
    auth = Authentication(API_KEY, API_SECRET, API_PASS)
    request = {"type": "subscribe",
               "channels": [{"name": "full", "product_ids": [product]}]}

    request.update(auth.get_dict())  # comment this for no auth

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

    # Shows data of every wallet
    # print(trader.list_accounts())

    # Start connection.
    connectThread.start()
