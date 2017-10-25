# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 20:54:30 2017

@author: Paúl Herrera
"""

from core import strategies, trader
from core.coinigy_data_feeder import CoinigyWebsocket
from core.libraries.websocket_thread import ConnectThread


if __name__ == "__main__":
	# User Variables.
    key = "5d69efe677adf65c82ab8fd65477737a"
    secret = "cb83efff6c3b2d75e27db699f2d50349"
    timeframe = 1 # In minutes.
    auth_id = 1111
    
    # Settings.
    channels=[
        'TRADE-PLNX--USDT--BTC',
    ]
    #needs ui
    value = {
        "exchange_code":"PLNX",
        "exchange_market":"BTC/USDT",
        "type":"history"}
    header = {
        "Content-Type":"application/json",
        "X-API-KEY":key,
        "X-API-SECRET":secret}
    data = {
            'values':value,
            'headers':header,
            'timef':str(timeframe) + "T",
            'EventType' : 'SELL'}
            # + "S" for seconds, + "T" for minutes
            # EventType values = SELL or BUY

    # Initializing websocket.
    ws = CoinigyWebsocket(key, secret, channels=channels, reconnect=True)
    connnectThread = ConnectThread(ws)
    connnectThread.setDaemon(False)

    # Setting strategy and subscriptions.
    strategy = strategies.MACrossover(5, 20, 10, **data)
    for c in channels:
    	ws.pub.register(c, strategy)

    # Setting trader and subscriptions.
    trader = trader.Trader(key, secret, auth_id=auth_id)
    strategy.pub.register('signals', trader)

    # Start connection.
    connnectThread.start()
