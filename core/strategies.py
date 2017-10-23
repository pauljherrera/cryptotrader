# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:42:36 2017

@author: Paúl Herrera
"""

import numpy as np
import pandas as pd
import datetime as dt
from urllib import request
import threading
import json
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber


class Strategy(Subscriber):
    """
    Abstract Base Class for strategies.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.headers = kwargs['headers']
        self.values = kwargs['values']
        self.timef = kwargs['timef']

        self.pub = Publisher(events=['signals'])
        self.accountState = 'CLOSE'
        self.ask = [0]
        self.bid = [0]
        self.columns = ['Time', 'Price', 'Type']
        self.data = pd.DataFrame(columns=self.columns).set_index('Time', inplace=True)
        self.req = requests.post('https://api.coinigy.com/api/v1/data', data=json.dumps(self.values), headers=self.headers)
        self.hist_df = pd.DataFrame(json.loads(self.req.text)['data']['history'])
        self.hist_df = self.hist_df.loc[(self.hist_df['type']=='SELL')]
        self.hist_df['time_local'] = pd.to_datetime(self.hist_df['time_local'],format="%Y-%m-%dT%H:%M:%S")
        self.hist_df.set_index('time_local', drop=True, inplace=True)
        self.sample = self.hist_df.resample(self.timef).first().ffill()

        print(self.sample)

    def calculate(self, message):
        print('calculate this: {}'.format(message))

    def update(self, message):
#        thread = threading.Thread(target=self.calculate, args=(message,))
#        thread.start()
        self.calculate(message)

    def live(self,message):

        live_data = [message['time_local'], '{:.10f}'.format(message['price']) , '{:.10f}'.format(message['quantity']), message['type']]
        columns_n = ['time_local', 'price', 'quantity', 'type']
        live_df = pd.DataFrame([live_data], columns=columns_n)
        live_df['time_local'] = pd.to_datetime(live_df['time_local'], format="%Y-%m-%dT%H:%M:%S")
        live_df.set_index('time_local', drop=True, inplace=True)

        self.hist_df = pd.concat([live_df, self.hist_df])

        print(self.hist_df.resample(self.timef).first().ffill())



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
        if message['type'] == 'SELL':
            super().live(message)

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
