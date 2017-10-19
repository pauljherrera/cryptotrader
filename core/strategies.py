# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:42:36 2017

@author: Paúl Herrera
"""

import numpy as np
import pandas as pd
import datetime as dt
import threading
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber


class Strategy(Subscriber):
    """
    Abstract Base Class for strategies.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.pub = Publisher(events=['signals'])
        self.accountState = 'CLOSE'
        self.ask = [0]
        self.bid = [0]
        self.columns = ['Time', 'Price', 'Type']
        self.data = pd.DataFrame(columns=self.columns).set_index('Time', inplace=True)
    
    def calculate(self, message):
        print('calculate this: {}'.format(message))

    def update(self, message):
#        thread = threading.Thread(target=self.calculate, args=(message,))
#        thread.start()
        self.calculate(message)
        
        
class MACrossover(Strategy):
    def __init__(self, timeframe, long_period, short_period, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.timeframe = str(timeframe) + 'S'
        self.long_period = long_period
        self.short_period = short_period
        
    def calculate(self, message):
        """
        Sends a dictionary as trading signal.
        """
        self.parse(message)
        
        # Main logic.
        # Entry signals.
        if (self.accountState == 'CLOSE') and (message['type'] == 'BUY'):
            self.ask = self.data[self.data.Type == 'BUY'].resample(self.timeframe).last().ffill()            
            long_ma = self.ask.Price.rolling(self.long_period).mean()
            short_ma = self.ask.Price.rolling(self.short_period).mean()
            print('Long MA: {} - Short MA: {}'.format(long_ma[-1], short_ma[-1]))
            if (short_ma[-1] > long_ma[-1]):
                print('Buy signal')
                self.accountState = 'BUY'
                signal = {'type' : message['type'],
                          'price' : message['price']}
                self.pub.dispatch('signals', signal)
                
        # Exit signals.       
        elif (self.accountState == 'BUY') and (message['type'] == 'SELL'):
            self.bid = self.data[self.data.Type == 'SELL'].resample(self.timeframe).last().ffill()
            long_ma = self.bid.Price.rolling(self.long_period).mean()
            short_ma = self.bid.Price.rolling(self.short_period).mean()
            print('Long MA: {} - Short MA: {}'.format(long_ma[-1], short_ma[-1]))
            if (short_ma[-1] < long_ma[-1]):
                print('Close signal')
                self.accountState = 'CLOSE'
                signal = {'type' : message['type'],
                          'price' : message['price']}
                self.pub.dispatch('signals', signal)
        
        
    def parse(self, message):
        time_ = dt.datetime.strptime(message['timestamp'], "%Y-%m-%dT%H:%M:%SZ")\
                       .replace(microsecond=0)
        new_data = [time_, message['price'], message['type']]
        new_df = pd.DataFrame([new_data], columns=self.columns)
        new_df.set_index('Time', inplace=True)
        self.data = pd.concat([self.data, new_df])
        
        
        
