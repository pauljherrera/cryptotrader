#!/usr/bin/python3.5
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

    def list_accounts(self):
        return super().list_accounts()  # if auth from gdax api keys


if __name__ == '__main__':
    # API keys.
    API_KEY = ''
    API_PASS = ''
    API_SECRET = ''

    # Creating the objects needed.
    auth = Authentication(api_key=API_KEY, secret_key=API_SECRET, passphrase=API_PASS)
    trader = GDAXTrader(auth=auth)

    print(trader.list_accounts())
