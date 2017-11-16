import numpy as np
import pandas as pd
import datetime as dt
from urllib import request
import threading
import json
import sys
import os
import requests
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from core.libraries.pub_sub import Publisher, Subscriber


class Strategy(Subscriber):

    def __init__(self, *args, **kwargs):

        self.timeframe ={'granularity': kwargs['granularity']}
        self.product = kwargs['pairs']
        self.period = kwargs['ATR-Period']
        self.req = requests.get("https://api.gdax.com//products/{}/candles".format(self.product),params=self.timeframe)
        self.data = json.loads(self.req.text)
        self.headers = ["time", "low", "high", "open", "close", "volume"]
        self.hist_df = pd.DataFrame(self.data, columns=self.headers)
        self.hist_df['time'] = pd.to_datetime(self.hist_df['time'],unit = 's')
        self.hist_df[['low','high','open','close']] = self.hist_df[['low','high','open','close']].apply(pd.to_numeric)
        self.hist_df.set_index('time', drop=True, inplace=True)

        #self.ohlc_df = self.hist_df.resample(self.timeframe).asfreq()[1:]

        #self.queue=[]
        self.ATR()
    def ATR(self):
        self.hist_df['TR1'] = abs (self.hist_df['high'] - self.hist_df['low'])
        self.hist_df['TR2'] = abs (self.hist_df['high'] - self.hist_df['close'].shift())
        self.hist_df['TR3'] = abs (self.hist_df['low'] - self.hist_df['close'].shift())
        self.hist_df['TrueRange'] = self.hist_df[['TR1','TR2','TR3']].max(axis=1)
        self.hist_df['ATR'] = self.hist_df.TrueRange.rolling(self.period).mean()
        del [self.hist_df['TR1'],self.hist_df['TR2'],self.hist_df['TR3']]
        print(self.hist_df)

    def update(self, message):
        #self.queue.append(message)
        print(message)
        time.sleep(1) #just for  testing



#i will add this soon
"""class MACrossover(Strategy):
    def __init__(self, timeframe, long_period, short_period, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.timeframe = str(timeframe) + 'S'
        self.long_period = long_period
        self.short_period = short_period

    def calculate(self, message):
        "
        Sends a dictionary as trading signal.
        "

        # Main logic.
        # Entry signals.
        if (self.accountState == 'CLOSE') and (message['side'] == 'BUY'):
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
"""
