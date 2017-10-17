# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Paúl Herrera
"""

from core import strategies, trader
from core.coinigy_data_feeder import CoinigyWebsocket
from core.libraries.websocket_thread import ConnectThread


if __name__ == "__main__":
	# Variables.
    key = "67a4cf6b2800fb2a177693a61bff2b1a"
    secret = "8f756b95e898a8e42bbed7b0abb858d5"
    auth_id = 1111
    channels=[
        'TRADE-PLNX--USDT--BTC',
    ]

    # Initializing websocket.
    ws = CoinigyWebsocket(key, secret, channels=channels, reconnect=False)
    connnectThread = ConnectThread(ws)
    connnectThread.setDaemon(True)

    # Setting strategy and subscriptions.
    strategy = strategies.MACrossover(5, 20, 10)
    for c in channels:
    	ws.pub.register(c, strategy)
        
    # Setting trader and subscriptions.
    trader = trader.Trader(key, secret, auth_id=auth_id)
    strategy.pub.register('signals', trader)

    # Start connection.
    connnectThread.start()
