# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 19:23:23 2017

@author: Paul Herrera
"""

import requests
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from core.libraries.gdax_auth import Authentication


class GDAX_Handler:
    def __init__(self, auth=None, *args, **kwargs):
        self.url = 'https://api.gdax.com'
        self.order_dict = {
            "type": "market",
            "size": "0.01",
            "price": "0.100",
            "side": "buy",
            "product_id": "BTC-USD"
        }
        
    def get_ticker(self, product_id):
        r = requests.get(self.url + '/products/{}/ticker'.format(product_id))
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            print("Error in response.")
    
    def list_accounts(self):
        r = requests.get(self.url + '/accounts', auth=auth)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            print("Error in response.")
    
    def place_order(self, _type='market', size='0.01', side='buy',
                    product_id='BTC_USD', price=None):
        # Creating trade JSON.
        order_dict = {}
        order_dict['type'] = _type
        order_dict['size'] = size
        order_dict['side'] = side
        order_dict['product_id'] = product_id
        if _type == 'limit':
            order_dict['price'] = price
            assert(order_dict['price'] != None)
        
        self.order_dict = order_dict
        
        # Placing trade.
        r = requests.post(self.url + '/orders', json=order_dict, auth=auth)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            print("Error in response.")


if __name__ == '__main__':
    # API keys.
    API_key = 'c2c736241299f78327809504d2ffb0e7'
    passphrase = 'si3b5hm7609'
    secret = 'xzYSvcKvfP8Nx1uS+FxK7yWtoSfJplenN0vv9zGywfQcjTqEfqTmvGWsGixSQHCtkh9JdNoncEU1rEL1MXDWkA=='
    
    # Instantianting the objects needed.
    auth = Authentication(api_key=API_key, secret_key=secret, passphrase=passphrase)
    gdax = GDAX_Handler(auth=auth)

    
    
        
    
        
    
        
    


