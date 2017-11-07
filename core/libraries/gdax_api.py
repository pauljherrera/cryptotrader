# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 19:23:23 2017

@author: Paul Herrera
"""

import requests
import json
import pymongo

from dateutil import parser


class GDAX_Handler:
    def __init__(self):
        self.url = 'https://api.gdax.com'
        
    def get_ticker(self, product_id):
        r = requests.get(self.url + '/products/{}/ticker'.format(product_id))
        return json.loads(r.text)


if __name__ == '__main__':
    # Instantianting the objects needed.
    gdax = GDAX_Handler()
    client = pymongo.MongoClient()
    
    # Preparing database.
    db = client['GDAX_data']
    collection = db['API']
    
    # Looping between the coins.
    products = ['BTC-USD', 'LTC-USD']
    
    for p in products:
        ticker = gdax.get_ticker(p)
        keys = list(ticker.keys())
        
        # Storing data into database.
        document = {}
        document['Time'] = parser.parse(ticker['time'])
        document['USD_Value'] = float(ticker['ask']) #Avoided using np.float32 for problems with MongoDB
        document['Currency'] = p.upper()
        collection.insert_one(document)
        
        # Printing the last price for two products and the returned keys.
        print('\nThe most recent price for {} is'.format(p))
        print('Ask: {}'.format(ticker['ask']))
        print('Bid: {}'.format(ticker['bid']))
        print('The keys of the returned Json are: {}'.format(keys))
    
    
        
    
        
    
        
    


