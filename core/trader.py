# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 09:36:39 2017

@author: paulj
"""

import requests
import json
import threading

from .libraries.pub_sub import Publisher, Subscriber

class Trader(Subscriber):
    """
    Abstract Base Class for trader.
    """
    def __init__(self, key, secret, auth_id, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.pub = Publisher(events=['trades'])
        self.headers = {'Content-Type': 'application/json',
                        'X-API-KEY': key,
                        'X-API-SECRET': secret}
        self.values = {"auth_id": auth_id,  # exchange accounts
                       "exch_id": 13,  # Poloniex id
                       "mkt_id": 1627,  # BTC/USDT id
                       "order_type_id": 1, # 1 for buy, 2 for sell.
                       "price_type_id": 6, # 3 for limit, 6 for stop (limit)
                       "limit_price": 0,
                       "order_quantity": 0.01}     
        
    def trade(self, signal):
        """
        Receives a dictionary.
        """
        self.values['limit_price'] = signal['price']
        
        if signal['type'] == 'BUY':
            self.values['order_type_id'] = 1
        elif signal['type'] == 'SELL':
            self.values['order_type_id'] = 2
        
        print(self.values)
        r = requests.post('https://api.coinigy.com/api/v1/addOrder', 
                          data=json.dumps(self.values), 
                          headers=self.headers)
        print(r.text)

    def update(self, message):
        thread = threading.Thread(target=self.trade, args=(message,))
        thread.start()
    
    




