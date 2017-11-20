# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 09:36:39 2017

@author: paulj
"""

import requests
import json
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber
from core.libraries.gdax_api import GDAX_Handler
from core.libraries.gdax_auth import Authentication


class Trader:
    def place_order(self, _type='market', size='0.01', side='buy',
                    product_id='BTC_USD', price=None):
        print('\n{} {} order'.format(product_id, _type))
        print('Type: {}.\nSize: {}.\n'.format(side, size))
        
    def close_last_order(self):
        print('\nLast order closed.\n')



class GDAXTrader(GDAX_Handler, Trader):
    def place_order(self, _type='market', size='0.01', side='buy',
                    product_id='BTC-USD', price=None, verbose=True):
        order = super().place_order(_type=_type, size=size, side=side,
                                    product_id=product_id, price=price,
                                    verbose=verbose)
        self.last_order = order
        
        
    def close_last_order(self):
        # Setting parameters.
        if self.order_dict['side'] == 'buy':
            side = 'sell'
        elif self.order_dict['side'] == 'sell':
            side = 'buy'
        size = self.order_dict['size']
        product_id = self.order_dict['product_id']
    
        # Placing trade.
        order = self.place_order(size=size, side=side, product_id=product_id,
                                 verbose=False)
        self.last_order = order
        
        super().close_last_order()



class CoinigyTrader(Subscriber):
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
    
if __name__ == '__main__':
    # API keys.
    API_key = 'c2c736241299f78327809504d2ffb0e7'
    passphrase = 'si3b5hm7609'
    secret = 'xzYSvcKvfP8Nx1uS+FxK7yWtoSfJplenN0vv9zGywfQcjTqEfqTmvGWsGixSQHCtkh9JdNoncEU1rEL1MXDWkA=='
    
    # Instantianting the objects needed.
    auth = Authentication(api_key=API_key, secret_key=secret, passphrase=passphrase)
    trader = GDAXTrader(auth=auth)




