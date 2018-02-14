#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 19:23:23 2017

@author: Paul Herrera
"""
from coinbase.wallet.client import OAuthClient
import requests
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from core.libraries.gdax_auth import Authentication


class GDAX_Handler:
    def __init__(self, auth=None, sandbox=False, *args, **kwargs):
        if sandbox:
            self.url = 'https://api-public.sandbox.gdax.com'
        else:
            self.url = 'https://api.gdax.com'
        self.order_dict = {
            "type": "market",
            "size": "0.01",
            "price": "0.100",
            "side": "buy",
            "product_id": "BTC-USD"
        }

        self.auth = auth

    def get_ticker(self, product_id):
        r = requests.get(self.url + '/products/{}/ticker'.format(product_id))
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            print("Error in response.")

    def list_accounts(self):
        r = requests.get(self.url + '/accounts', auth=self.auth)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            print(r, r.text)
            print("Error in response.")

    def place_order(self, _type='market', size='0.01', side='buy',
                    product_id='BTC-USD', price=None, verbose=True):
        # Creating trade JSON.
        order_dict = {'type': _type, 'size': size, 'side': side, 'product_id': product_id}
        if _type == 'limit':
            order_dict['price'] = price
            assert (order_dict['price'] is not None)

        self.order_dict = order_dict

        # Placing trade.
        r = requests.post(self.url + '/orders', data=json.dumps(order_dict),
                          auth=self.auth)
        if r.status_code == 200:
            if verbose:
                print('\nNew order: {}, {}, {}'.format(product_id, side, size))
            return json.loads(r.text)
        else:
            print("Error in response.")
            return r


if __name__ == '__main__':
    # API keys.
    API_key = 'c2c736241299f78327809504d2ffb0e7'
    passphrase = 'si3b5hm7609'
    secret = 'xzYSvcKvfP8Nx1uS+FxK7yWtoSfJplenN0vv9zGywfQcjTqEfqTmvGWsGixSQHCtkh9JdNoncEU1rEL1MXDWkA=='

    # Instantianting the objects needed.
    auth = Authentication(api_key=API_key, secret_key=secret, passphrase=passphrase)
    gdax = GDAX_Handler(auth=auth)
